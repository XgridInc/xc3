import json
import boto3
import os
import botocore
import logging

runtime_region = os.environ['AWS_REGION']
lambda_client = boto3.client('lambda')

def lambda_handler(event, context):
    """
    Resource Inventory Method.

    Args:
        Region: AWS region.
        Accound ID: AWS account id.

    Returns:
        It return list of ec2 instances in provided aws region.

    Raises:
        Lambda Invoke Error: Raise error if lambda invoke api call not execute,
        KeyError: Raise error if resourcegroupstaggingapi call not execute.
    """
    account_id = context.invoked_function_arn.split(':')[4]
    subset_list=[]
    case_list=[]
    cost_analysis_lambda = "testing-lambda"
    region_name = json.loads(event['body'])['region']
    try:
        response = resource_client.get_resources(ResourceTypeFilters= ['ec2:instance'])
    except Exception as e:
        logging.error("Error calling get resource api: " + str(e))
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
                   #adding service and resource id 
               subset_list.append(subset[2]+":"+subset[5])
            else:
                   #adding service and resource id 
                subset_list.append(subset[2]+":"+subset[5]+":"+subset[6])
    result_list = {'Region': region_name, 'ResourceList': subset_list}
    case_list.append(result_list)
    logging.info(case_list)
    functionName = 'arn:aws:lambda:{0}:{1}:function:{2}'.format(runtime_region,account_id,cost_analysis_lambda)
    try:
        cost_lambda_response = lambda_client.invoke(
            FunctionName = functionName,
            InvocationType = 'RequestResponse',
            Payload = json.dumps(case_list[0])
        )
    except Exception as e:
        logging.error("Error in invoking lambda function: " + str(e))
    result_from_child = json.load(cost_lambda_response['Payload'])
    logging.info(result_from_child['body'])
    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        },
        'body': result_from_child['body']
    }
