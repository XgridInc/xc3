import boto3  # Importing boto3 library for AWS interactions
import json  # Importing json library for JSON operations
import csv   # Importing csv library for CSV file operations
import io    # Importing io library for input and output operations
import os    # Importing os library for operating system related operations

sns_topic_arn = os.environ['SNS_TOPIC_ARN']  # Retrieve SNS topic ARN from environment variable

sns = boto3.client('sns')  # Creating an SNS client

def lambda_handler(event, context):
    """
    Lambda function handler to check for untagged resources and publish a notification to SNS if any are found.
    
    Parameters:
        event (dict): Event data passed to the function.
        context (object): Lambda function context object.
    
    Returns:
        dict: Response containing status code and message indicating success.
    """

    s3_client = boto3.client('s3')  # Creating an S3 client
    
    bucket_name = 'xc3'  # Name of the S3 bucket
    file_name = 'cRt.csv'  # Name of the CSV file
    
    # Read the CSV file from S3
    response = s3_client.get_object(Bucket=bucket_name, Key=file_name)
    csv_data = response['Body'].read().decode('utf-8')

    # Parse CSV data
    csv_reader = csv.DictReader(io.StringIO(csv_data), fieldnames=['Resource', 'Tagged'])
    next(csv_reader)  # Skip header row
    
    # Check for untagged resources
    untagged_resources = []
    for row in csv_reader:
        if row['Tagged'].lower() == 'no':
            untagged_resources.append(row['Resource'])
    
    # Prepare message
    message = ""
    if untagged_resources:
        message += "Important Notification: Untagged Resources Detected\nDear User,\nFollowing listed are the untagged resources found:\n"
        for resource in untagged_resources:
            message += resource + "\n"
    else:
        message += "No untagged resources found."

    # Publish message to SNS topic
    sns.publish(
        TopicArn=sns_topic_arn,  # Use dynamically retrieved SNS topic ARN
        Message=message
    )

    return {
        'statusCode': 200,
        'body': json.dumps('Message published to SNS topic')
    }
