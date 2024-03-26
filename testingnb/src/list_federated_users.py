import boto3  # Importing boto3 library for AWS interactions
import csv  # Importing csv module for CSV file handling

def lambda_handler(event, context):
    """
    Lambda function handler to list IAM users, retrieve their details, write to a CSV file,
    and upload the CSV file to an S3 bucket.

    Returns:
    - dict: Dictionary containing status code and response body.
    """
    # Initialize the boto3 clients for IAM and S3
    iam_client = boto3.client('iam')  # Creating client for IAM
    s3_client = boto3.client('s3')  # Creating client for S3

    # List users
    users = iam_client.list_users()  # Getting list of IAM users

    # Open a CSV file for writing
    with open('/tmp/users.csv', 'w') as f:  # Opening CSV file in write mode
        writer = csv.writer(f)  # Creating CSV writer object
        writer.writerow(['UserId', 'UserName', 'UserCreateDate', 'UserEmail'])  # Writing header row

        # Iterate through each user
        for user in users['Users']:  # Iterating through IAM users
            # Retrieve user tags
            user_tags = iam_client.list_user_tags(UserName=user['UserName'])  # Getting tags for the user

            # Extract email tag (if available)
            email_tag = next((tag for tag in user_tags['Tags'] if tag['Key'] == 'email'), None)  # Searching for email tag
            email = email_tag['Value'] if email_tag else 'N/A'  # Extracting email value or assigning 'N/A'

            # Write user data to CSV
            writer.writerow([user['UserId'], user['UserName'], user['CreateDate'], email])  # Writing user data row

    # Upload the CSV file to S3
    s3_client.upload_file('/tmp/users.csv', 'nb-details-bucket', 'users.csv')  # Uploading CSV file to S3 bucket
