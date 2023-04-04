# Copyright (c) 2023, Xgrid Inc, https://xgrid.co

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#        http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import boto3
import logging

def lambda_handler(event, context):
   """
    List resources under ownership of specific IAM User.

    Args:
        IAM Users List: IAM Users.

    Returns:
        It return list of resources under ownership of specific IAM user in aws .

    Raises:
        KeyError: Raise error if cost explorer api  call not execute.
   """
   case_list=[]
   # Tag key to fetch resources 
   tag_key = 'Owner'
   # list of specific IAM user
   user_detail_data = ['saman-batool','muhammad-saad','faheem-khan']
   
   # list of specific region 
   list_region= ['eu-west-1','ap-southeast-1','ap-northeast-1']
   
   for user in user_detail_data:
       for region_name in list_region:
           # Initializing resources list for each region
           subset_list=[]
           try:
               client = boto3.client("resourcegroupstaggingapi", region_name= region_name)
           except Exception as e:
               logging.error("Error in initiating boto3 client: " + str(e))
               return {
                    'statusCode': 500,
                    'body': json.dumps({"Error": str(e)})
                }
                
           # getting resource detail using Owner tag        
           try:
               response = client.get_resources(TagFilters=[
                    {
                        'Key': tag_key,
                        'Values': [
                         user,
                        ]
                    },
                ])
           except Exception as e:
               logging.error("Error getting response from resourcegroupstaggingapi: " + str(e))
               return {
                    'statusCode': 500,
                    'body': json.dumps({"Error": str(e)})
                }
           # Creating json dict of response data from CE API     
           response_dict = json.dumps(response)
           parse_string = json.loads(response_dict)
           
           # parsing resource info
           dict_len = len(parse_string["ResourceTagMappingList"])
           if dict_len == 0:
              result_list = {'User': user, 'ResourceList': [''], 'Region': region_name}
              case_list.append(result_list)
           else:
                for item in parse_string["ResourceTagMappingList"]:
                    subset = item["ResourceARN"].split(':')
                    subset_len = len(subset)
                    if subset_len == 6:
                           #adding service and resource id 
                       resource = subset[2]+":"+subset[5]
                       subset_list.append(resource)
                    else:
                           #adding service and resource id 
                        resource = subset[2]+":"+subset[5]+":"+subset[6]
                        subset_list.append(resource)
                # creating resource list for cost and usage api        
                result_list = {'User': user, 'ResourceList': subset_list, 'Region': region_name}
                case_list.append(result_list)
   return {
        'statusCode': 200,
        'body': json.dumps(case_list)
    }
