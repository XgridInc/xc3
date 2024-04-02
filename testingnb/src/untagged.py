import boto3
import json
import os
from botocore.exceptions import ClientError

sns_payload_lambda_arn = os.environ['SNS_PAYLOAD_LAMBDA_ARN']  # Retrieve SNS topic ARN from environment variable

def lambda_handler(event, context):
    # Create AWS clients for S3, EC2, VPC, and Lambda
    s3_client = boto3.client('s3')
    ec2_client = boto3.client('ec2')
    vpc_client = boto3.client('ec2')
    lambda_client = boto3.client('lambda')

    # List untagged S3 buckets
    response = s3_client.list_buckets()
    s3_buckets = []
    for bucket in response['Buckets']:
        try:
            tagging = s3_client.get_bucket_tagging(Bucket=bucket['Name'])
            if 'TagSet' not in tagging:
                s3_buckets.append({'ResourceType': 'S3 Bucket', 'ResourceName': bucket['Name'], 'ResourceARN': f"arn:aws:s3:::{bucket['Name']}"})
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchTagSet':
                s3_buckets.append({'ResourceType': 'S3 Bucket', 'ResourceName': bucket['Name'], 'ResourceARN': f"arn:aws:s3:::{bucket['Name']}"})
            else:
                print(f"Error retrieving tags for bucket {bucket['Name']}: {e}")

    # List untagged EC2 instances
    response = ec2_client.describe_instances()
    ec2_instances = [{'ResourceType': 'EC2 Instance', 'ResourceName': instance['InstanceId'], 'ResourceARN': instance['Arn']} 
    for reservation in response['Reservations'] 
        for instance in reservation['Instances'] 
            if not instance.get('Tags')]

    # List untagged VPCs
    response = vpc_client.describe_vpcs()
    vpcs = [{'ResourceType': 'VPC', 'ResourceName': vpc['VpcId'], 'ResourceARN': vpc['VpcId']} 
    for vpc in response['Vpcs'] 
        if not vpc.get('Tags')]

    # List untagged Lambda functions
    response = lambda_client.list_functions()
    lambda_functions = [{'ResourceType': 'Lambda Function', 'ResourceName': function['FunctionName'], 'ResourceARN': function['FunctionArn']} 
    for function in response['Functions'] 
        if not lambda_client.list_tags(Resource=function['FunctionArn']).get('Tags')]

    # Combine the lists of untagged resources
    untagged_resources = {
        "S3 Buckets": s3_buckets,
        "EC2 Instances": ec2_instances,
        "VPCs": vpcs,
        "Lambda Functions": lambda_functions
    }

    # Store untagged resources in a list
    untagged_resources_found = []
    for resource_type, resources in untagged_resources.items():
        for resource in resources:
            untagged_resources_found.append(f"Resource Type: {resource['ResourceType']}\n Resource Name: {resource['ResourceName']}\n Resource ARN: {resource['ResourceARN']}")


    # Invoke another Lambda function with the untagged resources as payload
    invoke_response = lambda_client.invoke(
        FunctionName=sns_payload_lambda_arn,
        InvocationType='RequestResponse',
        Payload=json.dumps({"Payload": untagged_resources_found})
    )

    responseJson = json.load(response['Payload'])



    # Print the untagged resources
    print("Untagged Resources Found:")
    for resource in untagged_resources_found:
        print(resource)
    print(responseJson)



    # Return a success message or any necessary response
    return "Printed untagged resources successfully."
