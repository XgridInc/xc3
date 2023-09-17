import unittest
import boto3
import logging
from moto import mock_sqs
from config import sqs_name, region, account_id


try:
    sqs_client = boto3.client("sqs", region_name=region)
except Exception as e:
    logging.error("Error creating SQS client: " + str(e))


class TestSQSResource(unittest.TestCase):
    @mock_sqs
    def test_create_queue(self):
        queue = sqs_client.create_queue(QueueName=sqs_name)

        self.assertEqual(
            queue["QueueUrl"],
            f"https://sqs.{region}.amazonaws.com/{account_id}/{sqs_name}",
        )


if __name__ == "__main__":
    unittest.main()
