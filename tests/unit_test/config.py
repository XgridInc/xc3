"""
Copyright (c) 2023, Xgrid Inc, https://xgrid.co

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

SPDX-License-Identifier: Apache-2.0
"""

import json
import os
import subprocess

# Run `terraform plan -out=tfplan` command to generate the plan file
os.chdir("../../infrastructure/")
subprocess.run(["terraform", "init"])
subprocess.run(["terraform", "validate"])
subprocess.run(
    ["terraform", "plan", "-var-file=terraform.auto.tfvars", "-out=tfplan"]
)  # noqa: E501

# Run `terraform show -json tfplan` command to get the plan output in JSON format    # noqa: E501
terraform_show_output = subprocess.run(
    ["terraform", "show", "-json", "tfplan"], capture_output=True, text=True
).stdout

# Parse the JSON output
terraform_plan_json = json.loads(terraform_show_output)

most_expensive_service = "most_expensive_service"
list_linked_accounts = "list_linked_accounts"
total_account_cost = "total_account_cost"
project_spend_cost = "project_spend_cost"
resource_list = "resource_list"

combined_list = []
for item in terraform_plan_json["planned_values"]["root_module"][
    "child_modules"
]:  # noqa: E501
    combined_list.extend(item["resources"])

kms_id = None
for data_item in combined_list:
    if data_item["type"] == "aws_cloudtrail" and data_item["name"] == "this":
        kms_id = data_item["values"]["kms_key_id"].split("/")[-1]
        break

s3_bucket = None
for data_item in combined_list:
    if (
        data_item["type"] == "aws_s3_bucket"
        and data_item["name"] == "this"
        and data_item["address"] == "module.xc3.aws_s3_bucket.this"
    ):
        s3_bucket = data_item["values"]["bucket"]
        break

s3_bucket_tags = None
for data_item in combined_list:
    if data_item["type"] == "aws_s3_bucket" and data_item["name"] == "this":
        s3_bucket_tags = data_item["values"]["tags"]
        break

vpc_cidr = None
for data_item in combined_list:
    if data_item["type"] == "aws_vpc" and data_item["name"] == "this":
        vpc_cidr = data_item["values"]["cidr_block"]
        break

vpc_public_subnet = None
for data_item in combined_list:
    if data_item["type"] == "aws_subnet" and data_item["name"] == "public_subnet":
        vpc_public_subnet = data_item["values"]["cidr_block"]
        break

vpc_private_subnet = None
for data_item in combined_list:
    if data_item["type"] == "aws_subnet" and data_item["name"] == "private_subnet":
        vpc_private_subnet = data_item["values"]["cidr_block"]
        break

cognito = None
for data_item in combined_list:
    if (
        data_item["type"] == "aws_cognito_user_pool"
        and data_item["address"] == "module.xc3.aws_cognito_user_pool.grafana_pool[0]"
    ):
        cognito = data_item["values"]["name"]
        break

cloudwatch_list_linked_account = None
for data_item in combined_list:
    if (
        data_item["type"] == "aws_cloudwatch_event_rule"
        and data_item["name"] == list_linked_accounts
    ):
        cloudwatch_list_linked_account = data_item["values"]["name"]
        break

cloudwatch_list_linked_account_description = None
for data_item in combined_list:
    if (
        data_item["type"] == "aws_cloudwatch_event_rule"
        and data_item["name"] == list_linked_accounts
    ):
        cloudwatch_list_linked_account_description = data_item["values"]["description"]
        break

cloudwatch_list_linked_account_cron = None
for data_item in combined_list:
    if (
        data_item["type"] == "aws_cloudwatch_event_rule"
        and data_item["name"] == list_linked_accounts
    ):
        cloudwatch_list_linked_account_cron = data_item["values"]["schedule_expression"]
        break

cloudwatch_most_expensive_services = None
for data_item in combined_list:
    if (
        data_item["type"] == "aws_cloudwatch_event_rule"
        and data_item["name"] == most_expensive_service
    ):
        cloudwatch_most_expensive_services = data_item["values"]["name"]
        break

cloudwatch_most_expensive_services_description = None
for data_item in combined_list:
    if (
        data_item["type"] == "aws_cloudwatch_event_rule"
        and data_item["name"] == most_expensive_service
    ):
        cloudwatch_most_expensive_services_description = data_item["values"][
            "description"
        ]
        break

cloudwatch_most_expensive_services_cron = None
for data_item in combined_list:
    if (
        data_item["type"] == "aws_cloudwatch_event_rule"
        and data_item["name"] == most_expensive_service
    ):
        cloudwatch_most_expensive_services_cron = data_item["values"][
            "schedule_expression"
        ]
        break

cloudwatch_project_spend_cost = None
for data_item in combined_list:
    if (
        data_item["type"] == "aws_cloudwatch_event_rule"
        and data_item["name"] == project_spend_cost
    ):
        cloudwatch_project_spend_cost = data_item["values"]["name"]
        break

cloudwatch_project_spend_cost_description = None
for data_item in combined_list:
    if (
        data_item["type"] == "aws_cloudwatch_event_rule"
        and data_item["name"] == project_spend_cost
    ):
        cloudwatch_project_spend_cost_description = data_item["values"]["description"]
        break

cloudwatch_project_spend_cost_cron = None
for data_item in combined_list:
    if (
        data_item["type"] == "aws_cloudwatch_event_rule"
        and data_item["name"] == project_spend_cost
    ):
        cloudwatch_project_spend_cost_cron = data_item["values"]["schedule_expression"]
        break

