import os
import re
import gzip
from urllib.parse import unquote_plus
import boto3
import logging
import json
import io
from prometheus_client import CollectorRegistry, Gauge, push_to_gateway


try:
    s3 = boto3.client("s3")
except Exception as e:
    logging.error("Error creating boto3 client: " + str(e))


def lambda_handler(event, context):
    """
    Lambda handler function that extracts IAM role information and pushes it to Prometheus.

    Parameters:
    - event (dict): The event payload containing the list of roles from s3 bucket.
    - context (object): The context object that provides information about the runtime environment.

    Returns:
    - dict: The response with a status code of 200 and a message body of "IAM Roles".
    """

    registry = CollectorRegistry()
    g = Gauge(
        "IAM_Role_All",
        "XCCC All IAM Roles",
        labelnames=["iam_role_all", "iam_role_all_region", "iam_role_all_account"],
        registry=registry,
    )

    roles = []
    bucket = event["Records"][0]["s3"]["bucket"]["name"]
    key = unquote_plus(event["Records"][0]["s3"]["object"]["key"])
    if "resources" in key:
        try:
            response = s3.get_object(Bucket=bucket, Key=key)
            resource_file = response["Body"].read()
            with gzip.GzipFile(fileobj=io.BytesIO(resource_file), mode="rb") as data:
                roles = json.load(data)
        except Exception as e:
            logging.error(
                "Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.".format(
                    key, bucket
                ),
                str(e),
            )
            return {"statusCode": 500, "body": json.dumps({"Error": str(e)})}
    logging.info(roles)

    for role in roles:
        arn = role["Arn"]
        role_name = role["RoleName"]
        region = role["RoleLastUsed"].get("Region", "None")
        account_id = re.search(r"(?<=:)\d+", arn).group()
        g.labels(role_name, region, account_id).set(0)

    push_to_gateway(os.environ["prometheus_ip"], job="IAM-roles-all", registry=registry)
    return {"statusCode": 200, "body": "IAM Roles"}
