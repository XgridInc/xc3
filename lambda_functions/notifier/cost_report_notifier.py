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
from apprise import Apprise
import calendar
import os
import logging
import botocore

try:
    s3_client = boto3.client("s3")
except Exception as e:
    logging.error("Error creating boto3 client for s3: " + str(e))

try:
    # Set up the Apprise client
    apobj = Apprise()
    # Add the Slack webhook URL to the Apprise client
    apobj.add(os.environ["slack_channel_url"])
except Exception as e:
    logging.error("Error creating Agpprise client: " + str(e))


def send_notification_to_slack(title, body):
    """
    Sends a message to the Slack channel using Apprise.

    :param apobj: The Apprise object.
    :param title: The message title.
    :param body: The message body.
    """
    try:
        apobj.notify(body=body, title=title)
    except Exception as e:
        logging.error(f"Error sending notification to Slack: {e}")


def get_s3_object(bucket, key):
    """
    Retrieves an object from an S3 bucket and returns its contents
    as a Python dictionary.

    Args:
        bucket (str): The name of the S3 bucket.
        key (str): The key of the object to retrieve.

    Returns:
        dict: The contents of the object as a Python dictionary.

    Raises:
        botocore.exceptions.ClientError: If the specified object
        does not exist in the bucket.

    """
    try:
        s3_object = s3_client.get_object(Bucket=bucket, Key=key)
    except botocore.exceptions.ClientError as e:
        if e.response["Error"]["Code"] == "NoSuchKey":
            logging.error("The specified key does not exist in the bucket")
            return ""
        else:
            raise
    json_data = s3_object["Body"].read().decode("utf-8")

    # Convert the JSON data to a Python dictionary
    data_dict = json.loads(json_data)

    return data_dict


def get_accounts_cost():
    """
    Returns a table of account costs.

    :return: A table of account costs.

    Example:
    | Account Details                 | January | February | March   | April   |
    |---------------------------------|----------------------------------------|
    | Account ID - Name               |    0.00 |    0.00  |    1.47 |    0.10 |
    """
    try:
        data_dict = get_s3_object(
            os.environ["bucket_name"], os.environ["monthly_cost_prefix"]
        )

        # Get a list of all the months
        months = sorted(
            set(month for account in data_dict.values() for month in account.keys()),
            key=lambda x: list(calendar.month_abbr).index(x[:3]),
        )

        # Create a table of the data
        max_account_len = max(len(account) for account in data_dict.keys())
        max_cost_len = max(
            len(f"{cost:.2f}")
            for account in data_dict.values()
            for cost in account.values()
        )
        table_rows = []
        header_row = f"| {'Account Details'.ljust(max_account_len)} |"
        for month in months:
            header_row += f" {month.ljust(max_cost_len)} |"
        table_rows.append(header_row)
        table_rows.append(
            f"|{'-'*(max_account_len+2)}|{'-'*(max_cost_len+2)*len(months)}|"
        )
        for account, account_data in data_dict.items():
            account_row = f"| {account.ljust(max_account_len)} |"
            for month in months:
                account_row += (
                    f" {f'{account_data.get(month, 0):.2f}'.rjust(max_cost_len)} |"
                )
            table_rows.append(account_row)

        # Join the table rows into a string
        table = "\n".join(table_rows)
        return table
    except Exception as e:
        logging.error(f"Error getting account costs: {e}")
        return ""


def get_projects_cost():
    """
    Retrieves project costs from a JSON file stored in an S3 bucket and returns
    them as a formatted table string.

    Returns:
        str: A formatted table string of the project costs.

    Raises:
        ValueError: If the JSON data is not in the expected format or
                    contains invalid cost values.
        ClientError: If there is an error retrieving the JSON data from
                    the S3 bucket.

    Example:
    | Project                  |       Cost ($) |
    |--------------------------|----------------|
    | Project-Name             |         882.36 |
    """

    try:
        data_dict = get_s3_object(
            os.environ["bucket_name"], os.environ["project_spend_prefix"]
        )

        # Create a table of the data
        max_project_len = max(len(project) for project in data_dict.keys())
        max_cost_len = max(len(str(cost)) for cost in data_dict.values())
        table_rows = []
        table_rows.append(
            f"| {'Project'.ljust(max_project_len)} | {'Cost ($)'.rjust(max_cost_len)} |"
        )
        table_rows.append(f"|{'-'*(max_project_len+2)}|{'-'*(max_cost_len+2)}|")
        for project, cost in data_dict.items():
            try:
                cost = float(cost)
            except ValueError:
                raise ValueError("Invalid cost value in the JSON data.")
            table_rows.append(
                f"| {project.ljust(max_project_len)} "
                f"| {f'{cost:.2f}'.rjust(max_cost_len)} |"
            )

        # Join the table rows into a string
        table = "\n".join(table_rows)
        return table

    except botocore.exceptions.ClientError as e:
        raise e
    except Exception as e:
        raise ValueError("Error retrieving project costs from S3.") from e