cloudwatch_resource_list = None
for data_item in combined_list:
    if (
        data_item["type"] == "aws_cloudwatch_event_rule"
        and data_item["name"] == resource_list
    ):
        cloudwatch_resource_list = data_item["values"]["name"]
        break

cloudwatch_resource_list_description = None
for data_item in combined_list:
    if (
        data_item["type"] == "aws_cloudwatch_event_rule"
        and data_item["name"] == resource_list
    ):
        cloudwatch_resource_list_description = data_item["values"]["description"]
        break

cloudwatch_resource_list_cron = None
for data_item in combined_list:
    if (
        data_item["type"] == "aws_cloudwatch_event_rule"
        and data_item["name"] == resource_list
    ):
        cloudwatch_resource_list_cron = data_item["values"]["schedule_expression"]
        break

ec2_ami = None
ec2_ami_count = 0
for data_item in combined_list:
    if data_item["type"] == "aws_instance" and data_item["name"] == "this":
        ec2_ami = data_item["values"]["ami"]
        ec2_ami_count += 1
        break

ec2_az = None
for data_item in combined_list:
    if data_item["type"] == "aws_subnet" and data_item["name"] == "public_subnet":
        ec2_ami = data_item["values"]["availability_zone"]
        break

iam_role_project_spend_cost_name = None
for data_item in combined_list:
    if data_item["type"] == "aws_iam_role" and data_item["name"] == "ProjectSpendCost":
        iam_role_project_spend_cost_name = data_item["values"]["name"]
        break

iam_role_project_spend_cost_assumed_policy = None
for data_item in combined_list:
    if data_item["type"] == "aws_iam_role" and data_item["name"] == "ProjectSpendCost":
        iam_role_project_spend_cost_assumed_policy = data_item["values"][
            "assume_role_policy"
        ]
        break

iam_role_resource_list_name = None
for data_item in combined_list:
    if (
        data_item["type"] == "aws_iam_role"
        and data_item["name"] == "resource_list_service_role"
    ):
        iam_role_resource_list_name = data_item["values"]["name"]
        break

iam_role_resource_list_assumed_policy = None
for data_item in combined_list:
    if (
        data_item["type"] == "aws_iam_role"
        and data_item["name"] == "resource_list_service_role"
    ):
        iam_role_resource_list_assumed_policy = data_item["values"][
            "assume_role_policy"
        ]
        break

iam_role_total_account_cost_name = None
for data_item in combined_list:
    if data_item["type"] == "aws_iam_role" and data_item["name"] == total_account_cost:
        iam_role_total_account_cost_name = data_item["values"]["name"]
        break

iam_role_total_account_cost_assumed_policy = None
for data_item in combined_list:
    if data_item["type"] == "aws_iam_role" and data_item["name"] == total_account_cost:
        iam_role_total_account_cost_assumed_policy = data_item["values"][
            "assume_role_policy"
        ]
        break

iam_role_most_expensive_service_role_name = None
for data_item in combined_list:
    if (
        data_item["type"] == "aws_iam_role"
        and data_item["name"] == "most_expensive_service_role"
    ):
        iam_role_most_expensive_service_role_name = data_item["values"]["name"]
        break

mes_role_assumed_policy = None
for data_item in combined_list:
    if (
        data_item["type"] == "aws_iam_role"
        and data_item["name"] == "most_expensive_service_role"
    ):
        mes_role_assumed_policy = data_item["values"]["assume_role_policy"]
        break

iam_role_list_linked_accounts_name = None
for data_item in combined_list:
    if (
        data_item["type"] == "aws_iam_role"
        and data_item["name"] == list_linked_accounts
    ):
        iam_role_list_linked_accounts_name = data_item["values"]["name"]
        break

iam_role_list_linked_accounts_assumed_policy = None
for data_item in combined_list:
    if (
        data_item["type"] == "aws_iam_role"
        and data_item["name"] == list_linked_accounts
    ):
        iam_role_list_linked_accounts_assumed_policy = data_item["values"][
            "assume_role_policy"
        ]
        break

# Env
env = terraform_plan_json["variables"]["env"]["value"]
os.environ["ENV"] = env
os.system("export ENV")

# Region
region = terraform_plan_json["variables"]["region"]["value"]

# Account ID
account_id = terraform_plan_json["variables"]["account_id"]["value"]

# LB
load_balancer = None
for data_item in combined_list:
    if data_item["type"] == "aws_lb" and data_item["name"] == "this":
        load_balancer = data_item["values"]["name"]
        break
# api gateway
api_gateway = None
for data_item in combined_list:
    if data_item["type"] == "apigw" and data_item["name"] == "this":
        api_gateway = data_item["values"]["name"]
        break
# SQS
sqs_name = None
for data_item in combined_list:
    if data_item["type"] == "aws_sqs_queue" and data_item["name"] == "this":
        sqs_name = data_item["values"]["name"]
        break
# EIC endpoint
ec2_instance_connect_endpoint = None
for data_item in combined_list:
    if (
        data_item["type"] == "aws_ec2_instance_connect_endpoint"
        and data_item["name"] == "eicendpoint"
    ):
        ec2_instance_connect_endpoint = data_item["instances"]["arn"]
        break
# AWS Lambda fucntions
lambda_function_names = []
for data_item in combined_list:
    if data_item["type"] == "aws_lambda_function":
        lambda_function_names.append(data_item["name"])
