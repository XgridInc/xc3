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
from config import cognito_id


def test_user_pool_exists():
    """
    Unit test method for testing the existence of a Cognito User Pool with the given ID.

    Parameters:
        - None

    Returns:
        - None

    Raises:
        - AssertionError: If the Cognito User Pool with the given ID does not exist.

    Usage:
        - Call this method to test the existence of a Cognito User Pool
        with the given ID.
        The method uses the Boto3 client to describe the User Pool with
        the provided ID,
        and then asserts that the response is not empty.
        If the User Pool does not exist,
        an AssertionError is raised.
    """

    userpool_client = boto3.client("cognito-idp")
    userpool_id = cognito_id

    try:
        response = userpool_client.describe_user_pool(UserPoolId=userpool_id)
        assert response is not None, f"User pool {userpool_id} exists"
    except userpool_client.exceptions.ResourceNotFoundException:
        assert False, f"User pool {userpool_id} does not exist"
