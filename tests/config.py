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

import boto3
import json
import os
from dotenv import load_dotenv

load_dotenv()


def get_state_file(bucket_name, object_key):
    """
    Get the state file from an S3 bucket.

    This function takes the name of an S3 bucket and the key of
    the object that contains the state file. The state file is expected
    to be in JSON format.

    If the object is retrieved successfully and its contents can be decoded
    as a non-empty JSON string, the function parses the string and
    returns the resulting Python object along with a string indicating
    that the state file was retrieved successfully. If the JSON string
    is empty, the function returns None along with a message indicating
    that the file was empty.

    If the object cannot be retrieved for any reason, the function returns
    None along with a message indicating the reason.

    Args:
        bucket_name (str): The name of the S3 bucket.
        object_key (str): The key of the object that contains the state file.

    Returns:
        tuple: A tuple containing the contents of the state file as a dictionary,
        and a message indicating the success or failure of the operation.
        If the file could not be retrieved, returns None and a message indicating
        the reason for the failure.
    """
    s3 = boto3.client("s3")
    try:
        response = s3.get_object(Bucket=bucket_name, Key=object_key)
        state_file = response["Body"].read().decode("utf-8")
        if state_file:
            json_data = json.loads(state_file)
            return json_data
        else:
            return None, "state file is empty"
    except Exception as e:
        return None, f"failed to retrieve state file: {e}"


# Name of the bucket
bucket_name = os.environ.get("BUCKET_NAME")

# Key for the state file
object_key = os.environ.get("OBJECT_KEY")
state_file_json = get_state_file(bucket_name, object_key)


# Region

region = None
for data_item in state_file_json["resources"]:
    if data_item["type"] == "aws_s3_bucket" and data_item["name"] == "this":
        region = data_item["instances"][0]["attributes"]["region"]
        break


# Getting S3 bucket arn

s3_bucket_arn = None
for data_item in state_file_json["resources"]:
    if data_item["type"] == "aws_s3_bucket" and data_item["name"] == "this":
        s3_bucket_arn = data_item["instances"][0]["attributes"]["arn"]
        break

# Getting tags attached to s3 bucket

s3_bucket_tags = None
for data_item in state_file_json["resources"]:
    if data_item["type"] == "aws_s3_bucket" and data_item["name"] == "this":
        s3_bucket_tags = data_item["instances"][0]["attributes"]["tags"]
        break

# Getting Cloud trail arn

cloudtrail_arn = None
for data_item in state_file_json["resources"]:
    if data_item["type"] == "aws_cloudtrail" and data_item["name"] == "this":
        cloudtrail_arn = data_item["instances"][0]["attributes"]["arn"]
        break

# Getting Cloud Watch arn for most expensive services arn

cloudwatch_most_expensive_arn = None
for data_item in state_file_json["resources"]:
    if (
        data_item["type"] == "aws_cloudwatch_event_rule"
        and data_item["name"] == "most_expensive_service"
    ):
        cloudwatch_most_expensive_arn = data_item["instances"][0]["attributes"]["arn"]
        cloudwatch_most_expensive_name = cloudwatch_most_expensive_arn.split("/")[-1]
        break

# Getting Cloud Watch arn for project spend arn

cloudwatch_project_spend_arn = None

for data_item in state_file_json["resources"]:
    if (
        data_item["type"] == "aws_cloudwatch_event_rule"
        and data_item["name"] == "project_spend_cost"
    ):
        cloudwatch_project_spend_arn = data_item["instances"][0]["attributes"]["arn"]
        cloudwatch_project_spend_name = cloudwatch_project_spend_arn.split("/")[-1]
        break

# Getting Cloud Watch arn for resource list arn

cloudwatch_resource_list_arn = None

for data_item in state_file_json["resources"]:
    if (
        data_item["type"] == "aws_cloudwatch_event_rule"
        and data_item["name"] == "resource_list"
    ):
        cloudwatch_resource_list_arn = data_item["instances"][0]["attributes"]["arn"]
        cloudwatch_resource_list_name = cloudwatch_resource_list_arn.split("/")[-1]
        break

# Getting Cloud Watch arn for total account cost arn

cloudwatch_total_account_cost_arn = None

