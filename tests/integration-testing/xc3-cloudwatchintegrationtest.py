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

import boto3

from config import (functionmostexpensiveservice, functionprojectspendcost,
                    functiontotalaccountcost)


def test_cloudwatch_mostexpensiveservice():
    """
    Test function to verify the CloudWatch metrics for the most expensive service function.

    Raises:
        AssertionError: If the function name is not correct or if an exception occurs.
    """
    try:
        # Create a CloudWatch client
        cloudwatch_client = boto3.client('cloudwatch')
        # List CloudWatch metrics
        response = cloudwatch_client.list_metrics()

        value = None
        for metric in response['Metrics']:
            for dimension in metric['Dimensions']:
                if dimension['Name'] == 'FunctionName' and dimension['Value'] == functionmostexpensiveservice:
                    value = dimension['Value']
                    break

        assert value == functionmostexpensiveservice, f"Function name is correct: {value}"
    except Exception as e:
        assert False, f"Function name is not correct: {e}"

def test_cloudwatch_projectspendcost():
    """
    Test function to verify the CloudWatch metrics for project spend cost function.

    Raises:
        AssertionError: If the function name is not correct or if an exception occurs.
    """
    try:
        # Create a CloudWatch client
        cloudwatch_client = boto3.client('cloudwatch')
        # List CloudWatch metrics
        response = cloudwatch_client.list_metrics()

        value = None
        for metric in response['Metrics']:
            for dimension in metric['Dimensions']:
                if dimension['Name'] == 'FunctionName' and dimension['Value'] == functionprojectspendcost:
                    value = dimension['Value']
                    break

        assert value == functionprojectspendcost, f"Function name is correct: {value}"
    except Exception as e:
        
        assert False, f"Function name is not correct: {e}"