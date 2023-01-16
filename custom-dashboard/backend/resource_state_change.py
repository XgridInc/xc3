import json
import boto3

def lambda_handler(event, context):
    client = boto3.client('ec2')
    instance_id = json.loads(event['body'])['resource_id']
    status = json.loads(event['body'])['status']
    print(instance_id)
    resource_label = instance_id.split('/')
    resource_id  = resource_label[len(resource_label) -1]
    print(resource_id)
    if status == "stopped":
       response = client.start_instances(InstanceIds=[resource_id])
    else:
        response = client.stop_instances(InstanceIds=[resource_id])
    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        },
        'body': json.dumps(response)
    }
