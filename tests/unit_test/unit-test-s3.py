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
from config import region, s3_bucket, s3_bucket_tags
from moto import mock_s3

try:
    s3_client = boto3.client("s3")
except Exception as e:
    logging.error("Error creating S3 client: " + str(e))


class S3MockTests(unittest.TestCase):
    @mock_s3
    def test_create_bucket(self):
        bucket_name = s3_bucket

        s3_client.create_bucket(
            Bucket=bucket_name,
            CreateBucketConfiguration={"LocationConstraint": region},
        )
        logging.info("Bucket created successfully: %s", bucket_name)

        response = s3_client.list_buckets()
        buckets = response["Buckets"]
        self.assertEqual(len(buckets), 1)
        self.assertEqual(buckets[0]["Name"], bucket_name)

    @mock_s3
    def test_check_bucket_tags(self):
        bucket_name = s3_bucket

        s3_client.create_bucket(
            Bucket=bucket_name,
            CreateBucketConfiguration={"LocationConstraint": region},
        )

        tags = s3_bucket_tags

        tag_set = [{"Key": key, "Value": value} for key, value in tags.items()]
        s3_client.put_bucket_tagging(
            Bucket=bucket_name,
            Tagging={"TagSet": tag_set},
        )
        response = s3_client.get_bucket_tagging(Bucket=bucket_name)
        tags_res = response["TagSet"]
        if tags:
            logging.info("Tags for bucket: %s", bucket_name)
        else:
            logging.debug("No tags found for bucket: %s", bucket_name)

        self.assertEqual(len(tags_res), 4)

        for index, tag_key in enumerate(tags.keys()):
            self.assertEqual(tags_res[index]["Key"], tag_key)
            self.assertEqual(tags_res[index]["Value"], tags[tag_key])


if __name__ == "__main__":
    unittest.main()
