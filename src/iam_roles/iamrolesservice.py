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
from datetime import datetime, timedelta

import boto3
from prometheus_client import CollectorRegistry, Gauge, push_to_gateway


try:
    client = boto3.client("ce")
except Exception as e:
    logging.error("Error creating boto3 client: " + str(e))
try:
    lambda_client = boto3.client("lambda")
except Exception as e:
    logging.error("Error creating boto3 client: " + str(e))
try:
    ec2_client = boto3.client("ec2")
except Exception as e:
    logging.error("Error creating boto3 client: " + str(e))


def cost_of_instance(event, client, resource_id, start_date, end_date):
    """
    Fetches the cost and usage information for a given resource
    ID within a specified time period.

    Args:
        client: The boto3 client to use for the AWS Cost Explorer API.
        resource_id (str): The ID of the resource to fetch cost
        information for.
        start_date (str): The start date of the time period to fetch
        cost information for, in 'YYYY-MM-DD' format.
        end_date (str): The end date of the time period to fetch
        cost information for, in 'YYYY-MM-DD' format.

    Returns:
        The response from the AWS Cost Explorer API in JSON format.
    """
    response = client.get_cost_and_usage_with_resources(
        TimePeriod={"Start": start_date, "End": end_date},
        Granularity="DAILY",
        Filter={
            "Dimensions": {
                "Key": "RESOURCE_ID",
                "Values": [resource_id],
            }
        },
        Metrics=["UnblendedCost"],
    )
    return response


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


def lambda_handler(event, context):
    """
    The main Lambda function that is executed.

    Args:
        event: The input event that triggered the Lambda function.
        context: The context object for the Lambda function.

    Returns:
        A dictionary containing a status code and a message indicating
        that the function has completed.
    """

    registry = CollectorRegistry()

    iam_service_gauge = Gauge(
        "IAM_Role_Service",
        "XC3 IAM Role Info Data",
        labelnames=[
            "TimeSlot",
            "iam_role_of_service",
            "iam_role_service_region",
            "iam_role_service_account",
            "iam_role_service_resource_id",
            "iam_role_service_cost",
            "iam_role_service_state",
        ],
        registry=registry,
    )

    roles = event
    cost_by_days = 14
    end_date = str(datetime.now().date())
    start_date = str(datetime.now().date() - timedelta(days=cost_by_days))
    account_id = context.invoked_function_arn.split(":")[4]

    for i in range(len(roles)):
        arn = roles[i]["Role"]
        role = arn.rsplit("/", 1)[-1]
        role_region = roles[i]["Role_Region"]
        if role_region == "None":
            continue
        else:
            service_details = roles[i]["Service Details"]

            if len(service_details) == 0:
                response = cost_of_instance(event, client, "None", start_date, end_date)
                cumulative = 0.0
                for j in range(len(response["ResultsByTime"])):
                    time_Data = response["ResultsByTime"][j]["TimePeriod"]["End"]
                    new_time = time_Data.replace("00:00:00", "12:02:02")
                    cumulative = cumulative + float(
                        response["ResultsByTime"][j]["Total"]["UnblendedCost"]["Amount"]
                    )
                iam_service_gauge.labels(
                    (datetime.strptime(new_time, "%Y-%m-%dT%H:%M:%SZ")).strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),
                    role,
                    role_region,
                    account_id,
                    "None",
                    "0",
                    "Start",
                ).set(0)

            for detail in service_details:

                # check if detail is a dictionary
                if isinstance(detail, dict):
                    # extract the "Instance_Region" and "Instance" fields
                    instance_region = detail["Instance_Region"]
                    instance_region_name = region_names.get(instance_region, instance_region)
                    instance = detail["Instance"]
                    ec2 = "ec2:instance/" + instance
                    response = cost_of_instance(
                        event, client, instance, start_date, end_date
                    )

                    ec2_resource = boto3.resource("ec2", region_name=instance_region_name)
                    state = ec2_resource.Instance(instance).state["Name"]

                    if state != "terminated":
                        if state == "running":

                            cumulative = 0.0
                            for j in range(len(response["ResultsByTime"])):
                                time_Data = response["ResultsByTime"][j]["TimePeriod"][
                                    "End"
                                ]
                                new_time = time_Data.replace("00:00:00", "12:02:02")
                                cumulative = cumulative + float(
                                    response["ResultsByTime"][j]["Total"][
                                        "UnblendedCost"
                                    ]["Amount"]
                                )

                                iam_service_gauge.labels(
                                    (
                                        datetime.strptime(
                                            new_time, "%Y-%m-%dT%H:%M:%SZ"
                                        )
                                    ).strftime("%Y-%m-%d %H:%M:%S"),
                                    role,
                                    role_region,
                                    account_id,
                                    ec2,
                                    cumulative,
                                    "Stop",
                                ).set(cumulative)
                        elif state == "stopped":
                            cumulative = 0.0
                            for j in range(len(response["ResultsByTime"])):
                                time_Data = response["ResultsByTime"][j]["TimePeriod"][
                                    "End"
                                ]
                                new_time = time_Data.replace("00:00:00", "12:02:02")
                                cumulative = cumulative + float(
                                    response["ResultsByTime"][j]["Total"][
                                        "UnblendedCost"
                                    ]["Amount"]
                                )

                                iam_service_gauge.labels(
                                    (
                                        datetime.strptime(
                                            new_time, "%Y-%m-%dT%H:%M:%SZ"
                                        )
                                    ).strftime("%Y-%m-%d %H:%M:%S"),
                                    role,
                                    role_region,
                                    account_id,
                                    ec2,
                                    cumulative,
                                    "Start",
                                ).set(cumulative)
                    else:
                        continue

                elif isinstance(detail, str):
                    iam_service_gauge.labels(
                        (datetime.strptime(new_time, "%Y-%m-%dT%H:%M:%SZ")).strftime(
                            "%Y-%m-%d %H:%M:%S"
                        ),
                        role,
                        role_region,
                        account_id,
                        detail,
                        "0",
                        "Start",
                    ).set(0)

    push_to_gateway(
        os.environ["prometheus_ip"], job="IAM-roles-service-data", registry=registry
    )

    return {"statusCode": 200, "body": json.dumps("Service Lambda Data Pushed")}
