import json
import boto3
import urllib.request
import os


def calculate_total_cost_by_region_service(json_data):
    # Load JSON data into a list of dictionaries
    data_list = json.loads(json_data)

    # Create a nested dictionary to store the total cost for each unique region and service
    total_cost_by_region_service = {}

    # Calculate the total cost for each unique region and service
    for item in data_list:
        service = item["Service"]
        region = item["Region"]
        cost = float(item["Cost"])

        if region not in total_cost_by_region_service:
            total_cost_by_region_service[region] = {}

        if service not in total_cost_by_region_service[region]:
            total_cost_by_region_service[region][service] = 0.0

        total_cost_by_region_service[region][service] += cost

    return total_cost_by_region_service


def send_to_slack(payload, slack_webhook_url):
    # Convert the payload to JSON
    data = json.dumps(payload).encode("utf-8")

    # Set the headers with 'Content-Type' as 'application/json'
    headers = {"Content-Type": "application/json"}

    # Send the payload to Slack
    req = urllib.request.Request(slack_webhook_url, data=data, headers=headers)

    # Make the request to the Slack webhook
    try:
        response = urllib.request.urlopen(req)
        print(f"Slack Webhook Response: {response.read().decode('utf-8')}")
    except urllib.error.HTTPError as e:
        print(f"Failed to send the payload to Slack. Error: {e.code} {e.reason}")
    except urllib.error.URLError as e:
        print(f"Failed to connect to the Slack webhook. Error: {e.reason}")


# for email


def lambda_handler(event, context):
    # Initialize S3 client
    s3_client = boto3.client("s3")

    # S3 bucket and object details
    bucket_name = os.environ["BUCKET_NAME"]
    object_key = "cost-metrics/services_cost.json"

    # Fetch the Slack webhook URL from environment variables
    slack_webhook_url = os.environ["SLACK_WEBHOOK_URL"]

    try:
        # Get the JSON file from S3
        response = s3_client.get_object(Bucket=bucket_name, Key=object_key)
        json_data = response["Body"].read().decode("utf-8")

        # Parse JSON data
        resource_costs = json.loads(json_data)

        # Initialize CloudWatch client
        cloudwatch_client = boto3.client("cloudwatch")

        # Create a nested dictionary to store the metrics by region and service
        metrics_by_region_service = calculate_total_cost_by_region_service(json_data)

        # Push metrics to CloudWatch
        for region, services in metrics_by_region_service.items():
            for service, cost in services.items():
                cloudwatch_client.put_metric_data(
                    Namespace="RegionServiceCostMetrics",
                    MetricData=[
                        {
                            "MetricName": "RegionServiceCost",
                            "Dimensions": [
                                {"Name": "Region", "Value": region},
                                {"Name": "Service", "Value": service},
                            ],
                            "Value": cost,
                        },
                    ],
                )

        # Calculate the total cost for each unique region and service
        result = calculate_total_cost_by_region_service(json_data)

        # Filter regions that exceed the budget
        budget = os.environ["SERVICES_BUDGET_AMOUNT"]
        high_cost_regions = {
            region: services
            for region, services in result.items()
            if sum(services.values()) > float(budget)
        }

        # If there are high-cost regions, prepare and send the payload to Slack
        if high_cost_regions:
            # Prepare a breakdown of services for each high-cost region
            payload_text = ""
            for region, services in high_cost_regions.items():
                payload_text += (
                    f"Region: {region}, Total Cost: ${sum(services.values()):.2f}\n"
                )
                for service, cost in services.items():
                    payload_text += f"  Service: {service}, Cost: ${cost:.2f}\n"

            # Format the payload for Slack
            payload = {
                "text": payload_text,
                "username": "Cost Calculator",
                "icon_emoji": ":moneybag:",
            }

            # Send the payload to Slack via webhook
            send_to_slack(payload, slack_webhook_url)
            # Compose the email content
            email_subject = "AWS Account Cost Metric"
            email_body = f"The cost of your AWS account for the last 24 hours is: ${payload_text}"
            # Send the email using Amazon SES
            ses_client = boto3.client("ses")
            response = ses_client.send_email(
                Source=os.environ["SES_EMAIL_ADDRESS"],
                Destination={
                    "ToAddresses": [os.environ["SES_EMAIL_ADDRESS"]],
                },
                Message={
                    "Subject": {
                        "Data": email_subject,
                    },
                    "Body": {
                        "Text": {
                            "Data": email_body,
                        },
                    },
                },
            )
        # this is end of email
        return {"statusCode": 200, "body": json.dumps(result)}
    except Exception as e:
        return {"statusCode": 500, "body": str(e)}
