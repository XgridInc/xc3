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

import ast
import json
import logging
import os
from datetime import date, datetime, timedelta

import boto3
from prometheus_client import CollectorRegistry, Gauge, push_to_gateway

# Initialize boto3 client
try:
    client = boto3.client("ce")
    client_ssm = boto3.client("ssm")
except Exception as e:
    logging.error("Error creating boto3 client: " + str(e))


def cost_of_account(client, account_id, start_date, end_date):
    """
    Retrieves the unblended cost of a given account within a specified
    time period using the AWS Cost Explorer API.

    Args:
        client: A boto3.client object for the AWS Cost Explorer API.
        account_id: A string representing the AWS account ID to retrieve cost data for.
        start_date: A string representing the start date of the time
        period to retrieve cost data for in YYYY-MM-DD format.
        end_date: A string representing the end date of the time
        period to retrieve cost data for in YYYY-MM-DD format.

    Returns:
        A dictionary representing the response from the AWS Cost
        Explorer API, containing the unblended cost of the specified
         account for the specified time period.
    Raises:
        ValueError: If there is a problem with the input data format,
         or if the calculation fails.
    """
    try:
        response = client.get_cost_and_usage(
            TimePeriod={"Start": start_date, "End": end_date},
            Granularity="MONTHLY",
            Filter={
                "And": [
                    {
                        "Dimensions": {
                            "Key": "LINKED_ACCOUNT",
                            "Values": [account_id],
                        },
                    },
                    {
                        "Not": {
                            "CostCategories": {
                                "Key": "ChargeType",
                                "Values": ["Credit", "Refund"],
                            }
                        }
                    },
                ]
            },
            Metrics=["UnblendedCost"],
            GroupBy=[
                {"Type": "DIMENSION", "Key": "LINKED_ACCOUNT"},
            ],
        )

        return response
    except ValueError as ve:
        raise ValueError(
            f"ValueError occurred: {ve}.\nPlease check the input data format and try again."
        )
    except Exception as e:
        raise ValueError(
            f"An error occurred: {e}. Please check the input data and try again."
        )


def create_monthly_dict(json_data):
    """
    Converts AWS Cost Explorer API response data from a list
    of monthly cost data to a dictionary of monthly totals.

    Args:
        json_data: A dictionary representing the response
        data from the AWS Cost Explorer API.

    Returns:
        A dictionary where the keys are the names of the months
         in the input data (e.g. 'January', 'February', etc.),
         and the values are the total unblended cost for that month,
         calculated from the input data.
    Raises:
        KeyError: If the expected keys are not present in the input dictionary.
        ValueError: If there is a problem with the input data format,
         or if the calculation fails.
    """
    try:
        monthly_dict = {}
        for result in json_data["ResultsByTime"]:
            start_date_str = result["TimePeriod"]["Start"]
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
            month_name = start_date.strftime("%B")
            if (len(result["Groups"])) == 0:
                amount = float(result["Total"]["UnblendedCost"]["Amount"])
            else:
                amount = float(
                    result["Groups"][0]["Metrics"]["UnblendedCost"]["Amount"]
                )
            if month_name in monthly_dict:
                monthly_dict[month_name] += amount
            else:
                monthly_dict[month_name] = amount
    except KeyError as ke:
        raise KeyError(
            f"KeyError occurred: {ke}. Please check the format of the input dictionary."
        )
    except ValueError as ve:
        raise ValueError(
            f"ValueError occurred: {ve}.\nPlease check the input data format and try again."
        )
    except Exception as e:
        raise ValueError(
            f"An error occurred: {e}.\nPlease check the input data and try again."
        )
    return monthly_dict


def days_passed_in_current_year():
    """
    Returns the number of days passed in the current year.
    """
    today = date.today()
    first_day_of_year = date(today.year, 1, 1)
    days_passed = (today - first_day_of_year).days
    return days_passed


def lambda_handler(event, context):
    """
    Lambda function that collects and pushes cost data to Prometheus.

    :param event: The event that triggered the Lambda function.
                Expects an account ID in the form of a dictionary.
    :param context: The context of the Lambda function. Not used in this function.
    """
    account_detail = []
    # Collect cost data for the past 90 days
    cost_by_days = days_passed_in_current_year()
    end_date = str(datetime.now().date())
    start_date = str(datetime.now().date() - timedelta(days=cost_by_days))

    # Push cost data to Prometheus
    registry = CollectorRegistry()
    g = Gauge(
        "Total_Account_Cost",
        "Cost by month",
        ["month", "cost", "account_id"],
        registry=registry,
    )

    # Retrieve account ID from ssm
    parameter_name = os.environ["account_detail"] + "/account_details"

    try:
        response = client_ssm.get_parameter(Name=parameter_name, WithDecryption=True)
        parameter_value = response["Parameter"]["Value"]
        # Converting SSM ListString to List
        account_details = ast.literal_eval(parameter_value)
    except ValueError as ve:
        raise ValueError(
            f"ValueError occurred: {ve}.\nPlease check the input data format and try again."
        )
    except Exception as e:
        raise ValueError(
            f"An error occurred: {e}. Please check the input data and try again."
        )

    for account_detail in account_details:

        account_id = account_detail.split("-")[0]

        # Check that the account ID has 12 digits
        if len(account_id) != 12 or not account_id.isdigit():
            raise ValueError("Invalid AWS account ID")

        # Getting cost details of specific account
        response = cost_of_account(client, account_id, start_date, end_date)
        monthly_dict = create_monthly_dict(response)

        for month, cost in monthly_dict.items():
            if cost >= 0:
                g.labels(month, cost, account_detail).set(cost)
            else:
                g.labels(month, 0, account_detail).set(0)

    try:
        push_to_gateway(
            os.environ["prometheus_ip"], job="Total_Account_Cost", registry=registry
        )
    except Exception as e:
        raise ValueError(f"Failed to push cost data to Prometheus: {str(e)}")

    return {"statusCode": 200, "body": json.dumps(response)}
