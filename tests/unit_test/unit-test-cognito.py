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

import logging
import random
import string
import unittest

import boto3
from config import cognito, region
from moto import mock_cognitoidp


class CognitoMockTests(unittest.TestCase):
    @mock_cognitoidp
    def test_create_user_and_verify_attributes(self):
        region_name = region

        # Create a user pool
        user_pool_name = cognito
        user_pool_id = self.create_user_pool(user_pool_name, region_name)

        # Create a user
        username = "".join(
            random.choice(string.ascii_lowercase + string.digits) for _ in range(8)
        )
        email = (
            "".join(
                random.choice(string.ascii_lowercase + string.digits) for _ in range(8)
            )
            + "@example.com"
        )
        temporary_password = "".join(
            random.choice(string.ascii_letters + string.digits + string.punctuation)
            for _ in range(10)
        )
        self.create_user(user_pool_id, username, temporary_password, email)

        # Verify user attributes
        email_verified = self.get_user_attributes(user_pool_id, username)
        logging.info("Verified Email: %s", email_verified)

        # Assert the user attributes
        self.assertTrue(email_verified)

    def create_user_pool(self, user_pool_name, region_name):
        cognito_client = boto3.client("cognito-idp", region_name=region_name)
        user_pool_response = cognito_client.create_user_pool(
            PoolName=user_pool_name,
            Policies={
                "PasswordPolicy": {
                    "MinimumLength": 8,
                    "RequireLowercase": False,
                    "RequireNumbers": False,
                    "RequireSymbols": False,
                    "RequireUppercase": False,
                }
            },
            AutoVerifiedAttributes=["email"],
        )
        return user_pool_response["UserPool"]["Id"]

    def create_user(self, user_pool_id, username, temporary_password, email):
        cognito_client = boto3.client("cognito-idp", region_name=region)
        cognito_client.admin_create_user(
            UserPoolId=user_pool_id,
            Username=username,
            TemporaryPassword=temporary_password,
            UserAttributes=[
                {"Name": "email", "Value": email},
            ],
        )

    def get_user_attributes(self, user_pool_id, username):
        cognito_client = boto3.client("cognito-idp", region_name=region)
        user_response = cognito_client.admin_get_user(
            UserPoolId=user_pool_id, Username=username
        )
        user_attributes = user_response["UserAttributes"]
        email_verified = False

        for attribute in user_attributes:
            if attribute["Name"] == "email":
                email_verified = True

        return email_verified


if __name__ == "__main__":
    unittest.main()
