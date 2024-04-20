import boto3
import csv
from io import StringIO
from prometheus_client import CollectorRegistry, Gauge, push_to_gateway
import os
import json
import urllib.request


def download_and_parse_csv(s3_client, bucket_name, file_key):
    """Download and parse CSV file from S3."""
    response = s3_client.get_object(Bucket=bucket_name, Key=file_key)
    csv_string = response["Body"].read().decode("utf-8")
    return list(csv.DictReader(StringIO(csv_string)))


def fetch_lambda_to_role_mapping(lambda_client):
    """Fetch mapping from Lambda ARNs to IAM Role ARNs."""
    mapping_lambda_arn_to_role_arn = {}
    mapping_lambda_name_to_role_arn = {}
    paginator = lambda_client.get_paginator("list_functions")
    for page in paginator.paginate():
        for function in page["Functions"]:
            mapping_lambda_arn_to_role_arn[function["FunctionArn"]] = function["Role"]
            mapping_lambda_name_to_role_arn[function["FunctionName"]] = function["Role"]
    return mapping_lambda_arn_to_role_arn, mapping_lambda_name_to_role_arn


def fetch_topic_subscriptions(sns_client, topic_arns):
    """Fetch subscriptions for given SNS topics."""
    mapping = {}
    for topic_arn in topic_arns:
        if not topic_arn.startswith("arn:aws:sns:"):
            print(f"Invalid ARN skipped: {topic_arn}")
            continue
        try:
            subscriptions = sns_client.list_subscriptions_by_topic(TopicArn=topic_arn)[
                "Subscriptions"
            ]
            mapping[topic_arn] = [
                sub["Endpoint"] for sub in subscriptions if sub["Protocol"] == "lambda"
            ]
        except sns_client.exceptions.NotFoundException:
            print(f"Topic {topic_arn} not found. Skipping...")
        except Exception as e:
            print(f"An error occurred: {e}")
    return mapping


def fetch_cw_to_role_mapping(lambda_name_to_role_arn_mapping, cw_log_group_arns):
    """Map IAM role ARNs for given CloudWatch log group ARNs."""
    mapping = {}
    for cw_log_group_arn in cw_log_group_arns:
        try:
            parts = cw_log_group_arn.split(":")
            if (
                len(parts) >= 7
                and parts[2] == "logs"
                and parts[5] == "log-group"
                and "/aws/lambda/" in parts[6]
            ):
                lambda_function_name = parts[6].split("/")[-1]
                # Used function name to get the mapping, then
                # access the IAM Role from the nested dictionary
                role_arn = lambda_name_to_role_arn_mapping.get(lambda_function_name)
                if role_arn:
                    mapping[cw_log_group_arn] = role_arn
                else:
                    print(f"No role found for CloudWatch log ARN: {cw_log_group_arn}")
            else:
                print(f"Invalid CloudWatch log group ARN format: {cw_log_group_arn}")
        except Exception as e:
            print(f"Error processing CloudWatch log group ARN {cw_log_group_arn}: {e}")

    return mapping


def map_costs_to_roles(
    csv_rows,
    lambda_to_role_mapping,
    topic_subscriptions,
    name_to_role_mapping,
    cw_to_role_mapping,
):
    """Map costs to IAM roles based on Lambda functions and SNS subscriptions."""
    role_costs = {}
    for row in csv_rows:
        product_code = row["lineItem/ProductCode"]
        resource_id = row["lineItem/ResourceId"]
        cost = float(row["lineItem/UnblendedCost"])

        if product_code == "AWSLambda" and resource_id in lambda_to_role_mapping:
            role_arn = lambda_to_role_mapping[resource_id]
            if role_arn not in role_costs:
                role_costs[role_arn] = {
                    "LambdaCost": 0,
                    "SNSCost": 0,
                    "CloudWatchCost": 0,
                }
            role_costs[role_arn]["LambdaCost"] += cost

        elif product_code == "AmazonSNS" and resource_id in topic_subscriptions:
            for lambda_arn in topic_subscriptions[resource_id]:
                if lambda_arn in lambda_to_role_mapping:
                    role_arn = lambda_to_role_mapping[lambda_arn]
                    if role_arn not in role_costs:
                        role_costs[role_arn] = {
                            "LambdaCost": 0,
                            "SNSCost": 0,
                            "CloudWatchCost": 0,
                        }
                    role_costs[role_arn]["SNSCost"] += cost

        elif product_code == "AmazonCloudWatch" and resource_id in cw_to_role_mapping:
            role_arn = cw_to_role_mapping[resource_id]
            if role_arn not in role_costs:
                role_costs[role_arn] = {
                    "LambdaCost": 0,
                    "SNSCost": 0,
                    "CloudWatchCost": 0,
                }
            role_costs[role_arn]["CloudWatchCost"] += cost

    return role_costs


