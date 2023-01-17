import json
import boto3
import os
import botocore

"""
Resource Inventory Method.

Args:
    Region: AWS region.
    Accound ID: AWS account id.

Returns:
    It return list of ec2 instances in provided aws region.

Raises:
    Authorization: Authorization error,
    KeyError: Raise error if resourcegroupstaggingapi call not execute.
"""

def lambda_handler(event, context):
    runtime_region = os.environ['AWS_REGION']
    account_id = context.invoked_function_arn.split(':')[4]
    subset_list=[]
    case_list=[]
    cost_analysis_lambda = "testing-lambda"
    lambda_client = boto3.client('lambda')
    region_name = json.loads(event['body'])['region']
    client_resource = boto3.client('resourcegroupstaggingapi',region_name= region_name)
    try:
       response = client_resource.get_resources(ResourceTypeFilters= ['ec2:instance'] )
       response_dict = json.dumps(response)
       parse_string = json.loads(response_dict)
       dict_len = len(parse_string["ResourceTagMappingList"])
       if dict_len == 0:
          result_list = {'Region': region_name, 'ResourceList': ['']}
          case_list.append(result_list)
       else:
           for item in parse_string["ResourceTagMappingList"]:
               subset = item["ResourceARN"].split(':')
               subset_len = len(subset)
               if subset_len == 6:
                  subset_list.append(subset[2]+":"+subset[5])
               else:
                   subset_list.append(subset[2]+":"+subset[5]+":"+subset[6])
    except botocore.exceptions.ClientError as error:
        if error.response['Error']['Code'] == 'LimitExceededException':
           print('API call limit exceeded; backing off and retrying...')
        else:
            raise error
    result_list = {'Region': region_name, 'ResourceList': subset_list}
    case_list.append(result_list)
    try:
       cost_lambda_response = lambda_client.invoke(
        FunctionName = 'arn:aws:lambda:{0}:{1}:function:{2}'.format(runtime_region,account_id,cost_analysis_lambda),
        InvocationType = 'RequestResponse',
        Payload = json.dumps(case_list[0])
        )
       result_from_child = json.load(cost_lambda_response['Payload'])
       print(result_from_child['body'])
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
        'body': result_from_child['body']
    }

