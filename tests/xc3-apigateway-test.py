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
from botocore.exceptions import ClientError
from config import restapiID

"""
    Unit test method for testing the existence of an API Gateway REST API with the given
    ID.

    Parameters:
        - None

    Returns:
        - None

    Raises:
        - AssertionError: If the REST API with the given ID does not exist, or if there
        is an error while fetching the API information.

    Usage:
        - Call this method to test the existence of an API Gateway REST API
        with the given ID.
        The method uses the Boto3 client to fetch the REST API information,
        and then asserts that the response is not empty and that the
        REST API ID matches the expected ID.
        If the REST API does not exist or if there is an error while
        fetching the API information, an AssertionError is raised.
    """


def test_get_rest_api():
    # Create a Boto3 client for API Gateway
    apigateway_client = boto3.client("apigateway")

    try:
        # Use the API Gateway client to get the REST API information
        rest_api_list = apigateway_client.get_rest_api(restApiId=restapiID)

        # Check that the REST API list is not empty
        assert len(rest_api_list) > 0

        # Check that the REST API name in the output matches the expected name
        assert rest_api_list["id"] == restapiID, f"{rest_api_list} exists"

    except ClientError as e:
        assert False, f"Error: {e}"
