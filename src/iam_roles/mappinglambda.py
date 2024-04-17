import json
import boto3
import os

def fetch_assume_role_policy_document(role_name):
    iam = boto3.client('iam')

    try:
        # Get the IAM role details, including AssumeRolePolicyDocument
        role_details = iam.get_role(RoleName=role_name)
        assume_role_policy_document = role_details['Role']['AssumeRolePolicyDocument']
        return assume_role_policy_document
    except iam.exceptions.NoSuchEntityException:
        print(f"IAM role '{role_name}' not found.")
    except Exception as e:
        print(f"Error fetching IAM role details: {str(e)}")

    return None

def get_lambda_functions_for_role(role_name):
    lambda_client = boto3.client('lambda')

    try:
        # List Lambda functions associated with the IAM role
        functions_response = lambda_client.list_functions(
            FunctionVersion='ALL',  # Use 'ALL' to list all versions
            MaxItems=123  # Adjust MaxItems as needed
        )

        # Filter Lambda functions associated with the IAM role
        lambda_functions = [func['FunctionArn'] for func in functions_response['Functions'] if role_name in func['Role']]

        return lambda_functions
    except Exception as e:
        print(f"Error fetching Lambda functions for role '{role_name}': {str(e)}")

    return []

def get_s3_buckets_for_role(role_name):
    s3_client = boto3.client('s3')

    try:
        # List S3 buckets associated with the IAM role
        buckets_response = s3_client.list_buckets()

        # Filter S3 buckets associated with the IAM role
        s3_buckets = [bucket['Name'] for bucket in buckets_response['Buckets'] if role_name in bucket['Name']]

        return s3_buckets
    except Exception as e:
        print(f"Error fetching S3 buckets for role '{role_name}': {str(e)}")

    return []

def get_ec2_instances_for_role(role_name):
    try:
        iam = boto3.client('iam')
        service_client = boto3.client('ec2')

        # Get instance profiles associated with the IAM role
        instance_profile_detail = iam.list_instance_profiles_for_role(RoleName=role_name)

        # Initialize a list to store EC2 instance details
        ec2_instances = []

        # Iterate through instance profiles
        for profile in instance_profile_detail['InstanceProfiles']:
            instance_profile_arn = profile['Arn']

            # Describe EC2 instances associated with the instance profile ARN
            ec2_response = service_client.describe_instances(
                Filters=[
                    {
                        "Name": "iam-instance-profile.arn",
                        "Values": [instance_profile_arn],
                    }
                ]
            )

            # Extract EC2 instance details
            for reservation in ec2_response["Reservations"]:
                for instance in reservation["Instances"]:
                    instance_id = instance["InstanceId"]
                    instance_region = instance["Placement"]["AvailabilityZone"][:-1]
                    instance_detail = {
                        "Instance_Region": instance_region,
                        "Instance": instance_id,
                    }
                    ec2_instances.append(instance_detail)

        return ec2_instances
        
    except Exception as e:
        print(f"Error fetching EC2 instances for role '{role_name}': {str(e)}")
        return []

def get_rds_instances_for_role(role_name):
    try:
        iam = boto3.client('iam')
        rds_client = boto3.client('rds')

        # Get instance profiles associated with the IAM role
        instance_profile_detail = iam.list_instance_profiles_for_role(RoleName=role_name)

        # Initialize a list to store RDS instance identifiers
        rds_instances = []

        # Iterate through instance profiles
        for profile in instance_profile_detail['InstanceProfiles']:
            instance_profile_arn = profile['Arn']

            # Describe RDS instances associated with the instance profile ARN
            rds_response = rds_client.describe_db_instances()

            # Extract RDS instance identifiers
            for db_instance in rds_response['DBInstances']:
                rds_instances.append(db_instance['DBInstanceIdentifier'])

        return rds_instances
        
    except Exception as e:
        print(f"Error fetching RDS instances for role '{role_name}': {str(e)}")
        return []

def get_dynamodb_tables_for_role(role_name):
    try:
        dynamodb_client = boto3.client('dynamodb')
        
        # Describe DynamoDB tables associated with the IAM role
        tables_response = dynamodb_client.list_tables()
        
        # Extract DynamoDB table names
        dynamodb_tables = [table_name for table_name in tables_response['TableNames'] if role_name in table_name]
        
        return dynamodb_tables
    except Exception as e:
        print(f"Error fetching DynamoDB tables for role '{role_name}': {str(e)}")
        return []

def parse_roles_from_payload(iam_roles):
    parsed_roles = []

    for role_info in iam_roles:
        role = {
            "RoleName": role_info.get("RoleName", ""),
            "RoleArn": role_info.get("RoleArn", ""),
            "CreationDate": role_info.get("CreationDate", ""),
            "Description": role_info.get("Description", ""),
            "Path": role_info.get("Path", ""),
            "ServiceMapping": []
        }

        # Get AssumeRolePolicyDocument using the fetch_assume_role_policy_document function
        assume_role_policy_document = fetch_assume_role_policy_document(role["RoleName"])

        # Check if AssumeRolePolicyDocument is present
        if assume_role_policy_document:
            statement_service = assume_role_policy_document.get("Statement", [])

            # Parsing services attached to IAM role
            service_mapping = []
            for statement in statement_service:
                data_principal = statement.get("Principal", {})
                for key, value in data_principal.items():
                    if key == "Service":
                        if isinstance(value, list):
                            service_list = [item.split(".")[0] for item in value]
                        else:
                            service_list = [value.split(".")[0]]

                        for resource in service_list:
                            if resource == "lambda":
                                role["LambdaFunctions"] = []
                                lambda_functions = get_lambda_functions_for_role(role["RoleName"])
                                role["LambdaFunctions"] = lambda_functions
                                service_mapping.append(resource)
                            elif resource == "s3":
                                role["S3Buckets"] = []
                                s3_buckets = get_s3_buckets_for_role(role["RoleName"])
                                role["S3Buckets"] = s3_buckets
                                service_mapping.append(resource)
                            elif resource == "ec2":
                                role["EC2Instances"] =[]
                                ec2_instances = get_ec2_instances_for_role(role["RoleName"])
                                role["EC2Instances"] = ec2_instances
                                service_mapping.append(resource)
                            elif resource == "rds":
                                role["RDSInstances"] =[]  
                                rds_instances = get_rds_instances_for_role(role["RoleName"])
                                role["RDSInstances"] = rds_instances
                                service_mapping.append(resource)
                            elif resource == "dynamodb":
                                role["DynamoDBTables"] =[]  
                                dynamodb_tables = get_dynamodb_tables_for_role(role["RoleName"])
                                role["DynamoDBTables"] = dynamodb_tables
                                service_mapping.append(resource)
                            else:
                                service_mapping.append(resource)

            role["ServiceMapping"] = service_mapping if service_mapping else ["No Affiliated Services"]

        parsed_roles.append(role)

    return parsed_roles

def lambda_handler(event, context):
    payload = event
    iam_roles = payload['iam_roles']
    # Fetch roles, Lambda functions, and S3 buckets associated with roles
    parsed_roles = parse_roles_from_payload(iam_roles)
    
    payload = {
        "iam_roles": parsed_roles
    }

    # Convert the payload to JSON
    json_payload = json.dumps(payload)

    # Invoke lambda3
    lambda_client = boto3.client('lambda')
    response = lambda_client.invoke(
        FunctionName= os.environ["func_name_cost_lambda"],
        InvocationType='Event',  # Synchronous invocation
        Payload=json_payload
    )
    
    return {
        'statusCode': 200,
        'body': json.dumps(parsed_roles, indent=2)
    }
