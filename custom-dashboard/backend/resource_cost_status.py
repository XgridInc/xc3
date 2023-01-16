import json
import boto3
from datetime import date , timedelta

def lambda_handler(event, context):
    amount = []
    data_from_parent = event['ResourceList']
    if len(data_from_parent) == 0:
        status = {'Resource_ID': '', 'Cost': '', 'Status': ''}
        amount.append(status)
    else: 
        ec2_client = boto3.resource('ec2', region_name=event['Region'])
        end = date.today()
        start = end - timedelta(days=14)
        end_date = str(end)
        start_date = str(start)
        data_list = data_from_parent
        resource_for_ce = []
        resourceStatus = []
        for resource in data_list:
           if 'instance' in resource:
               resource_label = resource.split('/')
               resource_id  = resource_label[len(resource_label) -1]
               state = ec2_client.Instance(resource_id).state
               resultSet = {'resource': resource, 'resource_ce': resource_id, 'status':state['Name']}
               resource_for_ce.append(resultSet)
           else:
               resource_label = resource.split(':')
               resource_id  = resource_label[len(resource_label) -1]
               state = ec2_client.instance(resource_id)
               resultSet = {'resource': resource, 'resource_ce': resource_id, 'status':state['Name']}
               resource_for_ce.append(resultSet)
        print(resource_for_ce)
        client = boto3.client('ce')
        for item in resource_for_ce:
            ce_response = client.get_cost_and_usage_with_resources(
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
            if len(ce_response["ResultsByTime"][0]["Groups"]) != 0:
               amount_value = ce_response["ResultsByTime"][0]["Total"]["UnblendedCost"]["Amount"]
               status = {'Resource_ID': item['resource'], 'Cost': float(amount_value), 'Status': item['status']}
               print(status)
               amount.append(status)
            else:
                amount_value = ce_response["ResultsByTime"][0]["Total"]["UnblendedCost"]["Amount"]
                status = {'Resource_ID': item['resource'], 'Cost': float(amount_value), 'Status': item['status']}
                print(status)
                amount.append(status)
    return {
        'statusCode': 200,
        'body': json.dumps(amount)
    }