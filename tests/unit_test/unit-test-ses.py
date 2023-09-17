import unittest
import boto3
import logging
from moto import mock_ses
from config import region, ses_email

try:
    ses_client = boto3.client("ses", region_name=region)
except Exception as e:
    logging.error("Error creating SES client: " + str(e))


class TestEmailSender(unittest.TestCase):
    @mock_ses
    def test_send_email(self):
        ses_client.verify_email_identity(EmailAddress=ses_email)
        kwargs = dict(
            Source=ses_email,
            Destination={"ToAddresses": [ses_email]},
            Message={
                "Subject": {"Data": "test subject"},
                "Body": {"Html": {"Data": "test body"}},
            },
        )

        response = ses_client.send_email(**kwargs)
        self.assertEqual(response["ResponseMetadata"]["HTTPStatusCode"], 200)


if __name__ == "__main__":
    unittest.main()
