import boto3  # Importing boto3 library for AWS interactions
import csv  # Importing csv module for CSV file handling

def get_service_name_and_region(resource_arn):
    """
    Function to extract service name and region from an AWS resource ARN.

    Args:
    - resource_arn (str): AWS resource ARN to extract information from.

    Returns:
    -  Service name and region extracted from the ARN.
    """
    arn_parts = resource_arn.split(':')  # Splitting ARN to extract parts
    region = arn_parts[3]  # Extracting region from ARN
    service_name = arn_parts[2]  # Extracting service name from ARN
    return service_name, region  # Returning extracted service name and region

def lambda_handler(event, context):
    """
    Lambda function handler to list untagged AWS resources, write their details to a CSV file,
    and upload the CSV file to an S3 bucket.

    Returns:
    - dict: Dictionary containing status code and response body.
    """
    # Initialize Boto3 AWS clients
    resource_client = boto3.client('resourcegroupstaggingapi')  # Creating client for resource tagging API
    s3_client = boto3.client('s3')  # Creating client for S3
    
    # List untagged resources
    try:
        untagged_response = resource_client.get_resources(ResourcesPerPage=50, TagFilters=[])  # Getting untagged resources
        untagged_resources = untagged_response['ResourceTagMappingList']  # Extracting list of untagged resources

        """# Check if there are more pages to retrieve""
        if 'NextToken' in untagged_response:
            next_token = untagged_response['NextToken']
        else:
            break"""




    except Exception as e:
        return {
            'statusCode': 500,
            'body': {
                'errorMessage': f'Error listing untagged resources: {str(e)}'
            }
        }
    
    # Define file path for CSV
    csv_file_path = '/tmp/untagged_resources.csv'
    
    # Write CSV data to file
    with open(csv_file_path, mode='w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)  # Creating CSV writer object
        csv_writer.writerow(['ResourceARN', 'ServiceName', 'Region'])  # Writing header row
        for resource in untagged_resources:  # Iterating through untagged resources
            resource_arn = resource.get('ResourceARN', 'Unknown')  # Getting resource ARN
            service_name, region = get_service_name_and_region(resource_arn)  # Extracting service name and region
            csv_writer.writerow([resource_arn, service_name, region])  # Writing data row
    
    # Upload CSV file to S3 bucket
    s3_bucket = "xc3team12nb-metadata-storage"  # Target S3 bucket name
    s3_key = "untagged_resources.csv"  # Target S3 key
    try:
        s3_client.upload_file(csv_file_path, s3_bucket, s3_key)  # Uploading CSV file to S3
    except Exception as e:
        return {
            'statusCode': 500,
            'body': {
                'errorMessage': f'Error uploading CSV file to S3: {str(e)}'
            }
        }
    
    return {
        'statusCode': 200,
        'body': {
            'message': f'CSV file uploaded to S3 bucket {s3_bucket} with key {s3_key}'
        }
    }
