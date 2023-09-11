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
import os
from prometheus_client import CollectorRegistry, Gauge, push_to_gateway
from datetime import date, datetime, timedelta

case_list = []
regionName = os.environ["AWS_REGION"]
try:
    client = boto3.client("ce")
except Exception as e:
    logging.error("Error creating boto3 client: " + str(e))
try:
    ssm_client = boto3.client("ssm")
except Exception as e:
    logging.error("Error creating boto3 client for ssm:" + str(e))


def cost_of_instance(event, client, resource_id):
    """
    Return cost of resource from last 14 days

    Args:
        Resource ID: Resource ID.
        Client: Cost Explorer boto3 client
    Returns:
        It return cost of resource from last 14 days
    Raises:
        KeyError: Error if Cost Explorer API call doesn't execute.
    """
    cost_by_days = 14
    end_date = str(date.today())
    start_date = str(date.today() - timedelta(days=cost_by_days))
    ce_response = client.get_cost_and_usage_with_resources(
        TimePeriod={"Start": start_date, "End": end_date},
        Granularity="DAILY",
        Filter={
            "Dimensions": {
                "Key": "RESOURCE_ID",
                "Values": [resource_id],
            }
        },
        Metrics=["UnblendedCost"],
    )
    return ce_response
    
def get_region_names():
    """
    Retrieves the region names dictionary from AWS Systems Manager Parameter Store.

    Returns:
    - dict: The region names dictionary.
    """
    region_path = os.environ["region_names_path"]
    
    try:
        response = ssm_client.get_parameter(Name=region_path)
        region_names = json.loads(response["Parameter"]["Value"])
        return region_names
    except Exception as e:
        logging.error("Error retrieving region names from Parameter Store: " + str(e))
        raise

# Get the region names dictionary
region_names = get_region_names()


