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

import gzip
import io
import json
import logging
import os
from datetime import datetime, timedelta
from dateutil import relativedelta

import boto3
from prometheus_client import CollectorRegistry, Gauge, push_to_gateway
import pandas as pd

try:
    s3 = boto3.client("s3")
except Exception as e:
    logging.error("Error creating boto3 client: " + str(e))
try:
    client = boto3.client("ce")
except Exception as e:
    logging.error("Error creating boto3 client: " + str(e))
try:
    lambda_client = boto3.client("lambda")
except Exception as e:
    logging.error("Error creating boto3 client: " + str(e))
try:
    ec2_client = boto3.client("ec2")
except Exception as e:
    logging.error("Error creating boto3 client: " + str(e))
try:
    ssm_client = boto3.client("ssm")
except Exception as e:
    logging.error("Error creating boto3 client for ssm:" + str(e))


def cost_of_instance(event, client, resource_id, start_date, end_date):
    """
    Fetches the cost and usage information for a given resource
    ID within a specified time period.

    Args:
        client: The boto3 client to use for the AWS Cost Explorer API.
        resource_id (str): The ID of the resource to fetch cost
        information for.
        start_date (str): The start date of the time period to fetch
        cost information for, in 'YYYY-MM-DD' format.
        end_date (str): The end date of the time period to fetch
        cost information for, in 'YYYY-MM-DD' format.

    Returns:
        The response from the AWS Cost Explorer API in JSON format.
    """
    response = client.get_cost_and_usage_with_resources(
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
    return response
    
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


def get_cur_data():
    bucket = os.environ["report_bucket_name"]

    current_date = datetime.now()
    start_date_str = f"{current_date.strftime('%Y%m')}01"
    end_date = datetime.strptime(start_date_str, "%Y%m%d") + relativedelta.relativedelta(months=1)
    end_date_str = f"{end_date.strftime('%Y%m')}01"
    full_date_range = f"{start_date_str}-{end_date_str}"

    key = f"report/reportbucket/{full_date_range}/reportbucket-00001.csv.gz"
    try:
        response = s3.get_object(Bucket=bucket, Key=key)
        resource_file = response["Body"].read()
        cur_data = {}
        with gzip.GzipFile(fileobj=io.BytesIO(resource_file), mode="rb") as data:
            cur_data = pd.read_csv(io.BytesIO(data.read()))
            cur_data = cur_data[[
                "product/ProductName",
                "lineItem/ResourceId",
                "lineItem/UnblendedCost",
            ]]
            return cur_data.to_json(orient='records')
    except Exception as e:
        logging.error(
            "Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.".format(
                key, bucket
            )
        )
        return {"statusCode": 500, "body": json.dumps({"Error": str(e)})}

# Get the cost and usage report data
cur_data = get_cur_data()

def get_cumulative_cost(resource_id):
    """
    Fetches the cost for a given resource ID from the Cost and Usage Report.

    Args:
        resource_id (str): The ID of the resource to fetch the cost for.

    Returns:
        The cumulative cost of the resource in the Cost and Usage Report.
    """
    df = pd.json_normalize(json.loads(cur_data))
    cost = df.loc[df["lineItem/ResourceId"] == resource_id].sum()["lineItem/UnblendedCost"]
    return cost

def lambda_handler(event, context):
    """
    The main Lambda function that is executed.

    Args:
        event: The input event that triggered the Lambda function.
        context: The context object for the Lambda function.

    Returns:
        A dictionary containing a status code and a message indicating
        that the function has completed.
    """

    registry = CollectorRegistry()

    iam_service_gauge = Gauge(
        "IAM_Role_Service",
        "XC3 IAM Role Info Data",
        labelnames=[
            "TimeSlot",
            "iam_role_of_service",
            "iam_role_service_region",
            "iam_role_service_account",
            "iam_role_service_resource_id",
            "iam_role_service_cost",
            "iam_role_service_state",
        ],
        registry=registry,
    )

    roles = event
    cost_by_days = 14
    end_date = str(datetime.now().date())
    start_date = str(datetime.now().date() - timedelta(days=cost_by_days))
    account_id = context.invoked_function_arn.split(":")[4]
    
    new_time = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    
    for i in range(len(roles)):
        arn = roles[i]["Role"]
        role = arn.rsplit("/", 1)[-1]
        role_region = roles[i]["Role_Region"]
        if role_region == "None":
            continue
        else:
            service_details = roles[i]["Service Details"]

            if len(service_details) == 0:
                response = cost_of_instance(event, client, "None", start_date, end_date)
                cumulative = 0.0
                for j in range(len(response["ResultsByTime"])):
                    time_Data = response["ResultsByTime"][j]["TimePeriod"]["End"]
                    new_time = time_Data.replace("00:00:00", "12:02:02")
                    cumulative = cumulative + float(
                        response["ResultsByTime"][j]["Total"]["UnblendedCost"]["Amount"]
                    )
                iam_service_gauge.labels(
                    (datetime.strptime(new_time, "%Y-%m-%dT%H:%M:%SZ")).strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),
                    role,
                    role_region,
                    account_id,
                    "None",
                    "0",
                    "Start",
                ).set(0)

            for detail in service_details:

                # check if detail is a dictionary
                if isinstance(detail, dict):
                    if detail["Service"] == "ec2":
                        # extract the "Instance_Region" and "Instance" fields
                        instance_region = detail["Instance_Region"]
                        instance = detail["Instance"]
                        ec2 = "ec2:instance/" + instance
                        response = cost_of_instance(
                            event, client, instance, start_date, end_date
                        )

                        ec2_resource = boto3.resource("ec2", region_name=instance_region)
                        state = ec2_resource.Instance(instance).state["Name"]

                        if state != "terminated":
                            if state == "running":

                                cumulative = 0.0
                                for j in range(len(response["ResultsByTime"])):
                                    time_Data = response["ResultsByTime"][j]["TimePeriod"][
                                        "End"
                                    ]
                                    new_time = time_Data.replace("00:00:00", "12:02:02")
                                    cumulative = cumulative + float(
                                        response["ResultsByTime"][j]["Total"][
                                            "UnblendedCost"
                                        ]["Amount"]
                                    )

                                    iam_service_gauge.labels(
                                        (
                                            datetime.strptime(
                                                new_time, "%Y-%m-%dT%H:%M:%SZ"
                                            )
                                        ).strftime("%Y-%m-%d %H:%M:%S"),
                                        role,
                                        f"{role_region} ({region_names.get(role_region, 'unknown region name')})",
                                        account_id,
                                        ec2,
                                        cumulative,
                                        "Stop",
                                    ).set(cumulative)
                            elif state == "stopped":
                                cumulative = 0.0
                                for j in range(len(response["ResultsByTime"])):
                                    time_Data = response["ResultsByTime"][j]["TimePeriod"][
                                        "End"
                                    ]
                                    new_time = time_Data.replace("00:00:00", "12:02:02")
                                    cumulative = cumulative + float(
                                        response["ResultsByTime"][j]["Total"][
                                            "UnblendedCost"
                                        ]["Amount"]
                                    )

                                    iam_service_gauge.labels(
                                        (
                                            datetime.strptime(
                                                new_time, "%Y-%m-%dT%H:%M:%SZ"
                                            )
                                        ).strftime("%Y-%m-%d %H:%M:%S"),
                                        role,
                                        f"{role_region} ({region_names.get(role_region, 'unknown region name')})",
                                        account_id,
                                        ec2,
                                        cumulative,
                                        "Start",
                                    ).set(cumulative)
                        else:
                            continue
                        
                    elif detail["Service"] == "lambda":
                        # extract the "Function" field
                        function = detail["Function"]
                        lambda_function = "lambda:function/" + function
                        lambda_cost = get_cumulative_cost(function)

                        iam_service_gauge.labels(
                            (
                                datetime.strptime(
                                    new_time, "%Y-%m-%dT%H:%M:%SZ"
                                )
                            ).strftime("%Y-%m-%d %H:%M:%S"),
                            role,
                            f"{role_region} ({region_names.get(role_region, 'unknown region name')})",
                            account_id,
                            lambda_function,
                            lambda_cost,
                            "None",
                        ).set(lambda_cost)

                elif isinstance(detail, str):
                    iam_service_gauge.labels(
                        (datetime.strptime(new_time, "%Y-%m-%dT%H:%M:%SZ")).strftime(
                            "%Y-%m-%d %H:%M:%S"
                        ),
                        role,
                        f"{role_region} ({region_names.get(role_region, 'unknown region name')})",
                        account_id,
                        detail,
                        "0",
                        "Start",
                    ).set(0)

    push_to_gateway(
        os.environ["prometheus_ip"], job="IAM-roles-service-data", registry=registry
    )

    return {"statusCode": 200, "body": json.dumps("Service Lambda Data Pushed")}
#EOF