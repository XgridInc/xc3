import boto3
import json
import time
import os
def lambda_handler(event, context):
    # Retrieve IAM role details
    iam_roles = get_iam_role_details()

    # Prepare the payload to send to lambda2
    payload = {
        "iam_roles": iam_roles
    }

    # Convert the payload to JSON
    json_payload = json.dumps(payload)

    # Invoke lambda2
    lambda_client = boto3.client('lambda')
    response = lambda_client.invoke(
        FunctionName= os.environ["func_name_mapping_lambda"],
        InvocationType='Event',  # Synchronous invocation
        Payload=json_payload
    )
    
    
    
    # Extract and parse the response

    return 0

def get_iam_role_details():
    iam_client = boto3.client('iam')

    # List all IAM roles in the current AWS account
    response = iam_client.list_roles()

    # Extract details for each IAM role
    iam_roles = []
    for role in response['Roles']:
        role_name = role['RoleName']
        role_arn = role['Arn']
        role_creation_date = role['CreateDate'].strftime('%Y-%m-%d %H:%M:%S')

        # Additional details for each IAM role
        role_description = role.get('Description', '')
        role_path = role.get('Path', '')

        # You can add more details based on your requirements

        iam_roles.append({
            'RoleName': role_name,
            'RoleArn': role_arn,
            'CreationDate': role_creation_date,
            'Description': role_description,
            'Path': role_path,
            # Add more fields as needed
        })

    return iam_roles