for data_item in state_file_json["resources"]:
    if (
        data_item["type"] == "aws_cloudwatch_event_rule"
        and data_item["name"] == "total_account_cost"
    ):
        cloudwatch_total_account_cost_arn = data_item["instances"][0]["attributes"][
            "arn"
        ]
        cloudwatch_total_account_cost_name = cloudwatch_total_account_cost_arn.split(
            "/"
        )[-1]
        break

# Getting Cloud Watch arn for linked list arn

cloudwatch_linked_list_arn = None

for data_item in state_file_json["resources"]:
    if (
        data_item["type"] == "aws_cloudwatch_event_rule"
        and data_item["name"] == "list_linked_accounts"
    ):
        cloudwatch_linked_list_arn = data_item["instances"][0]["attributes"]["arn"]
        cloudwatch_linked_list_name = cloudwatch_linked_list_arn.split("/")[-1]
        break


# Getting Cloud Watch for cost report notifier

cloudwatch_cost_report_notifier_name = None

for data_item in state_file_json["resources"]:
    if (
        data_item["type"] == "aws_cloudwatch_event_rule"
        and data_item["name"] == "cost_report_notifier"
    ):
        cloudwatch_cost_report_notifier_arn = data_item["instances"][0]["attributes"][
            "arn"
        ]
        cloudwatch_cost_report_notifier_name = (
            cloudwatch_cost_report_notifier_arn.split("/")[-1]
        )
        break

# Getting Cognito ID

cognito_id = None

for data_item in state_file_json["resources"]:
    if (
        data_item["type"] == "aws_cognito_user_pool"
        and data_item["name"] == "grafana_pool"
    ):
        cognito_id_arn = data_item["instances"][0]["attributes"]["arn"]
        cognito_id = cognito_id_arn.split("/")[-1]
        break

# Getting IAM Role

iam_role_name = None

for data_item in state_file_json["resources"]:
    if data_item["type"] == "aws_iam_role" and data_item["name"] == "this":
        iam_role = data_item["instances"][0]["attributes"]["arn"]
        iam_role_name = iam_role.split("/")[-1]
        break

# Getting Load Balancer name

loadbalancer_name = None

for data_item in state_file_json["resources"]:
    if data_item["type"] == "aws_lb" and data_item["name"] == "this":
        lb = data_item["instances"][0]["attributes"]["name"]
        break

# Getting KMS Name

kms_name = None

for data_item in state_file_json["resources"]:
    if data_item["type"] == "aws_kms_alias" and data_item["name"] == "this":
        kms = data_item["instances"][0]["attributes"]["arn"]
        kms_name = kms.split("/")[-1]
        break

# Getting SNS Name

sns_name = None

for data_item in state_file_json["resources"]:
    if data_item["type"] == "aws_sns_topic" and data_item["name"] == "this":
        sns = data_item["instances"][0]["attributes"]["arn"]
        sns_name = sns.split(":")[-1]
        break

# Getting SNS ARN

sns_arn = None

for data_item in state_file_json["resources"]:
    if (
        data_item["type"] == "aws_sns_topic_subscription"
        and data_item["name"] == "invoke_with_sns"
    ):
        sns_arn = data_item["instances"][0]["attributes"]["arn"]
        break

# Getting SQS ARN

sqs_name = None

for data_item in state_file_json["resources"]:
    if data_item["type"] == "aws_sqs_queue" and data_item["name"] == "this":
        sqs = data_item["instances"][0]["attributes"]["arn"]
        sqs_name = sqs.split(":")[-1]
        break

# Getting SES ARN

ses_name = None

for data_item in state_file_json["resources"]:
    if data_item["type"] == "aws_ses_email_identity" and data_item["name"] == "this":
        ses = data_item["instances"][0]["attributes"]["arn"]
        ses_name = ses.split("/")[-1]
        break

# Getting VPC ID

vpc = None

for data_item in state_file_json["resources"]:
    if data_item["type"] == "aws_vpc" and data_item["name"] == "this":
        vpc = data_item["instances"][0]["attributes"]["tags"]["Name"]
        break

# Getting VPC CIDR

vpc_cidr = None

for data_item in state_file_json["resources"]:
    if data_item["type"] == "aws_vpc" and data_item["name"] == "this":
        vpc_cidr = data_item["instances"][0]["attributes"]["cidr_block"]
        break

# Getting Subnets for VPC

subnetid1 = None

