# import json
import logging
import boto3
# import time
# from datetime import date, timedelta

# import botocore
import os
from prometheus_client import CollectorRegistry, Gauge, push_to_gateway

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

def create_prometheus_metrics(project_name, response):
    if response:
        cost_gauge = Gauge("project_cost", "Cost of the project resources", ["project_name", "resource_id", "service"])

        for metric in response["ResultsByTime"]:
            for group in metric["Groups"]:
                resource_id, service = group["Keys"]
                cost = float(group["Metrics"]["UnblendedCost"]["Amount"])
                #setting the value for Prometheus gauge metrics named cost_gauge
                cost_gauge.labels(project_name=project_name, resource_id=resource_id, service=service).set(cost)

        print("Prometheus metrics created successfully")

# Function for pushing metrics to Prometheus
def push_metrics_to_prometheus():
    try:
        push_gateway = os.environ["prometheus_ip"]
        push_to_gateway(push_gateway, job="Project-Spend-Breakdown", registry=CollectorRegistry())
        print("Metrics pushed to Prometheus")
    except Exception as e:
        print(f"Failed to push metrics to Prometheus: {e}")

def lambda_handler(event, context):
    print(event)

    project_name = event["project_name"]
    start_date = event["start_date"]
    end_date = event["end_date"]

    response = get_cost_for_project(project_name, start_date, end_date)
    print("Result from get_cost_and_usage_with_resource")
    print(response)

    create_prometheus_metrics(project_name, response)
    push_metrics_to_prometheus()
    #End-Of-Code: Jasmine

    return "Hello from project spend breakdown"
