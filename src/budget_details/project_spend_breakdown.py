import logging
from datetime import datetime
import boto3

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
            Granularity="MONTHLY",  # 'DAILY'|'MONTHLY'|'HOURLY'
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
                {"Type": "DIMENSION", "Key": "SERVICE"},  # Group by SERVICE
                {"Type": "DIMENSION", "Key": "RESOURCE_ID"},  # Group by RESOURCE_ID
            ],
        )

        # Process the response to extract service and resource costs
        cost_data = []
        for group in response["ResultsByTime"]:
            for item in group["Groups"]:
                service = item["Keys"][0]  # first get service
                resource_id = item["Keys"][1]  # then get ResourceID from Keys list
                cost = float(item["Metrics"]["UnblendedCost"]["Amount"])

                start_date_str = group["TimePeriod"]["Start"]
                start_date_str = start_date_str.replace("00:00:00", "12:02:02")
                start_date = datetime.strptime(start_date_str, "%Y-%m-%dT%H:%M:%SZ")
                month_name = start_date.strftime("%B")

                resourcedata = {
                    "month": month_name,
                    "service": service,
                    "resource-id": resource_id,
                    "cost": cost,
                }
                cost_data.append(resourcedata)
        # Filter out blank projects
        cost_data_filtered = [
            data for data in cost_data if data["project_name"] != ""
        ]

        return cost_data

    except Exception as e:
        print(f"Error getting cost of project: {e}")
        return {"statusCode": 500, "body": "Error getting cost of project"}


def lambda_handler(event, context):
    print(event)

    project_name = event["project_name"]
    start_date = event["start_date"]
    end_date = event["end_date"]

    cost_data = get_cost_for_project(project_name, start_date, end_date)

    try:
        registry = CollectorRegistry()
        cost_gauge = Gauge(
            "Project_Cost_Breakdown",
            "Cost of the project resources",
            labelnames=["month", "project_name", "service", "resource_id"],
            registry=registry,
        )

        for line in cost_data:
            # print(line)
            cost_gauge.labels(
                line["month"], project_name, line["service"], line["resource-id"]
            ).set(line["cost"])

        jobname = "Project-Spend-Breakdown-" + project_name
        prometheus_ip = os.environ["prometheus_ip"]
        push_to_gateway(prometheus_ip, job=jobname, registry=registry)

        print("Metrics pushed to Prometheus")
        return {
            "statusCode": 200,
            "body": "Invocation of project_spend_breakdown for project "
            + project_name
            + " successful",
        }

    except Exception as e:
        logging.error("Error in invoking lambda function: " + str(e))
        return {
            "statusCode": 500,
            "body": "Error invoking project_spend_breakdown for project "
            + project_name,
        }