def get_expensive_services():
    """
    Retrieve a list of expensive services from an S3 bucket, format the data as a table,
    and send the table as a Slack notification using Apprise.

    Raises:
        botocore.exceptions.NoCredentialsError: If AWS credentials are
                                                not properly configured.
        botocore.exceptions.ClientError: If an error occurs while
                                         accessing the S3 bucket.

    Example:

    |----------------|-------------------------------|---------------|
    | Region         | Service                       | Cost($)       |
    |----------------|-------------------------------|---------------|
    | ap-south-1     | AWS Global Accelerator        | 8.225         |
    """
    try:
        # Set the bucket name and key prefix
        bucket_name = os.environ["bucket_name"]
        key_prefix = os.environ["expensive_service_prefix"]

        # Retrieve the objects from the S3 bucket with the specified prefix
        response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=key_prefix)
        object_count = response.get("KeyCount", 0)

        if object_count == 0:
            print(f"No objects found in {bucket_name}/{key_prefix}.")
            return

        # Create a Markdown-formatted table of the data from each object
        table_list = []
        for obj in response["Contents"]:
            # Get the object key
            key = obj["Key"]

            # Parse the JSON data and create a table using the data
            data_list = get_s3_object(bucket_name, key)
            max_region_len = max(
                [len(str(data.get("Region", ""))) for data in data_list]
            )
            max_service_len = max(
                [len(str(data.get("Service", ""))) for data in data_list]
            )
            max_cost_len = max([len(str(data.get("Cost", ""))) for data in data_list])

            table_header = "| {:{}} | {:{}} | {:{}} |\n".format(
                "Region",
                max_region_len,
                "Service",
                max_service_len,
                "Cost($)",
                max_cost_len,
            )
            table_separator = "|{:-<{:}}|{:-<{:}}|{:-<{:}}|\n".format(
                "", max_region_len + 2, "", max_service_len + 2, "", max_cost_len + 2
            )
            table = f"{table_separator}{table_header}{table_separator}"
            for data in data_list:
                table += "| {:{}} | {:{}} | {:{}} |\n".format(
                    data.get("Region", ""),
                    max_region_len,
                    data.get("Service", ""),
                    max_service_len,
                    data.get("Cost", ""),
                    max_cost_len,
                )
            table += table_separator
            table_list.append((table, key.split("/")[-1].split(".")[0]))

        # Send the tables as Markdown-formatted messages to
        # the Slack channel using Apprise
        for table, object_name in table_list:
            send_notification_to_slack(
                f"Expensive Services Costs for {object_name}", f"```{table}```"
            )

    except botocore.exceptions.NoCredentialsError:
        logging.error("AWS credentials are not properly configured.")
        raise Exception("AWS credentials are not properly configured.")

    except botocore.exceptions.ClientError as e:
        logging.error(f"Error accessing S3 bucket: {e}")
        raise Exception(f"Error accessing S3 bucket: {e}")


def lambda_handler(event, context):
    """
    Lambda function to fetch and display AWS cost data and send it to a Slack channel.

    Args:
        event (dict): Lambda function event object.
        context (LambdaContext): Lambda function context object.

    Returns:
        Status Code and Response Body.

    Raises:
        Exception: If any error occurs while fetching and processing the cost data.

    """

    try:
        # Get the cost tables
        project_cost_table = get_projects_cost()
        account_cost_table = get_accounts_cost()
        get_expensive_services()

        # Send the cost tables to Slack
        send_notification_to_slack(
            "Monthly Cost of AWS Accounts($)", f"```{account_cost_table}```"
        )
        send_notification_to_slack(
            "Cost of Projects ($)", f"```{project_cost_table}```"
        )

    except Exception as e:
        raise Exception(
            f"Error occurred while fetching and processing cost data: {str(e)}"
        )
    return {
        "statusCode": 200,
        "body": json.dumps("Cost Reports have been sent to Slack"),
    }
