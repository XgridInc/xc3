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
import logging
import os

import boto3

try:
    ec2_client = boto3.client("ec2")
    lambda_client = boto3.client("lambda")
except Exception as e:
    logging.error("Error creating boto3 client: " + str(e))
try:
    regions = {
        region["RegionName"] for region in ec2_client.describe_regions()["Regions"]
    }
except Exception as e:
    logging.error("Error describing ec2 regions: " + str(e))

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
    Fetch a list resources in all AWS Region.

    Returns:
        dict: The list of resources in a specific AWS Region.
    """

    resource_analysis_lambda = os.environ["resource_list_lambda_function"]
    # Initializing the dictionary for resources
    case_list = []

    # Initializing resource list
    resources = []
    for region_name in regions:
        try:
            client_resource = boto3.client(
                "resourcegroupstaggingapi", region_name=region_name
            )
        except Exception as e:
            logging.error("Error initializing resourcegroupstaggingapi api: " + str(e))
            return {"statusCode": 500, "body": json.dumps({"Error": str(e)})}

        try:
            response = client_resource.get_resources()
        except Exception as e:
            logging.error("Error in calling get_resource api: " + str(e))
            return {"statusCode": 500, "body": json.dumps({"Error": str(e)})}

        resources = response["ResourceTagMappingList"]

        dict_len = len(resources)
        if dict_len == 0:
            continue
        else:
            # Get the region name from the region code
            region_display_name = f"{region_name} ({region_names.get(region_name, 'Unknown')})"
            result_list = {"Region": region_display_name, "ResourceList": resources}
            case_list.append(result_list)
    try:
        cost_lambda_response = lambda_client.invoke(
            FunctionName=resource_analysis_lambda,
            InvocationType="Event",
            Payload=json.dumps(case_list),
        )
        # Extract the status code from the response
        status_code = cost_lambda_response["StatusCode"]
        if status_code != 202:
            # Handle unexpected status code
            logging.error(
                f"Unexpected status code {status_code} returned from resource_analysis_lambda"
            )
    except Exception as e:
        logging.error("Error in invoking lambda function: " + str(e))
        return {
            "statusCode": 500,
            "body": "Error invoking resource_analysis_lambda",
        }

    return {
        "statusCode": 200,
        "body": "Invocation of resource_analysis_lambda successful",
    }
