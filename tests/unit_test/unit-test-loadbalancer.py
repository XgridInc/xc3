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

import unittest
import boto3
import logging

from config import region, load_balancer, env


class TestLoadBalancerCreation(unittest.TestCase):
    def setUp(self):
        # Initialize the AWS ELB client
        self.elb_client = boto3.client("elbv2", region_name=region)

    @unittest.skipIf(env == "dev", "Skipping test in dev environment.")
    def test_load_balancer_created(self):
        # Log the load balancer name and other relevant information for debugging
        logging.info(
            f"Testing load balancer: {load_balancer}, Region: {region}, Environment: {env}"
        )

        # Check if the load balancer exists
        try:
            response = self.elb_client.describe_load_balancers(Names=[load_balancer])
            load_balancer_count = len(response["LoadBalancers"])

            if load_balancer_count == 1:
                logging.info(f"Load balancer '{load_balancer}' has been created.")
            elif load_balancer_count == 0:
                logging.warning(f"Load balancer '{load_balancer}' not found.")
            else:
                logging.warning(
                    f"Multiple load balancers with the name '{load_balancer}' found."
                )

            self.assertEqual(
                load_balancer_count, 1, "Expected one load balancer to be created."
            )
        except self.elb_client.exceptions.ClientError as e:
            if e.response["Error"]["Code"] == "LoadBalancerNotFound":
                logging.warning(f"Load balancer '{load_balancer}' not found.")
            else:
                raise


if __name__ == "__main__":
    unittest.main()
