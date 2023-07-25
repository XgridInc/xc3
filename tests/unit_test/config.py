import json
import os
import subprocess

# Run `terraform plan -out=tfplan` command to generate the plan file
os.chdir("../../infrastructure/")
subprocess.run(["terraform", "init"])
subprocess.run(["terraform", "validate"])
subprocess.run(["terraform", "plan", "-var-file=terraform.auto.tfvars", "-out=tfplan"])

# Run `terraform show -json tfplan` command to get the plan output in JSON format
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


# Json File
# with open("tfplan.json", "w") as file:
#     file.write(f"{terraform_plan_json}")


# Env
env = terraform_plan_json["variables"]["env"]["value"]
os.environ["ENV"] = env
os.system("export ENV")


combined_list = []
for item in terraform_plan_json["planned_values"]["root_module"]["child_modules"]:
    combined_list.extend(item["resources"])

# Region
region = terraform_plan_json["variables"]["region"]["value"]

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
    if data_item["type"] == "aws_ami" and data_item["name"] == "this":
        ec2_ami = data_item["values"]["filter"]["values"][0]
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
