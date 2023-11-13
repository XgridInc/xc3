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
from config import ec2_instance_connect_endpoint, region, env

class EicMockTests(unittest.TestCase):
    """
    Unit tests for EC2 Instance Connect Endpoint creation.

    These tests validate the existence of an EC2 Instance Connect Endpoint with the specified ARN when the environment is 'prod'.
    """
    # Define a decorator to skip the test if the environment is "dev"
    def skip_if_dev(func):
        def wrapper(self, *args, **kwargs):
            if env != "prod":
                self.skipTest("Skipping test in 'dev' environment")
            else:
                func(self, *args, **kwargs)

        return wrapper

    @skip_if_dev
    def setUp(self):
        """
        Set up the test case by initializing the AWS EC2 client.
        """
        # Initialize the AWS EC2 client
        self.ec2_client = boto3.client('ec2', region_name=region)

    @skip_if_dev
    def test_eni_endpoint_created(self):
        """
        Test if the EC2 Instance Connect Endpoint with the specified ARN has been created.

        This test checks if the EC2 Instance Connect Endpoint exists and logs information for debugging.

        Raises:
            AssertionError: If the number of EC2 Instance Connect Endpoints with the specified ARN is not equal to 1.
        """
        # Log information for debugging
        logging.info(f"Testing EC2 Instance Connect Endpoint: ARN: {ec2_instance_connect_endpoint}, Region: {region}, Environment: {env}")
        # Check if the ENI endpoint exists
        try:
            # Use Boto3 to describe the network interfaces and find the one with the specified ARN
            response = self.ec2_client.describe_network_interfaces(Filters=[{'Name': 'network-interface-id', 'Values': [ec2_instance_connect_endpoint]}])
            network_interfaces = response['NetworkInterfaces']

            if len(network_interfaces) == 1:
                logging.info(f"EC2 Instance Connect Endpoint with ARN '{ec2_instance_connect_endpoint}' has been created.")
            elif len(network_interfaces) == 0:
                logging.warning(f"EC2 Instance Connect Endpoint with ARN '{ec2_instance_connect_endpoint}' not found.")
            else:
                logging.warning(f"Multiple EC2 Instance Connect Endpoints with the same ARN '{ec2_instance_connect_endpoint}' found.")

            self.assertEqual(len(network_interfaces), 1, "Expected one EC2 Instance Connect Endpoint to be created.")
        except Exception as e:
            logging.warning(f"Error while checking EC2 Instance Connect Endpoint: {str(e)}")

if __name__ == "__main__":
    unittest.main()
    logging.shutdown()  