def push_metrics_to_pushgateway(role_costs, prometheus_pushgateway):
    """Push mapped costs by IAM roles to Prometheus Pushgateway."""
    registry = CollectorRegistry()

    # Gauge for Total costs by IAM role
    total_cost_gauge = Gauge(
        "aws_total_cost_by_iam_role",
        "Total Cost by IAM Role",
        ["role_arn"],
        registry=registry,
    )

    # Gauge for Lambda costs by IAM role
    lambda_cost_gauge = Gauge(
        "aws_lambda_cost_by_iam_role",
        "Cost of AWS Lambda by IAM Role",
        ["role_arn"],
        registry=registry,
    )

    # Gauge for SNS costs by IAM role
    sns_cost_gauge = Gauge(
        "aws_sns_cost_by_iam_role",
        "Cost of Amazon SNS by IAM Role",
        ["role_arn"],
        registry=registry,
    )

    # Gauge for CloudWatch costs by IAM role
    cloudwatch_cost_gauge = Gauge(
        "aws_cloudwatch_cost_by_iam_role",
        "Cost of Amazon CloudWatch by IAM Role",
        ["role_arn"],
        registry=registry,
    )

    for role_arn, costs in role_costs.items():
        # Calculate the total cost per IAM role
        total_cost = sum(costs.values())
        total_cost_gauge.labels(role_arn=role_arn).set(total_cost)
        lambda_cost_gauge.labels(role_arn=role_arn).set(costs.get("LambdaCost", 0))
        sns_cost_gauge.labels(role_arn=role_arn).set(costs.get("SNSCost", 0))
        cloudwatch_cost_gauge.labels(role_arn=role_arn).set(
            costs.get("CloudWatchCost", 0)
        )

    push_to_gateway(
        prometheus_pushgateway, job="aws_costs_by_iam_role", registry=registry
    )


# def main(bucket_name, file_key):
#     s3_client = boto3.client("s3")
#     lambda_client = boto3.client("lambda")
#     sns_client = boto3.client("sns")

#     csv_rows = download_and_parse_csv(s3_client, bucket_name, file_key)
#     lambda_to_role_mapping = fetch_lambda_to_role_mapping(lambda_client)

#     sns_topic_arns = {
#         row["lineItem/ResourceId"]
#         for row in csv_rows
#         if row["lineItem/ProductCode"] == "AmazonSNS"
#     }
#     print("SNS Topic ARNs:", sns_topic_arns)
#     topic_subscriptions = fetch_topic_subscriptions(sns_client, sns_topic_arns)

#     role_costs = map_costs_to_roles(
#         csv_rows, lambda_to_role_mapping, topic_subscriptions
#     )

#     for role_arn, cost in role_costs.items():
#         print(f"Role ARN: {role_arn}, Total Cost: {cost}")


# # Example usage - replace 'your-bucket-name' and 'your-file-key' with actual values
# bucket_name = "team1reportbucket"
# file_key = (
#     "report/mycostreport/20240401-20240501/20240405T101631Z/mycostreport-00002.csv"
# )
# main(bucket_name, file_key)

