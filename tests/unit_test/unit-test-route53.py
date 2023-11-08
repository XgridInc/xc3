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
from moto import mock_route53
from config import ec2_instance_connect_endpoint, region, env

class TestRoute53(unittest.TestCase):
    """
    Unit tests for Route 53 DNS record creation.

    These tests validate the creation of a DNS record in Route 53 when the environment is 'prod'.
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
    @mock_route53
    def test_create_dns_record(self):
        """
        Test the creation of a DNS record in Route 53.

        This test creates a mock Route 53 client, a hosted zone, and a DNS record. It checks if the DNS record was created successfully.

        Raises:
            AssertionError: If the DNS record creation does not return an HTTP status code of 200.
        """
        # Create a mock Route 53 client
        route53_client = boto3.client('route53', region_name=region)

        # Create a hosted zone
        hosted_zone_name = 'xgrid.co'
        response = route53_client.create_hosted_zone(
            Name=hosted_zone_name,
            CallerReference='test-123'
        )
        hosted_zone_id = response['HostedZone']['Id']

        # Define DNS record details
        dns_name = 'xccc.xgrid.co'
        dns_type = 'A'
        dns_value = '192.168.1.1'  # Random DNS value for testing.

        # Create a DNS record
        dns_record_change = {
            'Changes': [
                {
                    'Action': 'CREATE',
                    'ResourceRecordSet': {
                        'Name': dns_name,
                        'Type': dns_type,
                        'TTL': 300,
                        'ResourceRecords': [{'Value': dns_value}]
                    }
                }
            ]
        }

        response = route53_client.change_resource_record_sets(
            HostedZoneId=hosted_zone_id,
            ChangeBatch=dns_record_change
        )


        # Check if the DNS record was created successfully
        self.assertEqual(response['ResponseMetadata']['HTTPStatusCode'], 200)

if __name__ == "__main__":
    unittest.main()
