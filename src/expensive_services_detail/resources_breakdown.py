import boto3
import botocore
import os
import logging
from prometheus_client import CollectorRegistry, Gauge, push_to_gateway
import json

# Initialize and Connect to the AWS EC2 Service
try:
    s3 = boto3.client("s3")
except Exception as e:
    logging.error("Error creating boto3 client: " + str(e))


bucket_name = os.environ["bucket_name_get_report"]
report_prefix = os.environ["report_prefix"]

# Creates Prometheus gauges to track resource costs for 5 services by region and account ID,
# adds extracted cost data to the gauges as labels, and pushes metrics to Prometheus Pushgateway.
# Handles potential errors during the process.
def create_and_push_gauge(data_json):
    try:
        # Creating an empty list to store the data
        data_list = []

        # Adding the extracted cost data to the Prometheus
        # gauge as labels for service, region,resource_id, and cost
        registry = CollectorRegistry()
        
        # Create Prometheus gauge to track the cost of resources for 5 services by region and account ID
        for account_id, resource_list in data_json.items():
            gauge_resources_cost = Gauge(
                f"Resource_Cost_{account_id}",
                "Cost of resource of 5 services by region",
                ["region", "service", "resource"],
                registry=registry,
            )
            # Set Prometheus gauge labels with region, service, and resource ID, and update the cost value
            for resource in resource_list:
                region = resource["Region"]
                service = resource["Service"]
                resource_id = resource["ResourceId"]
                cost = resource["Cost"]
                gauge_resources_cost.labels(
                    region=region, service=service, resource=resource_id
                ).set(float(cost))

                # add the dictionary to the list
                data_dict = {
                    "Service": service,
                    "Region": region,
                    "ResourceId": resource_id,
                    "Cost": cost,
                }
                data_list.append(data_dict)

        # Push the metrics to Prometheus Pushgateway
        push_to_gateway(
            os.environ["prometheus_ip"], job="resources_cost", registry=registry
        )
        try:
            push_to_gateway(
                os.environ["prometheus_ip"], job="resources_cost", registry=registry
            )
        except Exception as e:
            print(f"Error occurred while pushing metrics to Prometheus Push Gateway: {e}")
        json_data = json.dumps(data_list)
        return json_data

    except Exception as e:
        logging.error("Error initializing Prometheus Registry and Gauge: " + str(e))
        return {"statusCode": 500, "body": json.dumps({"Error": str(e)})}

# uploads JSON data to an S3 bucket and handles potential errors.
def push_to_s3_bucket(json_data):
    key_name = f'{os.environ["top5_expensive_service_prefix"]}/resource_breakdown.json'
    try:
        s3.put_object(Bucket=os.environ["bucket_name"], Key=key_name, Body=json_data)
    except botocore.exceptions.ClientError as e:
        if e.response["Error"]["Code"] == "NoSuchBucket":
            raise ValueError(f"Bucket not found: {os.environ['bucket_name']}")
        elif e.response["Error"]["Code"] == "AccessDenied":
            raise ValueError(f"Access denied to S3 bucket: {os.environ['bucket_name']}")
        else:
            raise ValueError(f"Failed to upload data to S3 bucket: {str(e)}")


def lambda_handler(event, context):
    data = event["account_id"]
    try:
        if data:
            json_data = create_and_push_gauge(data)
            push_to_s3_bucket(json_data)
            # Return the response
            return {"StatusCode": 200, "body": json.dumps(json_data)}
        else:
            return {
                "StatusCode": 202,
                "body": "No payload found for resource cost breakdown",
            }

    except Exception as e:
        logging.error(
            "Error getting response from resource cost breakdown lambda: " + str(e)
        )
