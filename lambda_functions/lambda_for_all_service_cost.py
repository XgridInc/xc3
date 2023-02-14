import os
import json
import logging
import boto3
from prometheus_client import CollectorRegistry, Gauge, push_to_gateway

# Initialize boto3 client
try:
    client = boto3.client('ce')
except Exception as e:
    logging.error("Error creating boto3 client: " + str(e))

def lambda_handler(event, context):
    """
    This is an AWS Lambda function for getting the cost of EC2, RDS, and ECS Service that returns the input event.

    Parameters:
    - event: The input event passed to the function
    - context: The execution context passed to the function

    Returns:
    - The response of the cost and usage API
    """

    try:
        response = client.get_cost_and_usage(
            TimePeriod={
                'Start': event['start'],
                'End':  event['end']
            },
            Granularity='MONTHLY',
            Metrics=['UnblendedCost'],
            Filter={
                'Dimensions': {
                    'Key': 'SERVICE',
                    'Values': ['Amazon Elastic Compute Cloud - Compute', 'Amazon Relational Database Service', 'Amazon Elastic Container Service']
                }
            },
            GroupBy=[
                {
                    'Type': 'DIMENSION',
                    'Key': 'SERVICE'
                }
            ]
        )
    except Exception as e:
        print("Error getting cost and usage: " + str(e))
        return {
            'statusCode': 500,
            'body': json.dumps({"Error": str(e)})
        }

    # Create an empty dictionary to store the service's costs
    keys_amount = {}

    # Extract the service costs from the response
    for group in response["ResultsByTime"][0]['Groups']:
        service = str(group['Keys'])
        cost = group['Metrics']['UnblendedCost']['Amount']
        keys_amount[service] = cost

    try:
        # Initialize the Prometheus registry and gauge
        registry = CollectorRegistry()
        service_gauge = Gauge("Service_Cost", "XCCC Gauge for Cost of all Services",
                  labelnames=["Service", "Metric"], registry=registry)

        # Add the service costs to the gauge
        for service, cost in keys_amount.items():
            service_gauge.labels(service, cost).set(cost)

        # Push the gauge data to Prometheus
        push_to_gateway(os.environ['prometheus_ip'],
                        job='Cost_of_all_services', registry=registry)

    except Exception as e:
        logging.error("Error initializing Prometheus Registry and Gauge: " + str(e))
        return {
            'statusCode': 500,
            'body': json.dumps({"Error": str(e)})
        }

    # Return the response
    return {
        'statusCode': 200,
        'body': json.dumps(response)
    }
