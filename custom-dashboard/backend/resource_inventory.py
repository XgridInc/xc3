import json
import boto3

def lambda_handler(event, context):
    lambda_client = boto3.client('lambda')
    account_id = context.invoked_function_arn.split(':')[4]
    runtime_region = context.invoked_function_arn.split(':')[3]
    print(runtime_region)
    subset_list=[]
    case_list=[]
    region_name = json.loads(event['body'])['region']
    client_resource = boto3.client('resourcegroupstaggingapi',region_name= region_name)

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

    result_list = {'Region': region_name, 'ResourceList': subset_list}
    case_list.append(result_list)
    cost_lambda_response = lambda_client.invoke(
        FunctionName = 'arn:aws:lambda:' + runtime_region + ':' + account_id + ':function:testing-lambda',
        InvocationType = 'RequestResponse',
        Payload = json.dumps(case_list[0])
    )
    result_from_child = json.load(cost_lambda_response['Payload'])
    print(result_from_child['body'])
    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        },
        'body': result_from_child['body']
    }