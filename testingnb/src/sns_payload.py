import boto3  # Importing boto3 library for AWS interactions
import json  # Importing json library for JSON operations
import csv   # Importing csv library for CSV file operations
import io    # Importing io library for input and output operations
import os    # Importing os library for operating system related operations

sns_topic_arn = os.environ['SNS_TOPIC_ARN']  # Retrieve SNS topic ARN from environment variable

sns = boto3.client('sns')  # Creating an SNS client

def lambda_handler(event, context):
    # List of untagged resources
    untagged_resources = []

  # Extract payload data from the event
    payload = event.get('Payload')  # Assuming payload is passed directly

    if payload:
        # Append payload data to the untagged_resources list
        untagged_resources.extend(payload)

    # Prepare message
    message = "Dear Team and Administrator,\n\n"+ "I hope this message finds you well. I wanted to bring to your attention a list of untagged resources and the resources that does not have proper tags for proper cost allocation.\n"+ "Below is the list of resources found without proper tags for cost allocation.\n\n\n"

    for index in range(len(untagged_resources)):
        message += f"{index + 1}. {untagged_resources[index]}\n\n"

    message += "\n\nYour assistance in reviewing these resources and assigning appropriate tags to them would be greatly appreciated.\n"+ "Thank you for your attention to this matter.\n\nBest Regards"

    # Publish message to SNS topic
    response = sns.publish(
        TopicArn=sns_topic_arn,  # Use dynamically retrieved SNS topic ARN 
        Message=message
    )

    return {
        'statusCode': 200,
        'body': json.dumps('Message published to SNS topic')
    }
