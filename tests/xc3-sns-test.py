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

import unittest
import boto3
from config import sns, sns_name, sns_arn


class TestSNSTopic(unittest.TestCase):
    def test_topic_name(self):
        """
        Unit test method for testing the name of an
        Amazon Simple Notification Service (SNS) topic.

        Parameters:
            - self: Instance of the TestSNSTopic class.

        Returns:
            - None

        Raises:
            - AssertionError: If the SNS topic does not exist or if the
            `get_topic_attributes` call returns None.

        Usage:
            - Call this method to test the name of an SNS topic.
            The method uses the `boto3` client library to get the attributes
            of the topic with the given ARN,
            and then asserts that the response is not None.
            If the topic does not exist or if the response is None,
            an AssertionError is raised.
        """

        sns_client = boto3.client("sns")
        try:
            response = sns_client.get_topic_attributes(TopicArn=sns)
            self.assertIsNotNone(response, f"Topic {sns_name} exists")
        except sns_client.exceptions.NotFoundException:
            self.fail(f"Topic {sns_name} does not exist")

    def test_subscription_exists(self):
        """
        Unit test method for testing the existence of an
        Amazon Simple Notification Service (SNS) subscription.

        Parameters:
            - self: Instance of the TestSNSTopic class.

        Returns:
            - None

        Raises:
            - AssertionError: If the SNS subscription does not exist or
            if the `get_subscription_attributes` call returns None.

        Usage:
            - Call this method to test the existence of an SNS subscription.
            The method uses the `boto3` client library to get the attributes of the
            subscription with the given ARN, and then asserts that
            the response is not None.
            If the subscription does not exist or if the response is None,
            an AssertionError is raised."""

        sns_client = boto3.client("sns")
        subscription_arn = sns_arn
        try:
            response = sns_client.get_subscription_attributes(
                SubscriptionArn=subscription_arn
            )
            self.assertIsNotNone(response, f"{sns_arn} already exists")
        except sns_client.exceptions.NotFoundException:
            self.fail(
                f"Subscription for {subscription_arn} does not exist for {sns_name}"
            )
