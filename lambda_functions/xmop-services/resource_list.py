import json
import boto3
import os
import logging

try:
    ec2_client = boto3.client('ec2')
except Exception as e:
    logging.error("Error creating boto3 client: " + str(e))
try:
    regions = [region["RegionName"] for region in ec2_client.describe_regions()["Regions"]]
except Exception as e:
    logging.error("Error describing ec2 regions: " + str(e))

try:
   lambda_client = boto3.client('lambda')
except Exception as e:
    logging.error("Error creating lambda client: " + str(e))
    
def lambda_handler(event, context):
    """
    Fetch a list resources in all AWS Region.

    Returns:
        dict: The list of resources in a specific AWS Region.
    """

    resource_analysis_lambda = os.environ['resource_list_lambda_function']
    #Initializing the dictionary for resources
    case_list = []
    #resource map with region
    list_result = {}
    
    #Tag List to filter resources
    resources_without_tags = ['Project', 'Owner','Creator']
    
    #Initializing resource list
    resources = []
    for region_name in regions:
        try:
            client_resource = boto3.client('resourcegroupstaggingapi',region_name= region_name)
        except Exception as e:
               logging.error("Error initializing resourcegroupstaggingapi api: " + str(e))
               return {
                    'statusCode': 500,
                    'body': json.dumps({"Error": str(e)})
                }   
        try:        
            response = client_resource.get_resources()
        except Exception as e:
               logging.error("Error in calling get_resource api: " + str(e))
               return {
                    'statusCode': 500,
                    'body': json.dumps({"Error": str(e)})
                }

        resources = response["ResourceTagMappingList"] 
            
        dict_len = len(resources)
        if dict_len == 0:
            continue
        else:
            result_list = {'Region': region_name, 'ResourceList': resources} 
            case_list.append(result_list)
    try:
        cost_lambda_response = lambda_client.invoke(
        FunctionName = resource_analysis_lambda,
        InvocationType = 'Event',
        Payload = json.dumps(case_list)
        )
    except Exception as e:
        logging.error("Error in invoking lambda function: " + str(e))
    return {
        'statusCode': 200,
        'body': "success"
    }
