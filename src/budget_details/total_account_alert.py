import os
import boto3
from datetime import datetime, timedelta
import json
import urllib.parse
import urllib.request

# Set the budget amount and budget thresholds
budget_amount = float(os.environ["BUDGET_AMOUNT"])
threshold_25 = budget_amount * 0.25
threshold_50 = budget_amount * 0.5
threshold_75 = budget_amount * 0.75

# Set your Slack webhook URL
slack_webhook_url = os.environ["SLACK_WEBHOOK_URL"]


def send_email(subject, body):
    # Send the email using Amazon SES
    ses_client = boto3.client("ses")
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


def send_slack_message(message):
    # Send a message to Slack using the webhook
    payload = {"text": message}
    data = json.dumps(payload).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    request = urllib.request.Request(slack_webhook_url, data=data, headers=headers)
    response = urllib.request.urlopen(request)


def lambda_handler(event, context):
    # Set the desired time range for the cost metric
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

    # Retrieve the cost metric for the AWS account
    cost_client = boto3.client("ce")
    response = cost_client.get_cost_and_usage(
        TimePeriod={"Start": start_date, "End": end_date},
        Granularity="MONTHLY",
        Metrics=[
            "UnblendedCost",
        ],
    )

    # Extract the cost value from the response
    cost_amount = float(
        response["ResultsByTime"][0]["Total"]["UnblendedCost"]["Amount"]
    )

    # Publish the total cost metric to CloudWatch
    cloudwatch = boto3.client("cloudwatch")
    cloudwatch.put_metric_data(
        Namespace="AccountCost",
        MetricData=[{"MetricName": "TotalCost", "Value": cost_amount, "Unit": "None"}],
    )

    # Check if the cost amount exceeds the budget
    if cost_amount > budget_amount:
        send_email(
            "Budget Exceeded",
            "You have exceeded your budget. Your current cost: ${:.2f}".format(
                cost_amount
            ),
        )
        send_slack_message(
            "Budget Exceeded: Your current cost: ${:.2f}".format(cost_amount)
        )
    elif cost_amount > threshold_75:
        send_email(
            "Budget Exceeded",
            "You have exceeded 75% of your budget. Your current cost: ${:.2f}".format(
                cost_amount
            ),
        )
        send_slack_message(
            "Budget Exceeded - 75%: Your current cost: ${:.2f}".format(cost_amount)
        )
    # elif cost_amount > threshold_50:
    #     send_email("Budget Exceeded", "You have exceeded 50% of your budget. Your current cost: ${:.2f}".format(cost_amount))
    #     send_slack_message("Budget Exceeded - 50%: Your current cost: ${:.2f}".format(cost_amount))
    # elif cost_amount > threshold_25:
    #     send_email("Budget Exceeded", "You have exceeded 25% of your budget. Your current cost: ${:.2f}".format(cost_amount))
    #     send_slack_message("Budget Exceeded - 25%: Your current cost: ${:.2f}".format(cost_amount))

    # Compose the email content
    # email_subject = "AWS Account Cost Metric"
    # email_body = "The cost of your AWS account for the last month is: ${:.2f}".format(cost_amount)

    # # Send the email notification with the cost metric
    # send_email(email_subject, email_body)
    # send_slack_message("Budget Exceeded: Your current cost: ${:.2f}".format(cost_amount))
