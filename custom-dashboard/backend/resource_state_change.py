import json
import boto3
import botocore

"""
Instance State Change Method.

Args:
    instance_id: EC2 instance id is passing from event.
    status: EC2 instance state is passing from event.

Returns:
    It stop/start provided ec2 instance based on provided status.

Raises:
    Authorization: Authorization error,
    Instance State: Raise error if provided instance not exist.
"""

def lambda_handler(event, context):
    client = boto3.client('ec2')
    instance_id = json.loads(event['body'])['resource_id']
    status = json.loads(event['body'])['status']
    print(instance_id)
    try:
       resource_label = instance_id.split('/')
       resource_id  = resource_label[len(resource_label) -1]
       print(resource_id)
       if status == "stopped":
          response = client.start_instances(InstanceIds=[resource_id])
       else:
           response = client.stop_instances(InstanceIds=[resource_id])
    except botocore.exceptions.ClientError as error:
        if error.response['Error']['Code'] == 'LimitExceededException':
           print('API call limit exceeded; backing off and retrying...')
        else:
             raise error
    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        },
        'body': json.dumps(response)
    }
