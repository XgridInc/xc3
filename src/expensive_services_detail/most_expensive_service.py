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

import ast
import json
import logging
import os

import boto3

# Initialize and Connect to the AWS EC2 Service
try:
    client_ssm = boto3.client("ssm")
    lambda_client = boto3.client("lambda")
except Exception as e:
    logging.error("Error creating boto3 client: " + str(e))


def lambda_handler(event, context):

    """
    List 5 top most expensive services in provided aws region.

    Args:
        Account ID: AWS account id.
    Returns:
        It pushes the 5 most expensive services name and cost with AWS region to Prometheus using push gateway.
    Raises:
        KeyError: Raise error if cost explorer API call does not execute.
    """
    parameter_name = "/" + os.environ["account_detail"] + "/account_details"
    expensive_service_lambda = os.environ["lambda_function_name"]
    try:
        response = client_ssm.get_parameter(Name=parameter_name, WithDecryption=True)
        parameter_value = response["Parameter"]["Value"]
        # Converting SSM ListString to List
        account_details = ast.literal_eval(parameter_value)
    except ValueError as ve:
        raise ValueError(
            f"ValueError occurred: {ve}. Please check the input data format and try again."
        )
    except Exception as e:
        raise ValueError(
            f"An error occurred: {e}. Please check the input data and try again."
        )

    # Loop through each region
    for account_detail in account_details:
        account_id = account_detail.split("-")[0]
        # Check that the account ID has 12 digits
        if len(account_id) != 12 or not account_id.isdigit():
            raise ValueError("Invalid AWS account ID")

        payload = {"account_id": account_id, "account_detail": account_detail}
        try:
            expensive_lambda_response = lambda_client.invoke(
                FunctionName=expensive_service_lambda,
                InvocationType="Event",
                Payload=json.dumps(payload),
            )
            # Extract the status code from the response
            status_code = expensive_lambda_response["StatusCode"]
            if status_code != 202:
                # Handle unexpected status code
                logging.error(
                    f"Unexpected status code {status_code} returned from expensive_service_lambda"
                )
        except Exception as e:
            logging.error("Error in invoking lambda function: " + str(e))
            return {
                "statusCode": 500,
                "body": "Error invoking expensive_service_lambda",
            }

    return {
        "statusCode": 200,
        "body": "Invocation of expensive_service_lambda successful",
    }
