import boto3
import json
from datetime import datetime, timedelta
from prometheus_client import CollectorRegistry, Gauge, push_to_gateway
import os

def lambda_handler(event, context):
    iam_roles = list_iam_roles()
    role_function_mapping = map_roles_to_lambda_functions(iam_roles)
    cost_data = generate_cost_data(role_function_mapping)
    print(cost_data)
    data = cost_data
    # Aggregate the data by function name
    aggregated_data = {}
    for item in data:
        function_name = item['FunctionName']
        if function_name not in aggregated_data:
            aggregated_data[function_name] = []
        
        for result in item['CostData']['ResultsByTime']:
            start_date = result['TimePeriod']['Start']
            amount = result['Total']['UnblendedCost']['Amount']
            aggregated_data[function_name].append({'Start': start_date, 'Amount': amount})
    
    # Example of the aggregated data structure
    for function_name, costs in aggregated_data.items():
        print(f"Function Name: {function_name}")
        for cost in costs:
            print(f"Start Date: {cost['Start']}, Amount: {cost['Amount']}")
        print("\n")
    #print(aggregated_data)
    
    registry = CollectorRegistry()

    # Define the metric
    cost_gauge = Gauge('aws_lambda_function_cost', 'AWS Lambda function cost', ['function_name', 'start_date'], registry=registry)
    
    # Populate the metric with data from aggregated_data
    for function_name, costs in aggregated_data.items():
        for cost_info in costs:
            cost_gauge.labels(function_name=function_name, start_date=cost_info['Start']).set(float(cost_info['Amount']))
    
    # Push the metrics to the Pushgateway
    # Replace 'your_pushgateway_address' with the actual address of your Pushgateway
    #push_to_gateway('your_pushgateway_address', job='aws_lambda_costs', registry=registry)
    push_to_gateway(os.environ["prometheus_ip"], job="aws_lambda_costs", registry=registry)
    
    print("Data successfully pushed to Prometheus Pushgateway.")

	

def list_iam_roles():
    iam_client = boto3.client('iam')
    iam_roles = []
    paginator = iam_client.get_paginator('list_roles')
    for page in paginator.paginate():
        for role in page['Roles']:
            iam_roles.append(role)
    return iam_roles

def map_roles_to_lambda_functions(iam_roles):
    lambda_client = boto3.client('lambda')
    role_function_mapping = []
    paginator = lambda_client.get_paginator('list_functions')
    for page in paginator.paginate():
        for function in page['Functions']:
            for role in iam_roles:
                if function['Role'] == role['Arn']:
                    role_function_mapping.append({'RoleName': role['RoleName'], 'RoleArn': role['Arn'], 'FunctionName': function['FunctionName']})
    return role_function_mapping

def generate_cost_data(role_function_mapping):
    ce_client = boto3.client('ce')
    # Define your start and end dates
    cost_by_days = 14
    end_date = str(datetime.now().date())
    start_date = str(datetime.now().date() - timedelta(days=cost_by_days))
    cost_data = []
    for mapping in role_function_mapping:
        # Example filter, adjust according to your needs
        response = ce_client.get_cost_and_usage(
            TimePeriod={'Start': start_date, 'End': end_date},
            Granularity='DAILY',
            Filter={'Dimensions': {'Key': 'SERVICE', 'Values': ['AWS Lambda']}},
            Metrics=["UnblendedCost"]
        )
        cost_data.append({'RoleName': mapping['RoleName'], 'RoleArn': mapping['RoleArn'], 'FunctionName': mapping['FunctionName'], 'CostData': response})
    return cost_data

class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)
#(1,2)