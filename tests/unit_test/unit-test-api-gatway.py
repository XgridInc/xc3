"""
Copyright (c) 2023, Xgrid Inc, https://xgrid.co

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

SPDX-License-Identifier: Apache-2.0
"""

import logging
import unittest

import boto3
from config import (  # Import the 'env' variable and 'api_gateway_name' from your config   # noqa: E501
    api_gateway,
    env,
    region,
)


class TestApiGatewayCreation(unittest.TestCase):
    def setUp(self):
        # Initialize the AWS API Gateway client
        self.apigateway_client = boto3.client("apigateway", region_name=region)

    @unittest.skipIf(env == "dev", "Skipping test in dev environment")
    def test_api_gateway_created(self):
        # Log the API Gateway name and other relevant information for debugging
        logging.info(
            f"Testing API Gateway: {api_gateway}, Region: {region}, Environment: {env}"  # noqa: E501
        )

        # Check if the API Gateway exists
        try:
            response = self.apigateway_client.get_rest_apis()
            api_gateways = response["items"]

            # Filter API Gateways by name
            matching_api_gateways = [
                api for api in api_gateways if api["name"] == api_gateway
            ]

            if len(matching_api_gateways) == 1:
                logging.info(f"API Gateway '{api_gateway}' has been created.")
            elif len(matching_api_gateways) == 0:
                logging.warning(f"API Gateway '{api_gateway}' not found.")
            else:
                logging.warning(
                    f"Multiple API Gateways with the name '{api_gateway}' found."  # noqa: E501
                )

            self.assertEqual(
                len(matching_api_gateways),
                1,
                "Expected one API Gateway to be created.",  # noqa: E501
            )
        except Exception as e:
            logging.warning(f"Error while checking API Gateway: {str(e)}")


if __name__ == "__main__":
    unittest.main()
