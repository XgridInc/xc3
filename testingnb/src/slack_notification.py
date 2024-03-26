import urllib3   # Importing urllib3 library for HTTP requests
import boto3    # Importing boto3 library for AWS interactions
import json     # Importing json library for JSON operations
import csv      # Importing csv library for CSV file operations
import os

http = urllib3.PoolManager()  # Creating an HTTP connection pool manager

def lambda_handler(event, context):
    """
    Lambda function handler to send SNS messages to a Slack channel using a webhook.
    
    Parameters:
        event (dict): Event data passed to the function.
        context (object): Lambda function context object.
    
    Returns:
        None
    """
    url = os.environ["SLACK_WEBHOOK_URL"]  # Slack webhook URL
    
    # Construct Slack message
    msg = {
        "channel": "#untagged-resources",  # Slack channel where the message will be posted
        "username": "WEBHOOK_USERNAME",    # Username for the message
        "text": event["Records"][0]["Sns"]["Message"],  # Message content obtained from SNS event
        "icon_emoji": "",  # Icon emoji for the message
    }

    # Encode message as JSON
    encoded_msg = json.dumps(msg).encode("utf-8")
    
    # Send HTTP POST request to Slack webhook URL
    resp = http.request("POST", url, body=encoded_msg)
    
    # Print response details
    print(
        {
            "message": event["Records"][0]["Sns"]["Message"],  # Original SNS message
            "status_code": resp.status,  # HTTP status code of the response
            "response": resp.data,       # Response data
        }
    )
