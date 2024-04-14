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

import io
import gzip
import json
import boto3
import botocore
import os
import logging
from prometheus_client import CollectorRegistry, Gauge, push_to_gateway
from urllib.parse import unquote_plus
from datetime import datetime

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

def verify_tags(tags):
    required_tags = ['Owner','Creator', 'Project']
    if all(tag in tags for tag in required_tags):
        return True
    else:
        return False

def get_resources_for_account_id(account_id):
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
                
                resources.append({'ResourceARN': resource_arn, 'Tags': tags, 'Compliance': verify_tags(tags)})
                
    except Exception as e:
        print(f"Error retrieving resources: {str(e)}")
    
    return resources

def lambda_handler(event, context):
    """
    List IAM User Details.
    Args:
        Account ID: AWS account id.
    Returns:
        It returns a list of IAM Users details in provided aws account.
    Raises:
        Lambda Invoke Error: Raise error if message doesn't publish in SNS topic
    """

    # Initialize IAM client
    iam = boto3.client('iam')
    sts_client = boto3.client('sts')
    
    # Call list_users method
    
    # response = iam.list_groups()
    
    # Extract user information from the response
    # users = response['Users']
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
    
    # Convert the set of account IDs to a list
    accounts = list(account_ids)
    
    # Return the formatted user information
    all_resources = {}
    for account_id in account_ids:
        resources = get_resources_for_account_id(account_id)
        all_resources.update({account_id:resources})
        
    
    # # Define the parameters for invoking untagged resource lambda
    # invoke_params = {
    #     'FunctionName': untagged_resource_lambda_arn, 
    #     'InvocationType': 'Event'  # Asynchronous invocation
    # }

    current_date = datetime.now()
    year = str(current_date.year)
    month = current_date.strftime('%m')
    day = current_date.strftime('%d')

    # Set the destination key
    # bucket = event["Records"][0]["s3"]["bucket"]["name"]
    destination_key = f"fed-resources/{year}/{month}/{day}/resources.json"
    try:
        s3.put_object(Bucket=bucket_name, Key=destination_key, Body=json.dumps({'body':all_resources}))
        # Invoke untagged resource
        # response = lambda_client.invoke(**invoke_params)
        # Invoke another Lambda function with the untagged resources as payload
        invoke_response = lambda_client.invoke(
            FunctionName=untagged_resource_lambda_arn,
            InvocationType='RequestResponse',
            Payload=json.dumps({"accId": accounts})
        )
        # Check the response from untagged resource
        if response['StatusCode'] == 202:
            print("Untagged Resource invoked successfully")
            print(response)
        else:
            print("Error invoking Untagged resource")
    except botocore.exceptions.ClientError as e:
        if e.response["Error"]["Code"] == "NoSuchBucket":
            raise ValueError(f"Bucket not found: {os.environ['bucket_name']}")
        elif e.response["Error"]["Code"] == "AccessDenied":
            raise ValueError(
                f"Access denied to S3 bucket: {os.environ['bucket_name']}"
            )
        else:
            raise ValueError(f"Failed to upload data to S3 bucket: {str(e)}")
    
    return {
        'statusCode': 200,
        'body': all_resources
    }
   