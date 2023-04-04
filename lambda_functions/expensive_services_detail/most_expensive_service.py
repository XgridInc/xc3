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
import json
import os
import logging
from datetime import date, timedelta
from prometheus_client import CollectorRegistry, Gauge, push_to_gateway

# Initialize and Connect to the AWS EC2 Service
try:
    ec2_client = boto3.client('ec2')
except Exception as e:
    logging.error("Error creating boto3 client: " + str(e))

def lambda_handler(event, context):

    """
    List 5 top most expensive services in provided aws region.

    Args:
        Account ID: AWS account id.
        Region: AWS region

    Returns:
        It pushes the 5 most expensive services name and cost with AWS region to Prometheus using push gateway.

    Raises:
        KeyError: Raise error if cost explorer API call does not execute.
    """
    account_id = context.invoked_function_arn.split(':')[4]
    # Cost of last 14 days
    cost_by_days = 14
    end_date = str(date.today())
    start_date = str(date.today() - timedelta(days=cost_by_days))
    parent_list = []
    try:
        # Get the list of all regions
        regions = [region["RegionName"] for region in ec2_client.describe_regions()["Regions"]]
    
    except Exception as e:
        logging.error("Error getting response from ec2 describe region api : " + str(e))
        return {
            'statusCode': 500,
            'body': json.dumps({"Error": str(e)})
        }

    # Loop through each region
    for region in regions:
        top_5_resources = []
        # Connect to the AWS Cost Explorer API for the region
        try:    
            ce_region = boto3.client("ce", region_name=region)
        except Exception as e:
            logging.error("Error creating boto3 client: " + str(e))
            return {
                'statusCode': 500,
                'body': json.dumps({"Error": str(e)})
            }    
    
        # Retrieve the cost and usage data for the defined time period
        try:
            cost_and_usage = ce_region.get_cost_and_usage(
                TimePeriod={"Start": start_date, "End": end_date},
                Granularity="MONTHLY",
                Metrics=["UnblendedCost"],
                Filter={
                    "Dimensions": {
                        "Key": "REGION",
                        "Values": [region],
                    }
                },
                GroupBy=[{"Type": "DIMENSION", "Key": "SERVICE"}],
            )
        except Exception as e:
            logging.error("Error getting response from cost and usage api: " + str(e))
            return {
                'statusCode': 500,
                'body': json.dumps({"Error": str(e)})
            }
    
        # Extract the cost data
        cost_data = cost_and_usage["ResultsByTime"][0]["Groups"]
    
        # Sort the cost data in descending order
        sorted_cost_data = sorted(
            cost_data, key=lambda x: x["Metrics"]["UnblendedCost"]["Amount"], reverse=True
        )
    
        # Get the top 5 most expensive resources
        top_5_resources = sorted_cost_data[:5]    
    
        # Print the top 5 most expensive resources and their costs
        for resource in top_5_resources:
            resourcedata = {
                "Region": region,
                "Service": resource["Keys"][0],
                "Cost": resource["Metrics"]["UnblendedCost"]["Amount"],
            }
            parent_list.append(resourcedata)
    
    logging.info(parent_list)
    
    # Adding the extracted cost data to the Prometheus gauge as labels for service, region, and cost.
    try:
        registry = CollectorRegistry()
        gauge = Gauge("Expensive_Services_Detail", "AWS Services Cost Detail",
           labelnames=["service", "cost", "region", "account"], 
           registry=registry)
        for i in range(len(parent_list)):
            service = parent_list[i]['Service']
            region = parent_list[i]['Region']
            cost = parent_list[i]['Cost']
            gauge.labels(service, cost, region, account_id).set(cost)
    
            # Push the metric to the Prometheus Gateway
            push_to_gateway(os.environ['prometheus_ip'], job='Most_Expensive_Services', registry=registry)
    except Exception as e:
        logging.error("Error initializing Prometheus Registry and Gauge: " + str(e))
        return {
            'statusCode': 500,
            'body': json.dumps({"Error": str(e)})
        }
    # Return the response    
    return {
        'statusCode': 200,
        'body': json.dumps("Metrics Pushed")
    }