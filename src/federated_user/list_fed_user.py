# Copyright (c) 2023, Xgrid Inc, https://xgrid.co

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#        http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import re
import io
import gzip
import json
import boto3
import botocore
import os
import logging
from prometheus_client import CollectorRegistry, Gauge, push_to_gateway
from urllib.parse import unquote_plus
from datetime import datetime, timedelta
import time

#Needed to invoke Untagged Resource Lambda
untagged_resource_lambda_arn = os.environ['UNTAGGED_RESOURCE_LAMBDA_ARN']
lambda_client = boto3.client('lambda')
try:
    s3 = boto3.client("s3")
    bucket_name = os.environ["bucket_name"]
except Exception as e:
    logging.error("Error creating boto3 client: " + str(e))
try:
    sns = boto3.client("sns")
except Exception as e:
    logging.error("Error creating boto3 client: " + str(e))

# Initializing environment variables
runtime_region = 'ap-southeast-2' #os.environ["REGION"]
# topic_arn = os.environ["sns_topic"]

def lookup_events(next_token=None, attribute=None):
    cloud_trail_client = boto3.client('cloudtrail')
    # log = []
    if next_token:
        response = cloud_trail_client.lookup_events(
            LookupAttributes=[
                {
                    'AttributeKey': 'EventName',
                    'AttributeValue': attribute
                },
            ],
            StartTime=datetime.now() - timedelta(days=1),
            EndTime=datetime.now(),
            NextToken=next_token
        )
    else:
        response = cloud_trail_client.lookup_events(
            LookupAttributes=[
                {
                    'AttributeKey': 'EventName',
                    'AttributeValue': attribute
                },
            ],
            StartTime=datetime.now() - timedelta(days=1),
            EndTime=datetime.now()
        )
    
    return response 

    
    # for event in lookupevents:
    
def verify_tags(tags):
    required_tags = ['Owner','Creator', 'Project']
    if all(tag in tags for tag in required_tags):
        return True
    else:
        return False

def get_resources_with_tags():
    # Initialize the Resource Groups Tagging API client
    client = boto3.client('resourcegroupstaggingapi')
    
    # Retrieve resources with the specified account ID
    paginator = client.get_paginator('get_resources')
    resources = []
    
    try:
        # Paginate through the list of resources
        for page in paginator.paginate(ResourceTypeFilters=['s3', 'lambda', 'ec2:instance']):
            for resource in page.get('ResourceTagMappingList', []):
                resource_arn = resource['ResourceARN']
                tags = {tag['Key']: tag['Value'] for tag in resource.get('Tags', [])}
                if tags:
                    resources.append({'ResourceARN': resource_arn, 'Tags': tags, 'Compliance': verify_tags(tags)})
                else:
                    resources.append({'ResourceARN': resource_arn, 'Tags': tags})
        
    except Exception as e:
        print(f"Error retrieving resources: {str(e)}")
    
    return resources

def lambda_handler(event, context):
    # Initialize IAM client
    iam = boto3.client('iam')
    response = iam.list_roles()
    account_ids = set()
    # Process the response
    for role in response.get('Roles', []):
        assume_role_policy_document = role.get('AssumeRolePolicyDocument', {})
        principal = assume_role_policy_document.get('Statement', [{}])[0].get('Principal', {})
        federated_value = principal.get('Federated')
        if federated_value:
            # Extract the account ID from the federated ARN
            account_id = federated_value.split(':')[4]
            account_ids.add(account_id)
    accounts = list(account_ids)
    usernames = []
    response = iam.list_users()
    for account in account_ids:
        for user in response.get('Users'):
            if account in user.get('Arn').split(":")[4]:
                usernames.append(user.get('UserName'))
    resources_from_trail = []
    attributes = ['RunInstances', 'CreateFunction20150331', 'CreateBucket']
    for attribute in attributes:
        response = lookup_events(attribute=attribute)
        for event in response['Events']:
            for x in event['Resources']:
                if attribute == 'RunInstances' and x['ResourceType'] != 'AWS::EC2::Instance':
                    continue
                resources_from_trail.append({event['Username']:x['ResourceName']})
        while 'NextToken' in response:
            response = lookup_events(next_token=response.get('NextToken'), attribute=attribute)
            for event in response['Events']:
                for x in event['Resources']:
                    resources_from_trail.append({event['Username']:x['ResourceName']})
                    
    resources_by_user = {}

    for entry in resources_from_trail:
        for username, resource in entry.items():
            if username not in resources_by_user:
                resources_by_user[username] = set()
            resources_by_user[username].add(resource)
            
    tagging_resource = get_resources_with_tags()
    
    # Initialize combined dictionary
    combined_resources = {}
    
    # Iterate over resources from trail
    for username, resources in resources_by_user.items():
        combined_resources[username] = {'compliant': [], 'non-compliant': [], 'untagged': []}
        for x in resources:
            flag = False
            for data in tagging_resource:
                if 'Compliance' not in data:
                    continue
                if x in data['ResourceARN'] and data.get('Compliance'):
                    combined_resources[username]['compliant'].append({x:data['ResourceARN']})
                    flag=True
                elif x in data['ResourceARN'] and not data.get('Compliance'):
                    combined_resources[username]['non-compliant'].append({x:data['ResourceARN']})
                    flag=True
            if not flag:
                combined_resources[username]['untagged'].append(x)
    
    # print(combined_resources)

    current_date = datetime.now()
    year = str(current_date.year)
    month = current_date.strftime('%m')
    day = current_date.strftime('%d')

    # Set the destination key
    destination_key = f"fed-resources/{year}/{month}/{day}/resources.json"
    try:
        s3.put_object(Bucket=bucket_name, Key=destination_key, Body=json.dumps({'body':combined_resources}))

        invoke_response = lambda_client.invoke(
            FunctionName=untagged_resource_lambda_arn,
            InvocationType='Event'
        )
    except botocore.exceptions.ClientError as e:
        if e.response["Error"]["Code"] == "NoSuchBucket":
            raise ValueError(f"Bucket not found: {os.environ['bucket_name']}")
        elif e.response["Error"]["Code"] == "AccessDenied":
            raise ValueError(
                f"Access denied to S3 bucket: {os.environ['bucket_name']}"
            )
        else:
            raise ValueError(f"Failed to upload data to S3 bucket: {str(e)}")
    # print(resources_from_trail) 
    # print(resources_by_user)
    return {
        'statusCode': 200,
    }