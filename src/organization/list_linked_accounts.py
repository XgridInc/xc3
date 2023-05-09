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
    org_client = boto3.client("organizations")
    ssm_client = boto3.client("ssm")
except Exception as e:
    logging.error("Error creating boto3 client: " + str(e))


def lambda_handler(event, context):
    """
    Put list of all member accounts linked with mast AWS Account in SSM Parameter.

    Args:
        account_detail: A name of SSM parameter.

    Returns:
        A list of member accounts linked with master AWS Account
    Raises:
        KeyError: If the account id is incorrect.
        ValueError: If there is a problem in calling organization
        apis or creating ssm parameter.
    """
    # Initliazing list for account details
    linked_accounts = []
    account_details = []

    # Retrieve all accounts under the specified master account
    try:
        paginator = org_client.get_paginator("list_accounts")
        response_iterator = paginator.paginate()
    except Exception as e:
        raise ValueError(
            f"An error occurred in calling api: {e}.\nPlease check the network connectivity and try again."
        )
    linked_accounts = [
        account for page in response_iterator for account in page["Accounts"]
    ]
    account_details = [
        account["Id"] + "-" + account["Name"] for account in linked_accounts
    ]
    try:
        result = ssm_client.put_parameter(
            Name="/" + os.environ["account_detail"] + "/account_details",
            Value=json.dumps(account_details),
            Type="StringList",
            Overwrite=True,
        )
        logging.info(result)
    except Exception as e:
        raise ValueError(f"Failed to put value in ssm parameter: {str(e)}")

    return {"statusCode": 200, "body": json.dumps(account_details)}
