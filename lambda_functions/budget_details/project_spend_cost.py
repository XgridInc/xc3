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
import datetime
import os
import logging
from datetime import timedelta
from prometheus_client import CollectorRegistry, Gauge, push_to_gateway

try:
    ec2_client = boto3.client("ec2")
except Exception as e:
    logging.error("Error creating boto3 client: " + str(e))
try:
    ce_client = boto3.client("ce")
except Exception as e:
    logging.error("Error creating boto3 client: " + str(e))



cost_by_days = 30
end_date = str(datetime.datetime.now().date())
start_date = str(datetime.datetime.now().date() - timedelta(days=cost_by_days))


def cost_of_project(ce_client, start_date, end_date):
    """
    Calculates the cost of a project for a given time period.

    Args:
        ce_client (boto3.client): The AWS Cost Explorer client.
        start_date (str): The start date of the time period in 'YYYY-MM-DD' format.
        end_date (str): The end date of the time period in 'YYYY-MM-DD' format.

    Returns:
        dict: The cost of the project, grouped by project tag.
    """
    try:
        response = ce_client.get_cost_and_usage(
            TimePeriod={"Start": start_date, "End": end_date},
            Granularity="MONTHLY",
            Metrics=["UnblendedCost"],
            GroupBy=[
                {"Type": "TAG", "Key": "Project"},
            ],
        )
        return response
    except Exception as e:
        print(f"Error getting cost of project: {e}")
        return None


def lambda_handler(event, context):
    """
    The main function that is executed when the AWS Lambda function is triggered.

    Returns:
        str: A message indicating the success or failure of the function execution.
    """
    try:
        registry = CollectorRegistry()
        g = Gauge(
            "Project_Spend_Cost",
            "XCCC Project Spend Cost",
            labelnames=["project_spend_project", "project_spend_cost"],
            registry=registry,
        )

        response = cost_of_project(ce_client, start_date, end_date)

        for group in response["ResultsByTime"][0]["Groups"]:
            tag_key = group["Keys"][0]
            cost = group["Metrics"]["UnblendedCost"]["Amount"]

            print(f"{tag_key}: {cost}")
            tag_value = tag_key.split("$")[1]
            print(tag_value)
            g.labels(tag_value, cost).set(cost)

        push_to_gateway(
            os.environ["prometheus_ip"], job="Project-Spend-Cost", registry=registry
        )
        return "Successfully executed."
    except Exception as e:
        print(f"Error executing lambda_handler: {e}")
        return "Failed to execute."
    