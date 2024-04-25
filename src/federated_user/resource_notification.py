import json
import boto3
import os
from datetime import datetime
import urllib3

sns_topic_arn = os.environ['SNS_TOPIC_ARN']  # Retrieve SNS topic ARN from environment variable
namespace = os.environ['NAME_SPACE']
http = urllib3.PoolManager()  # Creating an HTTP connection pool manager

s3 = boto3.client('s3')

def get_resources_from_s3():
    # Current Date and time to access file in S3 bucket
    current_date = datetime.now()
    year = str(current_date.year)
    month = current_date.strftime('%m')
    day = current_date.strftime('%d')
    
    # Retrieve the file from S3
    bucket_name = (f"{namespace}-metadata-storage")
    file_key = f"fed-resources/{year}/{month}/{day}/resources.json"
    
    try:
        # Retrieve the file from S3
        response = s3.get_object(Bucket=bucket_name, Key=file_key)
        data = response['Body'].read().decode('utf-8')
        
        # Parse the JSON data
        json_data = json.loads(data)
        metadata = json_data['body']
        
        untagged_resources = []
        non_compliant_resources = []
        
        # Iterate over each user in metadata
        for user, resources in metadata.items():
            # Extract non-compliant resources
            non_compliant = resources.get('non-compliant', [])
            for item in non_compliant:
                non_compliant_resources.append(item)
            
            # Extract untagged resources
            untagged = resources.get('untagged', [])
            for item in untagged:
                untagged_resources.append(item)
        
        # return {
        #     "non_compliant_resources": non_compliant_resources,
        #     "untagged_resources": untagged_resources
        # }
        
        print(non_compliant_resources)
        print(untagged_resources)
        return non_compliant_resources, untagged_resources
    
    except s3.exceptions.NoSuchKey:
        return {
            "errorMessage": "The specified key does not exist in the S3 bucket."
        }
    
    except Exception as e:
        return {
            "errorMessage": str(e)
        }

def send_notification(non_compliant_resources, untagged_resources):
    url = os.environ["SLACK_WEBHOOK_URL"]  # Slack webhook URL
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
        "text": message,  # Message content obtained from SNS event
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
    
def lambda_handler(event, context):
    non_compliant_resources, untagged_resources = get_resources_from_s3()
    send_notification(non_compliant_resources, untagged_resources)
