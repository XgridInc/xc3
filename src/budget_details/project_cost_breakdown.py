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
from prometheus_client import CollectorRegistry, Gauge, push_to_gateway


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
        dict: The cost of the services, grouped by service dimension
        and filtered by project tag.
    Raises:
        ValueError: If there is a problem with the input data format,
        or if the calculation fails.
    """
    while True:
        try:
            response = client.get_cost_and_usage(
                TimePeriod={"Start": start, "End": end},
                Granularity="MONTHLY",
                Metrics=["UnblendedCost"],
                GroupBy=[{"Type": "DIMENSION", "Key": "SERVICE"}],
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
        It pushes the services name and cost of the project
        to Prometheus using push gateway.
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
            labelnames=["project_spend_service", "project_spend_cost"],
            registry=registry,
        )
        for i in range(len(parent_list)):
            service = parent_list[i]["Service"]

            cost = parent_list[i]["Cost"]
            data_dict = {
                "Service": service,
                "Cost": cost,
            }

            # add the dictionary to the list
            data_list.append(data_dict)
            gauge.labels(service, cost).set(cost)

            # Push the metric to the Prometheus Gateway
            push_to_gateway(
                os.environ["prometheus_ip"],
                job=f"{project_name}-Service",
                registry=registry,
            )

    except Exception as e:
        logging.error("Error initializing Prometheus Registry and Gauge: " + str(e))
        return {"statusCode": 500, "body": json.dumps({"Error": str(e)})}
    # Return the response
    return {"statusCode": 200, "body": json.dumps(parent_list)}
