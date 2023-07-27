import datetime
from datetime import timedelta
import boto3
from decimal import Decimal 

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
            Granularity="DAILY",  # Use "DAILY" granularity for more detailed breakdown
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
        cost_data = {}
        for group in response["ResultsByTime"]:
            for item in group["Groups"]:
                service = item["Keys"][0]  # first get service
                resource_id = item["Keys"][1]  # then get ResourceID from Keys list
                cost = Decimal(item["Metrics"]["UnblendedCost"]["Amount"])  # Decimal cost values
                key = f"{service}::{resource_id}"  # combine service with resource_id
                cost_data[key] = str(cost)
            
        return {
            "statusCode": 202,
            "body": cost_data
        }

    except Exception as e:
        print(f"Error getting cost of project: {e}")
        return {
            "statusCode": 500,
            "body": "Error getting cost of project"
        }

def lambda_handler(event, context):
    
    
    project_name = event["project_name"]
    start_date = event["start_date"]
    end_date = event["end_date"]

    response = get_cost_for_project(project_name, start_date, end_date)
    print("Result from get_cost_and_usage_with_resource")
    print(response)
    return response


    
