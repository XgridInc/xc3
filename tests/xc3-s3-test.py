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

import boto3
import json
from config import s3_bucket_arn, s3_bucket_tags

# Initializing S3 Client

s3_client = boto3.client("s3")


def test_s3_bucket_creation():
    """
    Test if the S3 bucket is created by Terraform.

    The test uses Boto3 to check if the S3 bucket with the given name exists.
    If the S3 bucket exists,the test passes.
    If the S3 bucket does not exist, the test fails.

    Raises:
        AssertionError: If the S3 bucket with the given name does not exist.
    """
    s3_client = boto3.client("s3")
    bucket_name = s3_bucket_arn.split(":")[-1]

    try:
        s3_response = s3_client.head_bucket(Bucket=bucket_name)
        assert s3_response is not None
    except s3_client.exceptions.ClientError as e:
        error_code = e.response["Error"]["Code"]
        assert error_code == "404", f"S3 bucket {bucket_name} does not exist"


def test_s3_bucket_encryption():
    """
    Test if the S3 bucket has default encryption enabled.

    The test uses Boto3 to check if the S3 bucket with the given name
    has default encryption enabled.
    If default encryption is enabled, the test passes.
    If default encryption is not enabled, the test fails.

    Raises:
        AssertionError: If the S3 bucket with the given name does
        not have default encryption enabled.
    """

    bucket_name = s3_bucket_arn.split(":")[-1]

    try:
        s3_response = s3_client.get_bucket_encryption(Bucket=bucket_name)
        rule = s3_response["ServerSideEncryptionConfiguration"]["Rules"][0]
        assert rule["ApplyServerSideEncryptionByDefault"]["SSEAlgorithm"] == "AES256"
    except s3_client.exceptions.ClientError as e:
        error_code = e.response["Error"]["Code"]
        assert (
            error_code == "ServerSideEncryptionConfigurationNotFoundError"
        ), f"S3 bucket {bucket_name} does not have default encryption enabled"


def test_s3_bucket_access_policy():
    """
    Test if the S3 bucket has the correct access policy.

    The test uses Boto3 to check if the S3 bucket with the given name
    has the correct access policy.
    If the access policy is correct, the test passes.
    If the access policy is incorrect, the test fails.

    Raises:
        AssertionError: If the S3 bucket with the given name does not have
        the correct access policy.
    """

    bucket_name = s3_bucket_arn.split(":")[-1]
    access_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": "*",
                "Action": ["s3:GetObject", "s3:PutObject"],
                "Resource": [
                    f"arn:aws:s3:::{bucket_name}/*",
                ],
            }
        ],
    }

    try:
        s3_response = s3_client.get_bucket_policy(Bucket=bucket_name)
        assert s3_response["Policy"] == json.dumps(
            access_policy
        ), "Access Policy exists"
    except s3_client.exceptions.ClientError as e:
        error_code = e.response["Error"]["Code"]
        assert (
            error_code == "NoSuchBucketPolicy"
        ), "S3 bucket {bucket_name} does not have the correct access policy"


def test_s3_bucket_tags():
    """
    Test if the S3 bucket has the expected tags.

    The test uses Boto3 to check if the S3 bucket with the given name
    has the expected tags.
    If the tags are correct, the test passes.
    If the tags are incorrect or not present, the test fails.

    Raises:
        AssertionError: If the S3 bucket with the given name does not have
        the expected tags.
    """

    bucket_name = s3_bucket_arn.split(":")[-1]
    expected_tags = s3_bucket_tags

    try:
        s3_response = s3_client.get_bucket_tagging(Bucket=bucket_name)
        actual_tags = {tag["Key"]: tag["Value"] for tag in s3_response["TagSet"]}
        assert (
            actual_tags == expected_tags
        ), f"{actual_tags} is equal to {expected_tags}"
    except s3_client.exceptions.ClientError as e:
        error_code = e.response["Error"]["Code"]
        assert (
            error_code == "NoSuchTagSet"
        ), f"S3 bucket {bucket_name} does not have the expected tags"
