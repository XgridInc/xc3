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
import time
from datetime import date, timedelta

import boto3
import botocore
from prometheus_client import CollectorRegistry, Gauge, push_to_gateway


try:
    s3 = boto3.client("s3")
except Exception as e:
    logging.error("Error creating boto3 client for s3: " + str(e))


def get_cost_and_usage_data(client, start, end, project_name=""):
    """
    Retrieves the unblended cost of a given project within a specified time period
    using the AWS Cost Explorer API.
    Args:
        client: A boto3.client object for the AWS Cost Explorer API.
        start_date: A string representing the start date of the time period to
        retrieve cost data for in YYYY-MM-DD format.
        end_date: A string representing the end date of the time period to
        retrieve cost data for in YYYY-MM-DD format.
        project_name: A string representing the name of the project to retrieve
        cost data of that project

    Returns:
        dict: The cost of the services, the usage volume and its unit of measurement
         grouped by service dimension and usage quantity and filtered by project tag.
    Raises:
        ValueError: If there is a problem with the input data format,
        or if the calculation fails.
    """
    while True:
        try:
            response = client.get_cost_and_usage(
                TimePeriod={"Start": start, "End": end},
                Granularity="MONTHLY",
                Metrics=["UnblendedCost", "UsageQuantity"],
                GroupBy=[
                    {"Type": "DIMENSION", "Key": "SERVICE"},
                    {"Type": "DIMENSION", "Key": "USAGE_TYPE"},
                ],
                Filter={
                    "Tags": {
                        "Key": "Project",
                        "Values": [project_name],
                    }
                },
            )
            return response
        except client.exceptions.LimitExceededException:
            # Sleep for 5 seconds and try again
            time.sleep(5)
        except ValueError as ve:
            raise ValueError(
                f"ValueError occurred: {ve}.\nPlease check the input data format."
            )


def lambda_handler(event, context):
    """
    List cost of services in provided project.
    Args:
        project_name: name of the project.
    Returns:
        It pushes the services name and cost of the project and its associated
        resources to Prometheus using push gateway.
    Raises:
        KeyError: Raise error if data not pushed to prometheus.
    """

    project_name = event["project_name"]
    # Cost of last 30 days
    cost_by_days = 30
    end_date = str(date.today())
    start_date = str(date.today() - timedelta(days=cost_by_days))

    parent_list = []
    try:

        ce = boto3.client("ce")
    except Exception as e:
        logging.error("Error creating boto3 client: " + str(e))

    # Retrieve the cost and usage data for the defined time period
    try:
        if project_name != "Others":
            cost_and_usage = get_cost_and_usage_data(
                ce, start_date, end_date, project_name
            )
        else:
            cost_and_usage = get_cost_and_usage_data(ce, start_date, end_date)
    except Exception as e:
        logging.error("Error getting response from cost and usage api: " + str(e))

    # Extract the cost data
    cost_data = cost_and_usage["ResultsByTime"][0]["Groups"]

    # Services of the project and their costs
    for resource in cost_data:
        resourcedata = {
            "Service": resource["Keys"][0],
            "Cost": resource["Metrics"]["UnblendedCost"]["Amount"],
        }
        parent_list.append(resourcedata)

    logging.info(parent_list)

    # Creating an empty list to store the data
    data_list = []

    # Adding the extracted cost data to the Prometheus
    # gauge as labels for service and cost.
    try:
        registry = CollectorRegistry()
        gauge = Gauge(
            f"{project_name}_Services_Cost",
            "AWS Services Cost Detail",
            labelnames=[
                "project_spend_services",
                "project_spend_cost",
                "Usage_type",
                "Usage_Quantity",
                "Unit",
            ],
            registry=registry,
        )
        # loop through api response to get cost and usage metrics
        for pos, value in enumerate(cost_data):
            data_list = value.get("Keys", [])
            metrics = value.get("Metrics", {})
            service, usage_type = data_list[0], data_list[1]
            usage_quantity = metrics.get("UsageQuantity", {}).get("Amount", "N/A")
            unit = metrics.get("UsageQuantity", {}).get("Unit", "N/A")
            cost = metrics.get("UnblendedCost", {}).get("Amount", "N/A")
            gauge.labels(service, cost, usage_type, usage_quantity, unit).set(cost)

            data_dict = {
                "Service": service,
                "Cost": cost,
                "usage_type": usage_type,
                "usage_quantity": usage_quantity,
                "unit": unit,
            }

            # add the dictionary to the list
            data_list.append(data_dict)

            # Push the metric to the Prometheus Gateway
            push_to_gateway(
                os.environ["prometheus_ip"],
                job=f"{project_name}-Service",
                registry=registry,
            )

        # convert data to JSON
        json_data = json.dumps(data_list)
        # upload JSON file to S3 bucket
        bucket_name = os.environ["bucket_name"]
        key_name = f'{os.environ["project_cost_breakdown_prefix"]}/{project_name}.json'
        try:
            s3.put_object(Bucket=bucket_name, Key=key_name, Body=json_data)
        except botocore.exceptions.ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchBucket":
                raise ValueError(f"Bucket not found: {os.environ['bucket_name']}")
            elif e.response["Error"]["Code"] == "AccessDenied":
                raise ValueError(
                    f"Access denied to S3 bucket: {os.environ['bucket_name']}"
                )
            else:
                raise ValueError(f"Failed to upload data to S3 bucket: {str(e)}")
    except Exception as e:
        logging.error("Error initializing Prometheus Registry and Gauge: " + str(e))
        return {"statusCode": 500, "body": json.dumps({"Error": str(e)})}
    # Return the response
    return {"statusCode": 200, "body": json.dumps(parent_list)}
