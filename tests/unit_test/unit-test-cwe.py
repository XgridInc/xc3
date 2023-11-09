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
import unittest

import boto3
from config import (
    cloudwatch_list_linked_account,
    cloudwatch_list_linked_account_cron,
    cloudwatch_list_linked_account_description,
    cloudwatch_most_expensive_services,
    cloudwatch_most_expensive_services_cron,
    cloudwatch_most_expensive_services_description,
    cloudwatch_project_spend_cost,
    cloudwatch_project_spend_cost_cron,
    cloudwatch_project_spend_cost_description,
    cloudwatch_resource_list,
    cloudwatch_resource_list_cron,
    cloudwatch_resource_list_description,
    region,
)
from moto import mock_events

try:
    events_client = boto3.client("events", region_name=region)
except Exception as e:
    logging.error("Error creating events client: " + str(e))


class CloudWatchEventMockTests(unittest.TestCase):
    @mock_events
    def test_create_cloudwatch_events(self):
        # Create a CloudWatch Event rule
        rule_data = [
            {
                "name": cloudwatch_list_linked_account,
                "description": cloudwatch_list_linked_account_description,
                "cron_expression": cloudwatch_list_linked_account_cron,
            },
            {
                "name": cloudwatch_most_expensive_services,
                "description": cloudwatch_most_expensive_services_description,
                "cron_expression": cloudwatch_most_expensive_services_cron,
            },
            {
                "name": cloudwatch_project_spend_cost,
                "description": cloudwatch_project_spend_cost_description,
                "cron_expression": cloudwatch_project_spend_cost_cron,
            },
            {
                "name": cloudwatch_resource_list,
                "description": cloudwatch_resource_list_description,
                "cron_expression": cloudwatch_resource_list_cron,
            },
        ]

        for rule in rule_data:
            rule_name = rule["name"]
            rule_description = rule["description"]
            rule_schedule_expression = rule["cron_expression"]
            response = events_client.put_rule(
                Name=rule_name,
                ScheduleExpression=rule_schedule_expression,
                State="ENABLED",
                Description=rule_description,
            )

            # Verify the rule was created
            self.assertEqual(response["ResponseMetadata"]["HTTPStatusCode"], 200)

            # Describe the CloudWatch Event rule
            response = events_client.describe_rule(Name=rule_name)

            # Verify the rule attributes
            self.assertEqual(response["Name"], rule_name)
            self.assertEqual(response["State"], "ENABLED")
            self.assertEqual(response["Description"], rule_description)
            self.assertEqual(response["ScheduleExpression"], rule_schedule_expression)


if __name__ == "__main__":
    unittest.main()
