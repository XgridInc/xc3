import boto3  # Importing boto3 library for AWS interactions
import csv  # Importing csv module for CSV file handling
import os  # Importing os module for operating system functionality

def lambda_handler(event, context):
    """
    Lambda function handler to retrieve information about EC2 instances, S3 buckets, Lambda functions, and RDS instances,
    write the details to a CSV file, and upload the CSV file to an S3 bucket.

    Args:
    - event (dict): Event data triggering the Lambda function.
    - context (LambdaContext): Context object representing the current execution environment.

    Returns:
    - str: Confirmation message about the CSV file upload to S3 bucket.
    """
    # Initialize AWS clients for EC2, S3, Lambda, and RDS
    ec2_client = boto3.client('ec2')  # Creating client for EC2
    s3_client = boto3.client('s3')  # Creating client for S3
    lambda_client = boto3.client('lambda')  # Creating client for Lambda
    rds_client = boto3.client('rds')  # Creating client for RDS

    # Retrieve all EC2 instances, S3 buckets, Lambda functions, and RDS instances
    ec2_response = ec2_client.describe_instances()  # Getting information about EC2 instances
    s3_response = s3_client.list_buckets()  # Listing S3 buckets
    lambda_response = lambda_client.list_functions()  # Listing Lambda functions
    rds_response = rds_client.describe_db_instances()  # Getting information about RDS instances

    # Initialize a CSV file
    csv_file = '/tmp/resources.csv'  # Setting CSV file path
    with open(csv_file, 'w', newline='') as csvfile:  # Opening CSV file in write mode
        fieldnames = ['Resource Type', 'Resource ID']  # Defining CSV field names
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)  # Creating CSV writer object
        writer.writeheader()  # Writing header row to CSV

        # Write EC2 instances to the CSV file
        for reservation in ec2_response['Reservations']:  # Iterating through EC2 reservations
            for instance in reservation['Instances']:  # Iterating through instances in reservation
                writer.writerow({'Resource Type': 'EC2 Instance', 'Resource ID': instance['InstanceId']})  # Writing EC2 instance data

        # Write S3 buckets to the CSV file
        for bucket in s3_response['Buckets']:  # Iterating through S3 buckets
            writer.writerow({'Resource Type': 'S3 Bucket', 'Resource ID': bucket['Name']})  # Writing S3 bucket data

        # Write Lambda functions to the CSV file
        for func in lambda_response['Functions']:  # Iterating through Lambda functions
            writer.writerow({'Resource Type': 'Lambda Function', 'Resource ID': func['FunctionName']})  # Writing Lambda function data

        # Write RDS instances to the CSV file
        for db_instance in rds_response['DBInstances']:  # Iterating through RDS instances
            writer.writerow({'Resource Type': 'RDS Instance', 'Resource ID': db_instance['DBInstanceIdentifier']})  # Writing RDS instance data

    # Upload the CSV file to S3
    s3_bucket = 'nb-details-bucket'  # Target S3 bucket name
    s3_key = 'resources.csv'  # Target S3 key
    s3_client.upload_file(csv_file, s3_bucket, s3_key)  # Uploading CSV file to S3 bucket

    return f"CSV file '{s3_key}' uploaded to S3 bucket '{s3_bucket}'."  # Returning confirmation message
