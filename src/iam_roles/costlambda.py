import json
import boto3
from prometheus_client import CollectorRegistry, Gauge, push_to_gateway
import datetime
import os

def get_lambda_function_cost(lambda_function_arn, start_date, end_date):
    cost_client = boto3.client('ce')

    try:
        cost_response = cost_client.get_cost_and_usage(
            TimePeriod={
                'Start': start_date,
                'End': end_date
            },
            Granularity='DAILY',
            Metrics=['UnblendedCost'],
            Filter={
                "Dimensions": {
                    "Key": "RESOURCE_ID",
                    "Values": [lambda_function_arn]
                }
            }
        )

        costs = cost_response['ResultsByTime'][0]['Total']['UnblendedCost']['Amount']
        costs = 0 if costs is None else float(costs)

        return costs
    except Exception as e:
        print(f"Error fetching cost for Lambda function '{lambda_function_arn}': {str(e)}")
        return 0
        
def get_ec2_instance_cost(instance_id, start_date, end_date):
    cost_client = boto3.client('ce')

    try:
        cost_response = cost_client.get_cost_and_usage(
            TimePeriod={
                'Start': start_date,
                'End': end_date
            },
            Granularity='DAILY',
            Metrics=['UnblendedCost'],
            Filter={
                "Dimensions": {
                    "Key": "INSTANCE_ID",
                    "Values": [instance_id]
                }
            }
        )

        # Extracting cost
        costs = cost_response['ResultsByTime'][0]['Total']['UnblendedCost']['Amount']
        costs = 0 if costs is None else float(costs)

        return costs

    except Exception as e:
        print(f"Error fetching cost for EC2 instance '{instance_id}': {str(e)}")
        return 0


def get_s3_bucket_cost(s3_bucket_name, start_date, end_date):
    cost_client = boto3.client('ce')

    try:
        cost_response = cost_client.get_cost_and_usage(
            TimePeriod={
                'Start': start_date,
                'End': end_date
            },
            Granularity='DAILY',
            Metrics=['UnblendedCost'],
            Filter={
                "Dimensions": {
                    "Key": "LINKED_ACCOUNT",
                    "Values": [s3_bucket_name]
                }
            }
        )

        costs = cost_response['ResultsByTime'][0]['Total']['UnblendedCost']['Amount']
        costs = 0 if costs is None else float(costs)

        return costs
    except Exception as e:
        print(f"Error fetching cost for S3 bucket '{s3_bucket_name}': {str(e)}")
        return 0

