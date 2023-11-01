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
        dns_value = '192.168.1.1'     #randome dns for testing.

        # Create a DNS record
        change_batch = {
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
            ChangeBatch=change_batch
        )

        # Check if the DNS record was created successfully
        self.assertEqual(response['ResponseMetadata']['HTTPStatusCode'], 200)

if __name__ == "__main__":
    unittest.main()
