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

import json
import boto3
import logging
import os
from prometheus_client import CollectorRegistry, Gauge, push_to_gateway
from datetime import date, datetime, timedelta
import botocore

case_list = []
regionName = os.environ["AWS_REGION"]
try:
    client = boto3.client("ce")
    s3 = boto3.client("s3")
except Exception as e:
    logging.error("Error creating boto3 client: " + str(e))
try:
    ssm_client = boto3.client("ssm")
except Exception as e:
    logging.error("Error creating boto3 client for ssm:" + str(e))


def cost_of_instance(event, client, resource_id):
    """
    Return cost of resource from last 14 days

    Args:
        Resource ID: Resource ID.
        Client: Cost Explorer boto3 client
    Returns:
        It return cost of resource from last 14 days
    Raises:
        KeyError: Error if Cost Explorer API call doesn't execute.
    """
    cost_by_days = 14
    end_date = str(date.today())
    start_date = str(date.today() - timedelta(days=cost_by_days))
    ce_response = client.get_cost_and_usage_with_resources(
        TimePeriod={"Start": start_date, "End": end_date},
        Granularity="DAILY",
        Filter={
            "Dimensions": {
                "Key": "RESOURCE_ID",
                "Values": [resource_id],
            }
        },
        Metrics=["UnblendedCost"],
    )
    total_amount = sum(float(item["Total"]["UnblendedCost"]["Amount"]) for item in ce_response["ResultsByTime"])
    return total_amount


def lambda_handler(event, context):
    """
    List resources under ownership of specific IAM User.
    Args:
        IAM Users List: IAM Users.
    Returns:
        It return list of resources under ownership of specific IAM user in aws .
    Raises:
        KeyError: Raise error if cost explorer api  call not execute."""
   
    try:
        current_date = datetime.now()
        year = str(current_date.year)
        month = current_date.strftime('%m')
        day = current_date.strftime('%d')
        bucket_name = os.environ['bucket_name']
        
        # Set the destination key
        destination_key = f"fed-resources/{year}/{month}/{day}/duplicated.json"
    
        data = s3.get_object(Bucket=event["Records"][0]["s3"]["bucket"]["name"], Key=event["Records"][0]["s3"]["object"]["key"])
        file_content = json.loads(data['Body'].read().decode('utf-8'))
        ec2_instances = []
        
        registry = CollectorRegistry()
#         # Creating gauge metrics for resource's cost for specific IAM User
        gauge = Gauge(
            "FED_USER_Resource_Cost_List",
            "FED USER Resource List And Cost",
            labelnames=[
                "resource_id",
                "resource",
                "cost",
                "account_id",
                'region'
            ],
            registry=registry,
        )
        
        for account_id, resources in file_content['body'].items():
            account = account_id
            for resource in resources:
                if resource['Compliance']:
                    resource_id = resource['ResourceARN']
                    resource_type = resource_id.split(':')[2]
                    if resource['ResourceARN'].startswith('arn:aws:s3'):
                        region = ''
                    else:
                        region = resource_id.split(':')[3]
                    cost = cost_of_instance(event, client, resource_id)
                    ec2_instances.append({'resource_id': resource_id, 'cost': cost, 'region': region, 'resource': resource_type, 'account_id': account})
                    gauge.labels(
                        resource_id, resource, cost, account_id, region
                    ).set(cost)
                    push_to_gateway(
                    os.environ["prometheus_ip"],
                        job="FED_USER_Resource_Cost_List",
                        registry=registry,
                    )
                    
                # elif resource['ResourceARN'].startswith('arn:aws:lambda'):
                    
        s3.put_object(Bucket=bucket_name, Key=destination_key, Body=json.dumps({'ec2':ec2_instances}))
    except Exception as f:
        s3.put_object(Bucket=bucket_name, Key=destination_key, Body=json.dumps({'data': str(f)}))
    except botocore.exceptions.ClientError as e:
        if e.response["Error"]["Code"] == "NoSuchBucket":
            raise ValueError(f"Bucket not found: {os.environ['bucket_name']}")
        elif e.response["Error"]["Code"] == "AccessDenied":
            raise ValueError(
                f"Access denied to S3 bucket: {os.environ['bucket_name']}"
            )
        else:
            raise ValueError(f"Failed to upload data to S3 bucket: {str(e)}")
    return {"statusCode": 200}