def send_email_ses(role_costs, sender_email, recipient_email):
    # Create the email message
    subject = "AWS Costs by IAM Role"
    body = "AWS Costs by IAM Role:\n\n"
    for role_arn, costs in role_costs.items():
        body += f"Role ARN: {role_arn}\n"
        body += f"Lambda Cost: {costs.get('LambdaCost', 0):.8f}\n"
        body += f"SNS Cost: {costs.get('SNSCost', 0):.8f}\n"
        body += f"CloudWatch Cost: {costs.get('CloudWatchCost', 0):.8f}\n"
        body += f"Total Cost: {sum(costs.values()):.8f}\n\n"

    # Create an SES client
    ses_client = boto3.client("ses")

    # Send the email using SES
    response = ses_client.send_email(
        Source=sender_email,
        Destination={"ToAddresses": [recipient_email]},
        Message={
            "Subject": {"Data": subject},
            "Body": {"Text": {"Data": body}},
        },
    )
    print(f"Email sent! Message ID: {response['MessageId']}")
    return body

def send_to_slack(payload, webhook_url):
    # Convert the payload to JSON
    data = json.dumps(payload).encode('utf-8')

    # Send the payload to Slack
    req = urllib.request.Request(webhook_url, data=data, headers={'Content-Type': 'application/json'})
    urllib.request.urlopen(req)

def lambda_handler(event, context):
    bucket_name = os.environ.get("CUR_s3_bucket_name")
    file_key = os.environ.get("CUR_s3_file_key")

    # Clients initialization
    s3_client = boto3.client("s3")
    lambda_client = boto3.client("lambda")
    sns_client = boto3.client("sns")

    # Download and parse the CSV file
    csv_rows = download_and_parse_csv(s3_client, bucket_name, file_key)

    # Fetch Lambda to IAM role mapping
    (
        lambda_arn_to_role_arn_mapping,
        lambda_name_to_role_arn_mapping,
    ) = fetch_lambda_to_role_mapping(lambda_client)

    # Fetch SNS Topic ARNs and corresponding subscriptions
    sns_topic_arns = {
        row["lineItem/ResourceId"]
        for row in csv_rows
        if row["lineItem/ProductCode"] == "AmazonSNS"
    }
    topic_subscriptions = fetch_topic_subscriptions(sns_client, sns_topic_arns)

    cw_log_group_arns = {
        row["lineItem/ResourceId"]
        for row in csv_rows
        if row["lineItem/ProductCode"] == "AmazonCloudWatch"
    }

    cw_to_role_mapping = fetch_cw_to_role_mapping(
        lambda_name_to_role_arn_mapping, cw_log_group_arns
    )

    # # Map costs to roles
    role_costs = map_costs_to_roles(
        csv_rows,
        lambda_arn_to_role_arn_mapping,
        topic_subscriptions,
        lambda_name_to_role_arn_mapping,
        cw_to_role_mapping,
    )

    # Push metrics or process costs as needed
    # For example, printing the role costs
    # for role_arn, data in role_costs.items():
    #     print(f"Role ARN: {role_arn}, Total Cost: {data}")

    # Push metrics to the Prometheus Pushgateway
    prometheus_pushgateway = os.environ["prometheus_ip"]
    push_metrics_to_pushgateway(role_costs, prometheus_pushgateway)

    print("Data successfully pushed to Prometheus Pushgateway.")

    #Slack 
    slack_channel = os.environ['slack_channel']
    slack_username = os.environ['slack_username']
    slack_icon_emoji = os.environ['slack_icon_emoji']
    slack_channel_url = os.environ['slack_channel_url']

    
    
    # Send email with the role costs using SES
    sender_email = os.environ["ses_email_address"]
    recipient_email = os.environ["receiver_email_address"]
    body = send_email_ses(role_costs, sender_email, recipient_email)

    # Format the payload for Slack
    payload = {
        'text': body,
        'channel': slack_channel,
        'username': slack_username,
        'icon_emoji': slack_icon_emoji
    }

    # Send the payload to Slack via webhook
    send_to_slack(payload, slack_channel_url)

    #send_email_ses(role_costs, sender_email, recipient_email)

    print("Email sent successfully.")