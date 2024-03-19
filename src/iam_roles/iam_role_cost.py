import boto3
# from datetime import datetime, timedelta
import csv
from io import StringIO, BytesIO
from prometheus_client import CollectorRegistry, Gauge, push_to_gateway
import gzip
import os
import json
import urllib.request

def format_data(cost_data):
    formatted_data = "Dear Client,\n\n"
    formatted_data += "I hope this message finds you well. Regarding the cost data, please find the details below:\n\n"
    
    # Iterate over each role in the cost_data
    for role_name, role_data in cost_data.items():
        formatted_data += f"Role: {role_name}\n"
        formatted_data += f"Total Cost: ${role_data['TotalCost']}\n"
        
        # Iterate over each function in the role
        for function_name, costs in role_data['Functions'].items():
            formatted_data += f"Function: {function_name}\n"
            for cost_entry in costs:
                formatted_data += f"Start Date: {cost_entry['StartDate']}, Cost: ${cost_entry['Cost']}\n"
            formatted_data += "\n"  # Add a new line between functions
        
        formatted_data += "\n"  # Add a new line between roles
    
    formatted_data += "Best regards,\nXGrid"
    return formatted_data

def lambda_handler(event, context):
    # Your existing code to generate cost_data
    iam_roles = list_iam_roles()
    role_function_mapping = map_roles_to_lambda_functions(iam_roles)
    bucket_name = os.environ["cur_bucket_name"]
    file_key = os.environ["cur_file_key"]
    cost_data = generate_cost_data(role_function_mapping, bucket_name, file_key)

    # Format the cost data
    formatted_data = format_data(cost_data)

    # Fetch the environment variables for Slack
    slack_channel = os.environ.get('C06NAMZR69E')
    slack_username = os.environ.get('bot')
    slack_icon_emoji = os.environ.get(':rocket:')
    slack_webhook_url = os.environ.get('https://hooks.slack.com/services/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')

    # Format the payload for Slack
    payload = {
        'text': formatted_data,
        'channel': slack_channel,
        'username': slack_username,
        'icon_emoji': slack_icon_emoji
    }

    # Send the payload to Slack via webhook
    send_to_slack(payload, 'https://hooks.slack.com/services/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')

    # Send email using Amazon SES
    sender_email = "mailtosagarpoudel@gmail.com"
    receiver_email = "mailtosagarpoudel@gmail.com"
    email_subject = "Lambda Function Notification"

    # Send email using Amazon SES
    ses_client = boto3.client('ses', region_name='ap-southeast-2')
    response_ses = ses_client.send_email(
        Source=sender_email,
        Destination={'ToAddresses': [receiver_email]},
        Message={
            'Subject': {'Data': email_subject, 'Charset': 'UTF-8'},
            'Body': {'Text': {'Data': formatted_data, 'Charset': 'UTF-8'}}
        }
    )

    # Push the metrics to the Prometheus Pushgateway
    push_metrics(cost_data)

    return {
        "statusCode": 200,
        "body": json.dumps("Notification sent successfully!")
    }

def push_metrics(cost_data):
    registry = CollectorRegistry()

    # Define the metric
    cost_gauge = Gauge(
        "aws_lambda_function_cost",
        "AWS Lambda function cost",
        ["role_name", "function_name", "start_date"],
        registry=registry,
    )

    # Iterate over the cost_data to populate the metric
    for role_name, role_data in cost_data.items():
        for function_name, costs in role_data["Functions"].items():
            for cost_entry in costs:
                # Populate the Gauge with labels for role,
                # function, and start date, and set the cost as the value
                cost_gauge.labels(
                    role_name=role_name,
                    function_name=function_name,
                    start_date=cost_entry["StartDate"],
                ).set(cost_entry["Cost"])

    # Push the metrics to the Pushgateway
    push_to_gateway(
        os.environ["prometheus_ip"], job="aws_lambda_costs", registry=registry
    )

    print("Data successfully pushed to Prometheus Pushgateway.")

def send_to_slack(payload, webhook_url):
    # Convert the payload to JSON
    data = json.dumps(payload).encode('utf-8')

    # Send the payload to Slack
    req = urllib.request.Request(webhook_url, data=data, headers={'Content-Type': 'application/json'})
    urllib.request.urlopen(req)

def list_iam_roles():
    iam_client = boto3.client("iam")
    iam_roles = []
    paginator = iam_client.get_paginator("list_roles")
    for page in paginator.paginate():
        for role in page["Roles"]:
            iam_roles.append(role)
    return iam_roles


def map_roles_to_lambda_functions(iam_roles):
    lambda_client = boto3.client("lambda")
    role_function_mapping = []
    paginator = lambda_client.get_paginator("list_functions")
    for page in paginator.paginate():
        for function in page["Functions"]:
            for role in iam_roles:
                if function["Role"] == role["Arn"]:
                    role_function_mapping.append(
                        {
                            "RoleName": role["RoleName"],
                            "RoleArn": role["Arn"],
                            "FunctionName": function["FunctionName"],
                        }
                    )
    return role_function_mapping


def generate_cost_data(role_function_mapping, bucket_name, file_key):
    csv_content = download_and_decompress_csv(bucket_name, file_key)
    csv_reader = csv.DictReader(StringIO(csv_content))

    # Initialize a dictionary to hold cost data for each role
    role_cost_data = {
        mapping["RoleName"]: {"TotalCost": 0, "Functions": {}}
        for mapping in role_function_mapping
    }

    for row in csv_reader:
        if row["lineItem/ProductCode"] == "AWSLambda":
            function_arn = row["lineItem/ResourceId"]
            cost = float(row["lineItem/UnblendedCost"])
            start_date = row["lineItem/UsageStartDate"]

            # Find the corresponding role for the function ARN
            for mapping in role_function_mapping:
                if (
                    mapping["FunctionName"] in function_arn
                ):  # Assuming FunctionName holds the ARN or part of it
                    role_name = mapping["RoleName"]
                    function_name = mapping["FunctionName"]

                    # Initialize function data if not present
                    if function_name not in role_cost_data[role_name]["Functions"]:
                        role_cost_data[role_name]["Functions"][function_name] = {}

                    # Aggregate cost by start date
                    if (
                        start_date
                        in role_cost_data[role_name]["Functions"][function_name]
                    ):
                        role_cost_data[role_name]["Functions"][function_name][
                            start_date
                        ] += cost
                    else:
                        role_cost_data[role_name]["Functions"][function_name][
                            start_date
                        ] = cost

                    # Update the total cost for the role
                    role_cost_data[role_name]["TotalCost"] += cost
                    break

    # Sort the function cost data by date and format it into a list
    for role, data in role_cost_data.items():
        for function_name, date_cost_map in data["Functions"].items():
            sorted_cost_data = [
                {"StartDate": date, "Cost": cost}
                for date, cost in sorted(date_cost_map.items())
            ]
            data["Functions"][function_name] = sorted_cost_data
    
    return role_cost_data


def download_and_decompress_csv(bucket_name, file_key):
    s3_client = boto3.client("s3")
    response = s3_client.get_object(Bucket=bucket_name, Key=file_key)

    # Decompose the file content
    with gzip.GzipFile(fileobj=BytesIO(response["Body"].read())) as gz:
        file_content = gz.read().decode("utf-8")

    return file_content


# lambda_handler(1,2)
