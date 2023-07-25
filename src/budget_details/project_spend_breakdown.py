#
# import json
import logging

# import os
# import time
# from datetime import date, timedelta
import boto3

# import botocore
# from prometheus_client import CollectorRegistry, Gauge, push_to_gateway


try:
    ce_client = boto3.client("ce")
except Exception as e:
    logging.error("Error creating boto3 client for ce: " + str(e))


def get_cost_for_project(project_name, start_date, end_date):
    """
    Obtains the cost for resources with the project tag 'project_name' for the given
    period.

    Args:
        project_name (str): The name of a project.
        start_date (str): The start date of the time period in 'YYYY-MM-DD' format.
        end_date (str): The end date of the time period in 'YYYY-MM-DD' format.

    Returns:
        dict: The cost of services in the project.
    """
    try:
        response = ce_client.get_cost_and_usage_with_resources(
            TimePeriod={"Start": start_date, "End": end_date},
            Granularity="MONTHLY",
            # Granularity="DAILY",
            Metrics=["UnblendedCost"],
            Filter={
                "Tags": {
                    "Key": "Project",
                    "Values": [
                        project_name,
                    ],
                },
            },
            GroupBy=[
                {"Type": "DIMENSION", "Key": "RESOURCE_ID"},
                {"Type": "DIMENSION", "Key": "SERVICE"},
            ],
        )

        print("Result from get_cost_and_usage_with_resource")
        print(response)
        return response
    except Exception as e:
        print(f"Error getting cost of project: {e}")
        return None


def lambda_handler(event, context):
    print(event)

    project_name = event["project_name"]
    start_date = event["start_date"]
    end_date = event["end_date"]

    response = get_cost_for_project(project_name, start_date, end_date)
    print("Result from get_cost_and_usage_with_resource")
    print(response)

    return response
