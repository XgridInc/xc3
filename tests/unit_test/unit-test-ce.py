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
from unittest.mock import patch, MagicMock
from config import region

def function_to_get_cost_and_usage():
    """
    This function retrieves cost and usage information from AWS Cost Explorer for Amazon S3 services.

    Returns:
        dict: A dictionary containing the total cost and currency, or None if no results are available.
    """
    ce_client = boto3.client('ce', region_name=region)  

    start_date = '2023-01-01'
    end_date = '2023-01-31'
    granularity = 'DAILY'
    metrics = ['UnblendedCost']
    
    filters = {
        'Dimensions': {
            'Key': 'SERVICE',
            'Values': ['Amazon S3']
        }
    }

    response = ce_client.get_cost_and_usage(
        TimePeriod={
            'Start': start_date,
            'End': end_date
        },
        Granularity=granularity,
        Metrics=metrics,
        Filter=filters
    )

    results = response['ResultsByTime']
    if results:
        total_cost = results[0]['Total']['UnblendedCost']['Amount']
        currency = results[0]['Total']['UnblendedCost']['Unit']
        
        return {'Total': float(total_cost), 'Currency': currency}
    else:
        return None

class TestCostExplorer(unittest.TestCase):
    """
    This class contains test cases for the `function_to_get_cost_and_usage` function.
    """
    @patch('boto3.client')
    def test_get_cost_and_usage(self, mock_boto3):
        """
        Test the `function_to_get_cost_and_usage` function with mock data.

        The function should return the expected cost and currency information.
        """
        # Mock the Boto3 client
        ce_mock = MagicMock()
        mock_boto3.return_value = ce_mock

        # Define the expected result
        expected_result = {'Total': 100.0, 'Currency': 'USD'}

        # Configure the mock's return value
        ce_mock.get_cost_and_usage.return_value = {
            'ResultsByTime': [
                {
                    'Total': {
                        'UnblendedCost': {'Amount': '100.0', 'Unit': 'USD'},
                    }
                }
            ]
        }

        # Call the function you want to test
        result = function_to_get_cost_and_usage()

        # Assert that the result matches the expected value
        self.assertEqual(result, expected_result)

if __name__ == '__main__':
    unittest.main()
