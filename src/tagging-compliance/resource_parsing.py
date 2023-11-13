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
import logging
import os
import re

from prometheus_client import CollectorRegistry, Gauge, push_to_gateway


def resource_arn_parsing(subset):
    """
    Parse resource arn.

    Args:
        subset: resource arn
    Returns:
        A subset of resource arn.
    Raises:
        ValueError: If there is a
        problem with the input data format.
    """
    try:
        pattern = (
            r"^arn:(?P<Partition>[^:]+):"
            r"(?P<Service>[^:]+):"
            r"(?P<Region>[^:]*):"
            r"(?P<AccountID>[^:]*):"
            r"(?P<ResourceType>[^:/]*[:/]?)?"
            r"(?P<Resource>.*)$"
        )
        match = re.match(pattern, subset)

        if match:
            service = match.group("Service")
            resource_type = match.group("ResourceType")
            resource = match.group("Resource")

            if resource_type:
                parsed_arn = "{0}:{1}{2}".format(service, resource_type, resource)
                return parsed_arn
            else:
                parsed_arn = "{0}:{1}".format(service, resource)
                return parsed_arn
        else:
            logging.error("Invalid ARN format")

    except ValueError as ve:
        raise ValueError(f"ValueError occurred: {ve}.\n Please check the ARN format.")


def lambda_handler(event, context):
    """
    Create dictionary of resources on which provided set of
    tags are missing in all AWS Region.
    Args: List resources in all AWS Regions
    Returns:
        dict: The list of resources on which provided tags are missing.
    """
    # Fetching event data
    lambda_detail = event
    resources_without_tags = []

    # List of Tags for filtering
    resources_without_tags = eval(os.environ["tagging_list"])
    account_id = os.environ["account_id"]

    try:
        registry = CollectorRegistry()
        resource_list_gauge = Gauge(
            "TaggingResourceList",
            "Resource List",
            labelnames=["resource", "region", "account_id"],
            registry=registry,
        )
    except Exception as e:
        logging.error("Error initializing Prometheus Registry and Gauge: " + str(e))
        return {"statusCode": 500, "body": json.dumps({"Error": str(e)})}
    for lambda_item in lambda_detail:
        subset_list = []
        for resource_item in lambda_item["ResourceList"]:
            # Check if the resource has any tags
            if len(resource_item["Tags"]) == 0:
                subset_value = resource_arn_parsing(resource_item["ResourceARN"])
                subset_list.append(subset_value)
            else:
                # Check if the resource has all the required tags
                if all(
                    tag["Key"] not in resources_without_tags
                    for tag in resource_item["Tags"]
                ):
                    subset_value = resource_arn_parsing(resource_item["ResourceARN"])
                    subset_list.append(subset_value)
        # Push resource list to Prometheus metric
        for resource in subset_list:
            resource_list_gauge.labels(resource, lambda_item["Region"], account_id).set(
                0
            )
    push_to_gateway(
        os.environ["prometheus_ip"], job="TaggingResourceList", registry=registry
    )

    return {"statusCode": 200, "body": "success"}
#EOF