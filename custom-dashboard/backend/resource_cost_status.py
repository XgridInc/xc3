import json
import boto3
import botocore
from datetime import date , timedelta
import logging

"""
Resource Cost and Status Method.

Args:
    resource_list: Set of EC2 instances.
    Region: AWS Region.

Returns:
    It returns cost and status of provided ec2 instances from last 14 days.

Raises:
    KeyError: Raise error if provided instances not exist and cost explorer api not executed.
"""

def lambda_handler(event, context):
    amount = []
    cost_by_days = 14
    data_from_parent = event['ResourceList']
    if len(data_from_parent) == 0:
        status = {'Resource_ID': '', 'Cost': '', 'Status': ''}
        amount.append(status)
    else: 
        try:
            ec2_client = boto3.resource('ec2', region_name=event['Region'])
        except Exception as e:
            logging.error("Error creating ec2 resource: " + str(e))
        try:
            ec2 = boto3.client('ec2', region_name=event['Region'])
        except Exception as e:
            logging.error("Error creating ec2 client: " + str(e))
        end = date.today()
        start = end - timedelta(days=cost_by_days)
        end_date = str(end)
        start_date = str(start)
        data_list = data_from_parent
        resource_for_ce = []
        resourceStatus = []
        try:
            reservations = ec2.describe_instances(Filters=[
            {
                "Name": "instance-state-name",
                "Values": ["terminated"],
            }
            ]).get("Reservations")
        except Exception as e:
            logging.error("Error in calling ec2 describe instances api: " + str(e))
        terminated_instance_list=[]
        for reservation in reservations:
            for instance in reservation["Instances"]:
                instance_id = instance["InstanceId"]
                terminated_instance_list.append(instance_id)
        for resource in data_list:
            if 'instance' in resource:
                resource_label = resource.split('/')
                resource_id  = resource_label[len(resource_label) -1]
                if resource_id in terminated_instance_list:
                   continue
                else:
                    try:
                        response = ec2_client.Instance(resource_id).state
                    except Exception as e:
                        logging.error("Error in calling ec2 instance state: " + str(e))
                    resultSet = {'resource': resource, 'resource_ce': resource_id, 'status':response['Name']}
                    resource_for_ce.append(resultSet)
            else:
                resource_label = resource.split(':')
                resource_id  = resource_label[len(resource_label) -1]
                if resource_id in terminated_instance_list:
                   continue
                else:
                    try:
                        response = ec2_client.Instance(resource_id).state
                    except Exception as e:
                        logging.error("Error in calling ec2 instance state: " + str(e))
                    resultSet = {'resource': resource, 'resource_ce': resource_id, 'status':response['Name']}
                    resource_for_ce.append(resultSet)
        try:
            ce_client = boto3.client('ce')
        except Exception as e:
            logging.error("Error in creating ce client: " + str(e))
        for item in resource_for_ce:
            try:
                ce_response = ce_client.get_cost_and_usage_with_resources(
                        TimePeriod={
                        'Start': start_date,
                        'End':  end_date
                        },
                        Granularity='MONTHLY',
                        Filter={
                        'Dimensions': {
                            'Key': 'RESOURCE_ID',
                            'Values': [item['resource_ce']]
                        }
                        },
                        Metrics=["UnblendedCost"]
                )
            except Exception as e:
                logging.error("Error in calling ce cost and usage api: " + str(e))
            if len(ce_response["ResultsByTime"][0]["Groups"]) != 0:
                amount_value = ce_response["ResultsByTime"][0]["Total"]["UnblendedCost"]["Amount"]
                status = {'Resource_ID': item['resource'], 'Cost': float(amount_value), 'Status': item['status']}
                amount.append(status)
            else:
                 amount_value = ce_response["ResultsByTime"][0]["Total"]["UnblendedCost"]["Amount"]
                 status = {'Resource_ID': item['resource'], 'Cost': float(amount_value), 'Status': item['status']}
                 amount.append(status)
    return {
        'statusCode': 200,
        'body': json.dumps(amount)
    }
