import json
import logging
import os

import boto3

region_names = {
    "us-east-1": "N. Virginia",
    "us-east-2": "Ohio",
    "us-west-1": "N. California",
    "us-west-2": "Oregon",
    "af-south-1": "Cape Town",
    "ap-east-1": "Hong Kong",
    "ap-south-1": "Mumbai",
    "ap-northeast-2": "Seoul",
    "ap-southeast-1": "Singapore",
    "ap-southeast-2": "Sydney",
    "ap-northeast-1": "Tokyo",
    "ap-northeast-3": "Osaka",
    "ca-central-1": "Canada",
    "eu-central-1": "Frankfurt",
    "eu-west-1": "Ireland",
    "eu-west-2": "London",
    "eu-south-1": "Milan",
    "eu-west-3": "Paris",
    "eu-north-1": "Stockholm",
    "me-south-1": "Bahrain",
    "sa-east-1": "São Paulo"
}

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
