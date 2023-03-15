import boto3
import os
from prometheus_client import CollectorRegistry, Gauge, push_to_gateway

def lambda_handler(event, context):
    """
    Create dictionary of resources on which provided set of tags are missing in all AWS Region.
    Args: List resources in all AWS Regions 
    Returns:
        dict: The list of resources on which provided tags are missing.
    """
    #Fetching event data 
    lambda_detail = event;
    #List of Tags for filtering
    resources_without_tags = ['Project', 'Owner', 'Creator']
    account_id = os.environ['account_id']
    try:
            registry = CollectorRegistry()
            resource_list_guage = Gauge("ResourceListXmops", "Resource List",
             labelnames=["resource","region","account_id"], 
             registry=registry)
    except Exception as e:
            logging.error("Error initializing Prometheus Registry and Gauge: " + str(e))
            return {
                'statusCode': 500,
                'body': json.dumps({"Error": str(e)})
            }
    for item in range(len(lambda_detail)):
        resource_list = lambda_detail[item]['ResourceList']
        #Initialzing list for resources
        subset_list = []
        for iterator in range(len(resource_list)):
            tag_len = len(resource_list[iterator]['Tags'])
            
            #Filter resources thats don't have any tags
            if tag_len == 0:
                subset = resource_list[iterator]['ResourceARN'].split(':')
                subset_len = len(subset)
                if subset_len == 6:
                    subset_list.append(subset[2]+":"+subset[5])
                else:
                    subset_list.append(subset[2]+":"+subset[5]+":"+subset[6])
                
            else:
                for item_tag in range(len(resource_list[iterator]['Tags'])):
                    #Filter resources thats don't have provided list of tags
                     if resource_list[iterator]['Tags'][item_tag]['Key'] in resources_without_tags:
                        count = 0
                        break
                     else:
                          count = 1
                          continue
                if count == 1:
                   subset = resource_list[iterator]['ResourceARN'].split(':')
                   subset_len = len(subset)
                   if subset_len == 6:
                      subset_list.append(subset[2]+":"+subset[5])
                   else:
                        subset_list.append(subset[2]+":"+subset[5]+":"+subset[6])
        #Pushing resource list in prometheus metric                
        for resource in subset_list:
            resource_list_guage.labels(resource,lambda_detail[item]['Region'],account_id).set(0)
    push_to_gateway(os.environ['prometheus_ip'], job='ResourceListXmops', registry=registry)            
    return {
        'statusCode': 200,
        'body': "success"
    }
