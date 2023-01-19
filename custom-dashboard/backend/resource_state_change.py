import json
import boto3
import botocore
import logging

"""
Instance State Change Method.

Args:
    instance_id: EC2 instance id is passing from event.
    status: EC2 instance state is passing from event.

Returns:
    It stop/start provided ec2 instance based on provided status.

Raises:
    Instance State: Raise error if ec2 instance api not execute.
"""

def lambda_handler(event, context):
    try:
       client = boto3.client('ec2')
    except Exception as e:
        logging.error("Error creating boto3 client: " + str(e))
    instance_id = json.loads(event['body'])['resource_id']
    status = json.loads(event['body'])['status']
    logging.info(instance_id)
    resource_label = instance_id.split('/')
    resource_id  = resource_label[len(resource_label) -1]
    logging.info(resource_id)
    if status == "stopped":
       try:
           response = client.start_instances(InstanceIds=[resource_id])
       except Exception as e:
           logging.error("Error in calling ec2 instance start api:" + str(e))
    else:
        try:
           response = client.stop_instances(InstanceIds=[resource_id])
        except Exception as e:
            logging.error("Error in calling ec2 instance stop api:" + str(e))
    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        },
        'body': json.dumps(response)
    }
