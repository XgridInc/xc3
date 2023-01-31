import json
import boto3
import os
import logging
from datetime import date , timedelta
from prometheus_client import CollectorRegistry, Gauge, push_to_gateway

runtime_region = os.environ['AWS_REGION']
# Initialize boto3 client
try:
    ce_client = boto3.client('ce')
except Exception as e:
    logging.error("Error creating boto3 client: " + str(e))

def lambda_handler(event, context):

    """
    List 5 top most expensive services in specific aws region.

    Args:
        Account ID: AWS account id.

    Returns:
        It pushes the 5 most expensive services name and cost with AWS region to Prometheus using push gateway.

    Raises:
        KeyError: Raise error if cost explorer API call does not execute.
    """
    account_id = context.invoked_function_arn.split(':')[4]
    cost_by_days = 14
    end_date = str(date.today())
    start_date = str(date.today() - timedelta(days=cost_by_days))

    # Get the cost and usage data
    try:
        response = ce_client.get_cost_and_usage(
            TimePeriod={
                'Start': start_date,
                'End': end_date
            },
            Granularity='MONTHLY',
            Metrics=['UnblendedCost'],
            GroupBy=[{
                'Type': 'DIMENSION',
                'Key': 'SERVICE'
            }]
        )
        
    except Exception as e:
        logging.error("Error getting response from cost and usage api: " + str(e))
        return {
            'statusCode': 500,
            'body': json.dumps({"Error": str(e)})
        }
        
    # get top 5 most expensive services 
    top_5_services = sorted(response['ResultsByTime'][0]['Groups'], key=lambda x: x['Metrics']['UnblendedCost']['Amount'], reverse=True)[:5]
    
    # Initialize the Prometheus registry and gauge
    try:
        registry = CollectorRegistry()
        gauge = Gauge("Expensive_Services_Detail", "AWS Services Cost Detail",
           labelnames=["service", "cost", "region", "account"], 
           registry=registry)
        for service in top_5_services:
            service_name = service['Keys'][0]
            service_amount = service['Metrics']['UnblendedCost']['Amount']
            # Add the service costs to the gauge
            gauge.labels(service_name,service_amount,runtime_region,account_id).set(service_amount)
        # Push the gauge data to Prometheus    
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