for data_item in state_file_json["resources"]:
    if data_item["type"] == "aws_instance" and data_item["name"] == "this":
        subnetid1 = data_item["instances"][0]["attributes"]["subnet_id"]
        break

subnetid2 = None

for data_item in state_file_json["resources"]:
    if (
        data_item["type"] == "aws_route_table_association"
        and data_item["name"] == "this"
    ):
        subnetid2 = data_item["instances"][1]["attributes"]["subnet_id"]
        break

subnetid3 = None

for data_item in state_file_json["resources"]:
    if (
        data_item["type"] == "aws_route_table_association"
        and data_item["name"] == "this"
    ):
        subnetid3 = data_item["instances"][0]["attributes"]["subnet_id"]
        break

# Getting Route Table Name

routetable = None

for data_item in state_file_json["resources"]:
    if data_item["type"] == "aws_vpc" and data_item["name"] == "this":
        routetable = data_item["instances"][0]["attributes"]["default_route_table_id"]

# Getting NAT Gateway Name

natgatewayname = None

for data_item in state_file_json["resources"]:
    if data_item["type"] == "aws_nat_gateway" and data_item["name"] == "this":
        natgatewayname = data_item["instances"][0]["attributes"]["tags"]["Name"]

# Getting NAT Gateway ID

natgatewayid = None

for data_item in state_file_json["resources"]:
    if data_item["type"] == "aws_nat_gateway" and data_item["name"] == "this":
        natgatewayid = data_item["instances"][0]["attributes"]["allocation_id"]

# Getting NAT Gateway Subnet ID

natgatewaysubnetid = None

for data_item in state_file_json["resources"]:
    if data_item["type"] == "aws_nat_gateway" and data_item["name"] == "this":
        natgatewaysubnetid = data_item["instances"][0]["attributes"]["subnet_id"]

# Getting EC2 Private Name

ec2privatename = None

for data_item in state_file_json["resources"]:
    if data_item["type"] == "aws_instance" and data_item["name"] == "this":
        ec2privatename = data_item["instances"][0]["attributes"]["tags"]["Name"]

# Getting EC2 Public Name

ec2publicname = None

for data_item in state_file_json["resources"]:
    if data_item["type"] == "aws_instance" and data_item["name"] == "bastion_host":
        ec2publicname = data_item["instances"][0]["attributes"]["tags"]["Name"]

# Getting Public Security Group Name

publicsecuritygroupname = None

for data_item in state_file_json["resources"]:
    if data_item["type"] == "aws_security_group" and data_item["name"] == "public_sg":
        publicsecuritygroupname = data_item["instances"][0]["attributes"]["name"]

# Getting Private Security Group Name

privatesecuritygroupname = None

for data_item in state_file_json["resources"]:
    if data_item["type"] == "aws_security_group" and data_item["name"] == "private_sg":
        privatesecuritygroupname = data_item["instances"][0]["attributes"]["name"]

# Getting Lambda Functions Name

iamrolestografananame = None

for data_item in state_file_json["resources"]:
    if (
        data_item["type"] == "aws_iam_role"
        and data_item["name"] == "lambda_execution_role_IamRolestoGrafana"
    ):
        iamrolestografananame = data_item["instances"][0]["attributes"]["name"]

# Getting IAM Roles Service Name

IamRolesServicename = None

for data_item in state_file_json["resources"]:
    if (
        data_item["type"] == "aws_iam_role"
        and data_item["name"] == "lambda_execution_role_IamRolesService"
    ):
        IamRolesServicename = data_item["instances"][0]["attributes"]["name"]

# Getting project spend cost

functionprojectspendcost = None

for data_item in state_file_json["resources"]:
    if (
        data_item["type"] == "aws_lambda_function"
        and data_item["name"] == "ProjectSpendCost"
    ):
        functionprojectspendcost = data_item["instances"][0]["attributes"][
            "function_name"
        ]

# Getting project cost breakdown

functionprojectcostbreakdown = None

for data_item in state_file_json["resources"]:
    if (
        data_item["type"] == "aws_lambda_function"
        and data_item["name"] == "ProjectCostBreakdown"
    ):
        functionprojectcostbreakdown = data_item["instances"][0]["attributes"][
            "function_name"
        ]

# Getting function total account cost

functiontotalaccountcost = None

for data_item in state_file_json["resources"]:
    if (
        data_item["type"] == "aws_lambda_function"
        and data_item["name"] == "total_account_cost"
    ):
        functiontotalaccountcost = data_item["instances"][0]["attributes"][
            "function_name"
        ]

