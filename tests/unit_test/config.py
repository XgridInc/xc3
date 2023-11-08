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


# Env
env = terraform_plan_json["variables"]["env"]["value"]
os.environ["ENV"] = env
os.system("export ENV")


combined_list = []
for item in terraform_plan_json["planned_values"]["root_module"][
    "child_modules"
]:  # noqa: E501
    combined_list.extend(item["resources"])

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