def get_costs_and_push_to_prometheus(parsed_roles, start_date, end_date):
    s3 = boto3.client('s3')
    registry = CollectorRegistry()
	
	# Gauge for IAM Role Information
    iam_role_gauge = Gauge(
        "iam_role_info",
        "IAM Role Information",
        labelnames=["role_name", "rolearn"],
        registry=registry,
    )

    # Gauge for IAM Role and Associated Resource Costs
    iam_role_resource_gauge = Gauge(
        "iam_role_resource_costs",
        "Role and Associated Resource Costs",
        labelnames=["role_name", "service", "resource_name"],
        registry=registry,
    )

    # Gauge for Service Costs
    service_cost_gauge = Gauge(
        "service_costs",
        "Cost of Each Service for IAM Roles",
        labelnames=["role_name", "service"],
        registry=registry,
    )

    for role in parsed_roles:
        role_name = role["RoleName"]
        services = role["ServiceMapping"]
        rolearn = role["RoleArn"]

        total_service_cost = 0  # Total cost for all services
        
        for service in services:
            service_cost = 0  # Cost for each service

            if service == "lambda":
                lambda_costs = []
                for lambda_function_arn in role["LambdaFunctions"]:
                    cost = get_lambda_function_cost(lambda_function_arn, start_date, end_date)
                    iam_role_resource_gauge.labels(role_name=role_name, service=service, resource_name=lambda_function_arn).set(cost)
                    lambda_costs.append({"LambdaFunctionArn": lambda_function_arn, "Cost": cost})
                    service_cost += cost
                
            elif service == "s3":
                s3_costs = []
                for s3_bucket_name in role["S3Buckets"]:
                    cost = get_s3_bucket_cost(s3_bucket_name, start_date, end_date)
                    iam_role_resource_gauge.labels(role_name=role_name, service=service, resource_name=s3_bucket_name).set(cost)
                    s3_costs.append({"S3BucketName": s3_bucket_name, "Cost": cost})
                    service_cost += cost
                
            elif service == "ec2":
                ec2_costs = []
                for ec2_instance_name in role["EC2Instances"]:
                    cost = get_ec2_instance_cost(ec2_instance_name, start_date, end_date)
                    iam_role_resource_gauge.labels(role_name=role_name, service=service, resource_name=ec2_instance_name).set(cost)
                    ec2_costs.append({"EC2InstanceName": ec2_instance_name, "Cost": cost})
                    service_cost += cost
                
            elif service == "rds":
                rds_costs = []
                for db_instance_identifier in role.get("RDSInstances", []):
                    cost = get_rds_instance_cost(db_instance_identifier, start_date, end_date)
                    iam_role_resource_gauge.labels(role_name=role_name, service=service, resource_name=db_instance_identifier).set(cost)
                    rds_costs.append({"DBInstanceIdentifier": db_instance_identifier, "Cost": cost})
                    service_cost += cost
              
            elif service == "dynamodb":
                dynamodb_costs = []
                for table_name in role.get("DynamoDBTables", []):
                    cost = get_dynamodb_table_cost(table_name, start_date, end_date)
                    iam_role_resource_gauge.labels(role_name=role_name, service=service, resource_name=table_name).set(cost)
                    dynamodb_costs.append({"TableName": table_name, "Cost": cost})
                    service_cost += cost
               

            # Set the total service cost as a Prometheus metric for service costs
            service_cost_gauge.labels(role_name=role_name, service=service).set(service_cost)
			
			# Set IAM role info gauge
            iam_role_gauge.labels(role_name=role_name, rolearn=rolearn).set(0)  # Set value to 0 for each role

        # Append the total service cost for all services to the role dictionary
        role["TotalServiceCost"] = total_service_cost

    try:
        push_to_gateway(os.environ["prometheus_ip"], job="iam_roles_service_mapping", registry=registry)
        print("Metrics pushed to Prometheus successfully.")
    except Exception as e:
        print(f"Error pushing metrics to Prometheus: {str(e)}")


def get_rds_instance_cost(db_instance_identifier, start_date, end_date):
    cost_client = boto3.client('ce')

    try:
        cost_response = cost_client.get_cost_and_usage(
            TimePeriod={
                'Start': start_date,
                'End': end_date
            },
            Granularity='DAILY',
            Metrics=['UnblendedCost'],
            Filter={
                "Dimensions": {
                    "Key": "LINKED_ACCOUNT",
                    "Values": [db_instance_identifier]
                }
            }
        )

        costs = cost_response['ResultsByTime'][0]['Total']['UnblendedCost']['Amount']
        costs = 0 if costs is None else float(costs)

        return costs
    except Exception as e:
        print(f"Error fetching cost for RDS instance '{db_instance_identifier}': {str(e)}")
        return 0

def get_dynamodb_table_cost(table_name, start_date, end_date):
    cost_client = boto3.client('ce')

    try:
        cost_response = cost_client.get_cost_and_usage(
            TimePeriod={
                'Start': start_date,
                'End': end_date
            },
            Granularity='DAILY',
            Metrics=['UnblendedCost'],
            Filter={
                "Dimensions": {
                    "Key": "LINKED_ACCOUNT",
                    "Values": [table_name]
                }
            }
        )

        costs = cost_response['ResultsByTime'][0]['Total']['UnblendedCost']['Amount']
        costs = 0 if costs is None else float(costs)

        return costs
    except Exception as e:
        print(f"Error fetching cost for DynamoDB table '{table_name}': {str(e)}")
        return 0

def lambda_handler(event, context):
    payload = event
    # Process payload and push metrics to Prometheus
    parsed_roles = payload['iam_roles']
    # Set start date to the beginning of the current year
    start_date = datetime.datetime(datetime.datetime.now().year, 1, 1).strftime('%Y-%m-%d')
    # Set end date to the current date
    end_date = datetime.datetime.now().strftime('%Y-%m-%d')
    get_costs_and_push_to_prometheus(parsed_roles, start_date, end_date)

    return {
        'statusCode': 200,
        'body': json.dumps({"message": "Metrics pushed to Prometheus successfully."})
    } 

                