# Getting function list iam user resources cost

functionlistiamuserresourcescost = None

for data_item in state_file_json["resources"]:
    if (
        data_item["type"] == "aws_iam_role"
        and data_item["name"] == "resources_cost_iam_user"
    ):
        functionlistiamuserresourcescost = data_item["instances"][0]["attributes"][
            "function_name"
        ]

# Getting function instance change

functioninstancechange = None

for data_item in state_file_json["resources"]:
    if (
        data_item["type"] == "aws_lambda_function"
        and data_item["name"] == "InstanceChangeState"
    ):
        functioninstancechange = data_item["instances"][0]["attributes"][
            "function_name"
        ]

# Getting function resource list

functionresourcelist = None

for data_item in state_file_json["resources"]:
    if (
        data_item["type"] == "aws_lambda_function"
        and data_item["name"] == "resource_list_function"
    ):
        functionresourcelist = data_item["instances"][0]["attributes"]["function_name"]

# Getting function list IAM user

functionlistiamuser = None

for data_item in state_file_json["resources"]:
    if (
        data_item["type"] == "aws_lambda_function"
        and data_item["name"] == "list_iam_user"
    ):
        functionlistiamuser = data_item["instances"][0]["attributes"]["function_name"]

# Getting function resource parsing

functionresourceparsing = None

for data_item in state_file_json["resources"]:
    if (
        data_item["type"] == "aws_lambda_function"
        and data_item["name"] == "resource_parsing_function"
    ):
        functionresourceparsing = data_item["instances"][0]["attributes"][
            "function_name"
        ]

# Getting function IAM role service map

functioniamroleservicemap = None

for data_item in state_file_json["resources"]:
    if (
        data_item["type"] == "aws_lambda_function"
        and data_item["name"] == "IamRolesServiceMapping"
    ):
        functioniamroleservicemap = data_item["instances"][0]["attributes"][
            "function_name"
        ]


# Getting function most expensive service

functionmostexpensiveservice = None

for data_item in state_file_json["resources"]:
    if (
        data_item["type"] == "aws_lambda_function"
        and data_item["name"] == "most_expensive_service"
    ):
        functionmostexpensiveservice = data_item["instances"][0]["attributes"][
            "function_name"
        ]

# Getting function total account cost arn

functiontotalaccountcost_arn = None

for data_item in state_file_json["resources"]:
    if (
        data_item["type"] == "aws_lambda_function"
        and data_item["name"] == "total_account_cost"
    ):
        functiontotalaccountcost_arn = data_item["instances"][0]["attributes"]["arn"]


# Getting function most expensive arn

functionmostexpensiveservice_arn = None

for data_item in state_file_json["resources"]:
    if (
        data_item["type"] == "aws_lambda_function"
        and data_item["name"] == "most_expensive_service"
    ):
        functionmostexpensiveservice_arn = data_item["instances"][0]["attributes"][
            "arn"
        ]

# Getting function resource list function arn

functionresourcelistfunction_arn = None

for data_item in state_file_json["resources"]:
    if (
        data_item["type"] == "aws_lambda_function"
        and data_item["name"] == "resource_list_function"
    ):
        functionresourcelistfunction_arn = data_item["instances"][0]["attributes"][
            "arn"
        ]


# Getting function project spend cost arn

functionprojectspendcost_arn = None

for data_item in state_file_json["resources"]:
    if (
        data_item["type"] == "aws_lambda_function"
        and data_item["name"] == "ProjectSpendCost"
    ):
        functionprojectspendcost_arn = data_item["instances"][0]["attributes"]["arn"]


# Getting function project cost breakdown arn

functionprojectcostbreakdown_arn = None

for data_item in state_file_json["resources"]:
    if (
        data_item["type"] == "aws_lambda_function"
        and data_item["name"] == "ProjectCostBreakdown"
    ):
        functionprojectcostbreakdown_arn = data_item["instances"][0]["attributes"][
            "arn"
        ]


# Getting rest api ID

restapiID = None

for data_item in state_file_json["resources"]:
    if (
        data_item["type"] == "aws_api_gateway_deployment"
        and data_item["name"] == "apideploy"
    ):
        restapiID = data_item["instances"][0]["attributes"]["rest_api_id"]