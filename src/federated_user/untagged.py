import boto3
import json
import os
from botocore.exceptions import ClientError
from datetime import datetime

resource_notification_lambda_arn = os.environ['RESOURCE_NOTIFICATION_LAMBDA_ARN']  # Retrieve SNS topic ARN from environment variable
acc_num = os.environ['ACC_NUM']
namespace = os.environ['NAME_SPACE']

def lambda_handler(event, context):
    # Create AWS clients for S3, EC2, VPC, and Lambda
    s3_client = boto3.client('s3')
    ec2_client = boto3.client('ec2')
    vpc_client = boto3.client('ec2')
    lambda_client = boto3.client('lambda')

    # Extract payload data from the event
    #Federated User account
    account_id_list = event.get('accId')  # Assuming payload is passed directly

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
            if resource['ResourceType'] == "S3 Bucket":
                untagged_resources_found.append(f"Resource Type: {resource['ResourceType']}\n Resource Name: {resource['ResourceName']}\n Resource ARN: {resource['ResourceARN']}")
            else:
                # Split the Resource ARN to extract the account ID
                arn_parts = resource['ResourceARN'].split(':')
                account_id = arn_parts[4]
                # Check if the account ID matches any item in the list of account IDs
                if account_id in account_id_list:
                    untagged_resources_found.append(f"Resource Type: {resource['ResourceType']}\n Resource Name: {resource['ResourceName']}\n Resource ARN: {resource['ResourceARN']}")

    
    #Current Date and time to access file in S3 bucket
    current_date = datetime.now()
    year = str(current_date.year)
    month = current_date.strftime('%m')
    day = current_date.strftime('%d')
    
    # S3 bucket and object key
    # bucket_name = 'xc3team12-metadata-storage'
    # object_key = 'fed-resources/2024/04/03/resources.json'
    bucket_name = (f"{namespace}-metadata-storage")
    object_key = f"fed-resources/{year}/{month}/{day}/resources.json"
    # # Get the JSON file from S3
    # response = s3_client.get_object(Bucket=bucket_name, Key=object_key)
    # data = response['Body'].read().decode('utf-8')
        
    # # Parse JSON data
    # json_data = json.loads(data)
        
    # # Filter data where Compliance is false
    # non_compliant_resources = []
    # for idx, resource in enumerate(json_data['body'][acc_num], start=1):
    #     if resource['Compliance'] == False:
    #         non_compliant_resources.append (f"ResourceArn: {resource['ResourceARN']}")
    try:
        # Get the JSON file from S3
        response = s3_client.get_object(Bucket=bucket_name, Key=object_key)
        data = response['Body'].read().decode('utf-8')
        
        # Parse JSON data
        json_data = json.loads(data)
        
        # Filter data where Compliance is false
        non_compliant_resources = []
        for idx, resource in enumerate(json_data.get('body', {}).get(acc_num, []), start=1):
            if resource.get('Compliance') == False:
                non_compliant_resources.append(f"ResourceArn: {resource.get('ResourceARN')}")
                
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchKey':
            print(f"No such key: {object_key} in bucket: {bucket_name}")
            # Handle the case where the file does not exist
        elif e.response['Error']['Code'] == 'NoSuchBucket':
            print(f"No such bucket: {bucket_name}")
            # Handle the case where the bucket does not exist
        else:
            print(f"An unexpected error occurred: {e}")


    # Invoke another Lambda function with the untagged resources as payload
    invoke_response = lambda_client.invoke(
        FunctionName=resource_notification_lambda_arn,
        InvocationType='RequestResponse',
        Payload=json.dumps({"Payload1": untagged_resources_found, "Payload2": non_compliant_resources})
    )

    # Extract and load the payload from the invoke response
    responseJson = json.loads(invoke_response['Payload'].read().decode("utf-8"))



    # Print the untagged resources
    print("Untagged Resources Found:")
    for resource in untagged_resources_found:
        print(resource)
    print(responseJson)
    print(non_compliant_resources)



    # Return a success message or any necessary response
    return "Printed untagged resources successfully."
