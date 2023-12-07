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
from moto import mock_sqs
from config import region, sqs_name

class TestSQSService(unittest.TestCase):
    """
    Unit tests for Amazon Simple Queue Service (SQS).

    These tests validate sending and receiving messages to and from an SQS queue, including error scenarios.
    """

    @mock_sqs
    def test_send_and_receive_message(self):
        """
        Test sending and receiving a message to/from an SQS queue, including error scenarios.

        This test creates a mock SQS client and a mock SQS queue, sends a message to the queue, and then receives the message.
        It checks if a message was received and if it matches the sent message. It also covers error scenarios such as
        sending a message to a non-existent queue and receiving a message from an empty queue.

        Raises:
            AssertionError: If any part of the test fails, including error scenarios.
        """
        # Create a mock SQS client
        sqs_client = boto3.client("sqs", region_name=region)

        # Create a mock SQS queue
        queue_name = sqs_name
        queue_url = sqs_client.create_queue(QueueName=queue_name)["QueueUrl"]

        # Test sending a message to a non-existent queue
        non_existent_queue_url = "https://sqs.us-east-1.amazonaws.com/123456789012/NonExistentQueue"
        with self.assertRaises(boto3.exceptions.botocore.exceptions.ClientError):
            sqs_client.send_message(QueueUrl=non_existent_queue_url, MessageBody="Test message to non-existent queue")

        # Send a message to the queue
        message_body = "Test message"
        sqs_client.send_message(QueueUrl=queue_url, MessageBody=message_body)

        # Receive a message from the empty queue
        empty_queue_url = sqs_client.create_queue(QueueName="EmptyQueue")["QueueUrl"]
        response = sqs_client.receive_message(QueueUrl=empty_queue_url, MaxNumberOfMessages=1)
        self.assertNotIn("Messages", response)

        # Receive a message from the queue
        response = sqs_client.receive_message(QueueUrl=queue_url, MaxNumberOfMessages=1)

        # Check if a message was received
        self.assertIn("Messages", response)
        self.assertEqual(len(response["Messages"]), 1)

        # Check if the received message matches the sent message
        received_message = response["Messages"][0]["Body"]
        self.assertEqual(received_message, message_body)

if __name__ == "__main__":
    unittest.main()
