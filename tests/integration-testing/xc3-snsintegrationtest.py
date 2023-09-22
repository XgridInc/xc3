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

from config import functionlistiamuserresourcescost, region, sns_arn


def test_sns_lambdaendpoint():
    """
    Test function to check if the endpoint of an SNS topic subscription matches the specified Lambda function.

    This function uses the AWS SDK for Python (Boto3) to connect to the AWS SNS service and retrieve the
    subscriptions for the SNS topic specified in the 'sns_arn' variable. It then extracts the 'Endpoint' 
    from the response, which should be the ARN of the Lambda function. The function compares the obtained 
    'endpoint' with the value in the 'functionlistiamuserresourcescost' variable to check if they match. 

    If the 'endpoint' matches the Lambda function ARN, the test is considered successful. Otherwise, an
    exception is raised with an error message indicating the mismatch.

    Raises:
        AssertionError: If the endpoint does not match the Lambda function ARN or if any other exception
                       occurs during the execution of the test.
    """
    try:
        region_name = region

        # Create an SNS client
        sns_client = boto3.client('sns', region_name=region_name)

        # List subscriptions by topic
        response = sns_client.list_subscriptions_by_topic(TopicArn=sns_arn)

        # Extract Endpoint from the above response
        endpoint = response['Subscriptions'][0]['Endpoint']

        assert endpoint == functionlistiamuserresourcescost, f"Endpoint is correct: {endpoint}"
    
    except Exception as e:
        
        assert False, f"Endpoint is not correct: {e}"