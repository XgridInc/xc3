import unittest
import boto3
import logging
from moto import mock_sns
from config import region, sns_topic_name


try:
    sns_client = boto3.client("sns", region_name=region)
except Exception as e:
    logging.error("Error creating SNS client: " + str(e))


class TestSNSService(unittest.TestCase):
    @mock_sns
    def test_publish_message_to_topic(self):
        # Create a mock SNS topic
        topic_response = sns_client.create_topic(Name=sns_topic_name)
        topic_arn = topic_response["TopicArn"]

        # Publish a message to the topic
        message = "Hello, world!"
        sns_client.publish(TopicArn=topic_arn, Message=message)

        # Retrieve the published messages from the topic
        topic_attributes = sns_client.get_topic_attributes(TopicArn=topic_arn)
        self.assertIn("SubscriptionsPending", topic_attributes["Attributes"])
        self.assertEqual(int(topic_attributes["Attributes"]["SubscriptionsPending"]), 0)

        # List topic subscriptions
        subscriptions = sns_client.list_subscriptions_by_topic(TopicArn=topic_arn)
        self.assertEqual(len(subscriptions["Subscriptions"]), 0)


if __name__ == "__main__":
    unittest.main()