def cost_of_resources(event, resource_list, account_id):
    """
    Push metrics of cumulative cost under ownership of specific IAM User.
    Push metrics of total services cost for specific IAM User.
    Args:
        Resource List: IAM User's resource list.
        Account ID: AWS Account ID
    Returns:
        It pushes following metrics in grafana:
           - Total Services cost for specific IAM User in each AWS Region
           - List resources with cumulative cost under ownership of specific IAM User
    Raises:
        KeyError: Error in initializing Prometheus Registry and Gauge.
    """
    # Initialize the Prometheus registry and gauge
    try:
        registry = CollectorRegistry()
        # Creating gauge metrics for resource's cost for specific IAM User
        gauge = Gauge(
            "IAM_USER_Resource_Cost_List",
            "IAM User Resource List And Cost",
            labelnames=[
                "Query_Time",
                "user",
                "region",
                "resource",
                "cumulative_cost",
                "account_id",
            ],
            registry=registry,
        )
        # Creating gauge metrics for total services cost of IAM User
        g_user_cost = Gauge(
            "IAM_USER_Total_Services_Cost_List",
            "IAM User Total Services Cost List",
            labelnames=["Query_Time", "user", "region", "resources_cost", "account_id"],
            registry=registry,
        )

        for item in range(len(resource_list)):
            # Getting IAM User detail
            user = resource_list[item]["User"]
            region = resource_list[item]["Region"]
            resources = resource_list[item]["ResourceList"]
            # Initializing total_services cost
            user_region_wise_cost = 0.0

            for res in resources:
                cumulative_cost = 0.0
                if len(res) == 0:
                    continue
                elif "ec2" in res:
                    # getting instance ID
                    instance = res.split("/")[1]
                    # Calling Cost method
                    response = cost_of_instance(event, client, instance)
                    # Parsing result from cost method
                    for iterator in range(len(response["ResultsByTime"])):
                        cumulative_cost = cumulative_cost + float(
                            response["ResultsByTime"][iterator]["Total"][
                                "UnblendedCost"
                            ]["Amount"]
                        )
                        time_delta = response["ResultsByTime"][iterator]["TimePeriod"][
                            "End"
                        ]
                        metric_time = time_delta.replace("00:00:00", "12:02:02")
                    user_region_wise_cost = user_region_wise_cost + cumulative_cost
                    gauge.labels(
                        (datetime.strptime(metric_time, "%Y-%m-%dT%H:%M:%SZ")).strftime(
                            "%Y-%m-%d %H:%M:%S"
                        ),
                        user,
                        f"{region} ({region_names.get(region, 'unknown region name')})", 
                        res,
                        cumulative_cost,
                        account_id,
                    ).set(cumulative_cost)
                elif "lambda" in res:
                    lambda_service = res.split(":")[-1]
                    time_delta = response["ResultsByTime"][iterator]["TimePeriod"][
                        "End"
                    ]
                    logging.info(lambda_service)
                    metric_time = time_delta.replace("00:00:00", "12:02:02")
                    gauge.labels(
                        (datetime.strptime(metric_time, "%Y-%m-%dT%H:%M:%SZ")).strftime(
                            "%Y-%m-%d %H:%M:%S"
                        ),
                        user,
                        f"{region} ({region_names.get(region, 'unknown region name')})",
                        res,
                        "0",
                        account_id,
                    ).set(0)
            g_user_cost.labels(
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                user,
                f"{region} ({region_names.get(region, 'unknown region name')})",
                user_region_wise_cost,
                account_id,
            ).set(user_region_wise_cost)

        # Push the gauge data to Prometheus
        push_to_gateway(
            os.environ["prometheus_ip"],
            job="IAM_User_Resource_List_Cost_" + regionName,
            registry=registry,
        )
        push_to_gateway(
            os.environ["prometheus_ip"],
            job="IAM_User_Total_Services_Cost_List_" + regionName,
            registry=registry,
        )

    except Exception as e:
        raise ValueError(f"Failed to push cost data to Prometheus: {str(e)}")


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
    # Getting IAM User Detail from SNS Message Payload
    user_details = json.loads(event["Records"][0]["Sns"]["Message"])
    account_id = context.invoked_function_arn.split(":")[4]

    for iterator in range(len(user_details)):
        user = user_details[iterator]["UserName"]
        # creating subset list for resources under ownership of specific IAM User
        subset_list = []
        try:
            client = boto3.client("resourcegroupstaggingapi", region_name=regionName)
        except Exception as e:
            logging.error("Error in initiating boto3 client: " + str(e))
            return {"statusCode": 500, "body": json.dumps({"Error": str(e)})}
        # getting resource detail using Owner tag
        try:
            response = client.get_resources(
                TagFilters=[
                    {
                        "Key": "Owner",
                        "Values": [
                            user,
                        ],
                    },
                ]
            )
        except Exception as e:
            logging.error(
                "Error getting response from resourcegroupstaggingapi: " + str(e)
            )
            return {"statusCode": 500, "body": json.dumps({"Error": str(e)})}

        response_dict = json.dumps(response)
        parse_string = json.loads(response_dict)

        # parsing resource info
        dict_len = len(parse_string["ResourceTagMappingList"])
        if dict_len == 0:
            result_list = {"User": user, "ResourceList": [""], "Region": regionName}
            case_list.append(result_list)
        else:
            for item in parse_string["ResourceTagMappingList"]:
                subset = item["ResourceARN"].split(":")
                subset_len = len(subset)
                if subset_len == 6:
                    # adding service and resource id
                    resource = subset[2] + ":" + subset[5]
                    subset_list.append(resource)
                else:
                    # adding service and resource id
                    resource = subset[2] + ":" + subset[5] + ":" + subset[6]
                    subset_list.append(resource)
                # creating resource list for cost and usage api
            result_list = {
                "User": user,
                "ResourceList": subset_list,
                "Region": regionName,
            }
            case_list.append(result_list)
    # Calling method to get cost of resources
    cost_of_resources(event, case_list, account_id)

    return {"statusCode": 200, "body": json.dumps(case_list)}
