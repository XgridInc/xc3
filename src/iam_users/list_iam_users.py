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

import io
import gzip
import json
import boto3
import os
import logging
from prometheus_client import CollectorRegistry, Gauge, push_to_gateway
from urllib.parse import unquote_plus

try:
    s3 = boto3.client("s3")
except Exception as e:
    logging.error("Error creating boto3 client: " + str(e))
try:
    sns = boto3.client("sns")
except Exception as e:
    logging.error("Error creating boto3 client: " + str(e))

# Initializing environment variables
runtime_region = os.environ["REGION"]
topic_arn = os.environ["sns_topic"]


def lambda_handler(event, context):
    """
    List IAM User Details.
    Args:
        Account ID: AWS account id.
    Returns:
        It returns a list of IAM Users details in provided aws account.
    Raises:
        Lambda Invoke Error: Raise error if message doesn't publish in SNS topic
    """
    account_id = context.invoked_function_arn.split(":")[4]
    user_detail_data = []
    iam_user_detail = []
    # Getting IAM User Detail from S3 bucket
    bucket = event["Records"][0]["s3"]["bucket"]["name"]
    key = unquote_plus(event["Records"][0]["s3"]["object"]["key"])
    # parsing resource.json file
    if "resources" in key:
        try:
            response = s3.get_object(Bucket=bucket, Key=key)
            resource_file = response["Body"].read()
            with gzip.GzipFile(fileobj=io.BytesIO(resource_file), mode="rb") as data:
                user_detail_data = json.load(data)
        except Exception as e:
            logging.error(
                """
                Error getting object {} from bucket {}.
                Make sure bucket and function are in the same region.
                """.format(
                    key, bucket
                ),
                str(e),
            )
            return {"statusCode": 500, "body": json.dumps({"Error": str(e)})}
    logging.info(user_detail_data)
    if len(user_detail_data) == 0:
        return {"statusCode": 200, "body": json.dumps("IAM Users don't exist")}
    # Initialize the Prometheus registry and gauge
    else:
        try:
            registry = CollectorRegistry()
            g_user = Gauge(
                "IAM_Users",
                "IAM Users",
                labelnames=["user_name", "user_arn", "user_id", "account_id"],
                registry=registry,
            )
            for iterator in range(len(user_detail_data)):
                user_name = user_detail_data[iterator]["UserName"]
                user_arn = user_detail_data[iterator]["Arn"]
                user_id = user_detail_data[iterator]["UserId"]
                user_info = {
                    "UserName": user_name,
                    "UserArn": user_arn,
                    "UserId": user_id,
                }
                # Add the IAM User detail to the gauge
                g_user.labels(user_name, user_arn, user_id, account_id).set(0)
                iam_user_detail.append(user_info)
            # Push the gauge data to Prometheus
            push_to_gateway(
                os.environ["prometheus_ip"], job="IAM_User_Details", registry=registry
            )
        except Exception as e:
            logging.error("Error initializing Prometheus Registry and Gauge: " + str(e))
            return {"statusCode": 500, "body": json.dumps({"Error": str(e)})}
        # message for SNS Topic
        payload_data = iam_user_detail
        try:
            sns.publish(
                TopicArn=topic_arn,
                Message=json.dumps({"default": json.dumps(payload_data)}),
                MessageStructure="json",
            )
        except Exception as e:
            logging.error("Error in publish SNS message: " + str(e))
            return {"statusCode": 500, "body": json.dumps({"Error": str(e)})}

    return {"statusCode": 200, "body": json.dumps(iam_user_detail)}
