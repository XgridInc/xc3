import boto3  # Importing boto3 library for AWS interactions
import json  # Importing json library for JSON operations
import csv   # Importing csv library for CSV file operations
import io    # Importing io library for input and output operations
import os    # Importing os library for operating system related operations

import urllib3   # Importing urllib3 library for HTTP requests


sns_topic_arn = os.environ['SNS_TOPIC_ARN']  # Retrieve SNS topic ARN from environment variable
http = urllib3.PoolManager()  # Creating an HTTP connection pool manager

sns = boto3.client('sns')  # Creating an SNS client

def lambda_handler(event, context):

    url = os.environ["SLACK_WEBHOOK_URL"]  # Slack webhook URL
    # List of untagged resources
    untagged_resources = []
    non_compliant_resources = []

  # Extract payload data from the event
    payload1 = event.get('Payload1')  # Assuming payload is passed directly
    payload2 = event.get('Payload2')

    if payload1:
        # Append payload data to the untagged_resources list
        untagged_resources.extend(payload1)
    if payload2:
        non_compliant_resources.extend(payload2)

    # Prepare message
    message = "Dear Team and Administrator,\n\n"+ "I hope this message finds you well. I wanted to bring to your attention a list of untagged resources and the resources that does not have proper tags for proper cost allocation.\n"+ "Below is the list of resources found without proper tags for cost allocation.\n\n\n"

    for index in range(len(untagged_resources)):
        message += f"{index + 1}. {untagged_resources[index]}\n\n"

    #Show this message only if there are resource with tags that are not appropriate for cost allocation
    if non_compliant_resources:
        message += "\nFollowing are the resources without proper tags for cost allocation:\n"

        for index in range(len(non_compliant_resources)):
            message += f"{index + 1}. {non_compliant_resources[index]}\n\n"

    message += "\n\nYour assistance in reviewing these resources and assigning appropriate tags to them would be greatly appreciated.\n"+ "Thank you for your attention to this matter.\n\nBest Regards"

    # Publish message to SNS topic
    response = sns.publish(
        TopicArn=sns_topic_arn,  # Use dynamically retrieved SNS topic ARN 
        Message=message,
        Subject='Regarding Untagged Resources',
    )

    # Sending Message to Slack Channel
    msg = {
        "channel": "#untagged-resources",  # Slack channel where the message will be posted
        "username": "WEBHOOK_USERNAME",    # Username for the message
        "text": message,  # Message content obtained from SNS event
        "icon_emoji": "",  # Icon emoji for the message
    }

    # Encode message as JSON
    encoded_msg = json.dumps(msg).encode("utf-8")
    
    # Send HTTP POST request to Slack webhook URL
    resp = http.request("POST", url, body=encoded_msg)

    # Print response details
    print(
        {
            "message": message,  # Original SNS message
            "status_code": resp.status,  # HTTP status code of the response
            "response": resp.data,       # Response data
        }
    )

    return {
        'statusCode': 200,
        'body': json.dumps('Notification sent to SNS topic and Slack channel.')
    }
