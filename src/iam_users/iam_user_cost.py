import json
import boto3
import os
import urllib.request
from botocore.exceptions import ClientError


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


def send_email(subject, body, recipient):
    # Send the email using Amazon SES
    ses_client = boto3.client("ses")
    try:
        response = ses_client.send_email(
            Source=os.environ["SES_EMAIL_ADDRESS"],
            Destination={
                "ToAddresses": [os.environ["SES_EMAIL_ADDRESS"]],
            },
            Message={
                "Subject": {
                    "Data": subject,
                },
                "Body": {
                    "Text": {
                        "Data": body,
                    },
                },
            },
        )
        print("Email sent successfully.")
    except ClientError as e:
        print(f"Email could not be sent. Error: {e.response['Error']['Message']}")


def lambda_handler(event, context):
    # Initialize S3 client
    s3_client = boto3.client("s3")

    # S3 bucket and object details
    bucket_name = os.environ["BUCKET_NAME"]
    object_key = "cost-metrics/iam_cost.json"

    # Fetch the Slack webhook URL from environment variables
    slack_webhook_url = os.environ["SLACK_WEBHOOK_URL"]
    cloudwatch_client = boto3.client("cloudwatch")

    try:
        # Get the JSON file from S3
        response = s3_client.get_object(Bucket=bucket_name, Key=object_key)
        json_data = response["Body"].read().decode("utf-8")

        # Parse JSON data
        user_costs = json.loads(json_data)

        # Budget threshold
        budget = os.environ["IAM_BUDGET_AMOUNT"]

        # Filter users that exceed the budget
        high_cost_users = [
            user for user in user_costs if float(user["Cost"]) > float(budget)
        ]

        # If there are high-cost users, prepare and send the payload to Slack
        if high_cost_users:
            payload_text = ""
            for user in high_cost_users:
                payload_text += f"IAM User: {user['IAM']}, Region: {user['Region']}, Cost: ${user['Cost']}\n"

            # Format the payload for Slack
            payload = {
                "text": payload_text,
                "username": "IAM Cost Calculator",
                "icon_emoji": "💰",
            }

            # Send the payload to Slack via webhook
            send_to_slack(payload, slack_webhook_url)

            # Prepare and send email
            email_subject = "High-Cost IAM Users Notification"
            email_body = payload_text
            recipient_email = os.environ["SES_EMAIL_ADDRESS"]
            send_email(email_subject, email_body, recipient_email)

        for user in user_costs:
            user_cost = float(user["Cost"])
            user_iam = user["IAM"]
            user_region = user["Region"]

            # Put metric data
            cloudwatch_client.put_metric_data(
                Namespace="IAMCostMetrics",
                MetricData=[
                    {
                        "MetricName": "IAMCost",
                        "Dimensions": [
                            {"Name": "IAMUser", "Value": user_iam},
                            {"Name": "Region", "Value": user_region},
                        ],
                        "Value": user_cost,
                    },
                ],
            )

        return {"statusCode": 200, "body": json.dumps(high_cost_users)}
    except Exception as e:
        return {"statusCode": 500, "body": str(e)}
