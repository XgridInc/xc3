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

import gzip
import io
import json
import logging
import os
from urllib.parse import unquote_plus

import boto3
from prometheus_client import CollectorRegistry, Gauge, push_to_gateway

try:
    s3 = boto3.client("s3")
except Exception as e:
    logging.error("Error creating boto3 client: " + str(e))
try:
    lambda_client = boto3.client("lambda")
except Exception as e:
    logging.error("Error creating boto3 client: " + str(e))

try:
    ssm_client = boto3.client("ssm")
except Exception as e:
    logging.error("Error creating boto3 client for ssm:" + str(e))
    
def get_region_names():
    """
    Retrieves the region names dictionary from AWS Systems Manager Parameter Store.

    Returns:
    - dict: The region names dictionary.
    """
    region_path = os.environ["region_names_path"]
    
    try:
        response = ssm_client.get_parameter(Name=region_path)
        region_names = json.loads(response["Parameter"]["Value"])
        return region_names
    except Exception as e:
        logging.error("Error retrieving region names from Parameter Store: " + str(e))
        raise

# Get the region names dictionary
region_names = get_region_names()

def lambda_handler(event, context):
    """
    Lambda handler function that extracts IAM role information
    and pushes it to Prometheus.

    Parameters:
    - event (dict): The event payload containing the list
    of roles.
    - context (object): The context object that provides information
    about the runtime environment.

    Returns:
    - dict: The response with a status code of 200 and
    a message body of "IAM Roles".
    """

    list_of_iam_roles = []
    bucket = event["Records"][0]["s3"]["bucket"]["name"]
    key = unquote_plus(event["Records"][0]["s3"]["object"]["key"])
    if "resources" in key:
        try:
            response = s3.get_object(Bucket=bucket, Key=key)
            resource_file = response["Body"].read()
            with gzip.GzipFile(fileobj=io.BytesIO(resource_file), mode="rb") as data:
                list_of_iam_roles = json.load(data)
        except Exception as e:
            logging.error(
                "Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.".format(
                    key, bucket
                )
            )
            return {"statusCode": 500, "body": json.dumps({"Error": str(e)})}
    logging.info(list_of_iam_roles)

    account_id = context.invoked_function_arn.split(":")[4]

    registry = CollectorRegistry()
    iam_role_all_gauge = Gauge(
        "IAM_Role_All",
        "XC3 All IAM Roles",
        labelnames=["iam_role_all", "iam_role_all_region", "iam_role_all_account"],
        registry=registry,
    )

    functionName = os.environ["func_name_iam_role_service_mapping"]
    try:
        iam_role_service_lambda_payload = lambda_client.invoke(
            FunctionName=functionName,
            InvocationType="Event",
            Payload=json.dumps(list_of_iam_roles),
        )
        # Extract the status code from the response
        status_code = iam_role_service_lambda_payload["StatusCode"]
        if status_code != 202:
            # Handle unexpected status code
            logging.error(
                f"Unexpected status code {status_code} returned from iam_role_service_lambda"
            )
    except Exception as e:
        logging.error("Error in invoking lambda function: " + str(e))
        return {"statusCode": 500, "body": "Error invoking iam_role_service_lambda"}

    for role in list_of_iam_roles:
        role_name = role["RoleName"]
        region = role["RoleLastUsed"].get("Region", "None")
        region = f"{region} ({region_names.get(region, 'unknown region name')})"
        iam_role_all_gauge.labels(role_name, region, account_id).set(0)

    push_to_gateway(os.environ["prometheus_ip"], job="IAM-roles-all", registry=registry)
    return {"statusCode": 200, "body": json.dumps(list_of_iam_roles)}
