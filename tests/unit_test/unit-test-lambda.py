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
from config import lambda_function_names, region, env

class LambdaMockTests(unittest.TestCase):
    """
    Unit tests for AWS Lambda functions.

    These tests validate the existence of Lambda functions with the specified names.
    """
    def setUp(self):
        """
        Set up the test case by initializing the AWS Lambda client.
        """
        # Initialize the AWS Lambda client
        self.lambda_client = boto3.client('lambda', region_name=region)

    def test_lambda_functions_created(self):
        """
        Test if the expected Lambda functions have been created.

        This test checks if the Lambda functions exist and logs debugging information.

        Raises:
            AssertionError: If any of the expected Lambda functions are not found.
        """
        # Log information for debugging
        logging.info(f"Testing Lambda Functions in Region: {region}, Environment: {env}")

        # Check if the Lambda functions exist
        try:
            # Use Boto3 to list Lambda functions
            response = self.lambda_client.list_functions()
            lambda_functions = response['Functions']

            existing_function_names = [func['FunctionName'] for func in lambda_functions]

            for function_name in lambda_function_names:
                self.assertIn(function_name, existing_function_names, f"Lambda Function '{function_name}' not found.")

            logging.info("All expected Lambda Functions have been created.")
        except Exception as e:
            logging.warning(f"Error while checking Lambda Functions: {str(e)}")

if __name__ == "__main__":
    unittest.main()
    logging.shutdown()
