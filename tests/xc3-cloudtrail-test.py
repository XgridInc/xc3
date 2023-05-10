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
from botocore.exceptions import ClientError
from config import cloudtrail_arn

CLOUDTRAIL_NAME = cloudtrail_arn.split("/")[-1]

# Create Boto3 client for AWS cloudtrail
cloudtrail_client = boto3.client("cloudtrail")


def test_cloudtrail_is_enabled():
    """
    Test if CloudTrail is enabled for logging AWS API events.

    The test uses Boto3 to check if a specific CloudTrail trail
    is enabled for logging AWS API events. The test assumes that the
    AWS account has a CloudTrail trail with the name specified in the
    `CLOUDTRAIL_NAME` constant in the config module, and that Boto3 is installed.

    The test verifies that the trail exists, is a multi-region trail,
    and has log file validation enabled. If any of these conditions are
    not met or if there is an error while retrieving the trail details,
    the test will fail.

    Raises:
        AssertionError: If the CloudTrail trail does not meet the specified criteria
        or if there is an error.
    """
    try:
        response = cloudtrail_client.describe_trails(trailNameList=[CLOUDTRAIL_NAME])
        assert len(response["trailList"]) == 1
        assert (
            response["trailList"][0]["IsMultiRegionTrail"] is True
        ), f"MultiRegionTrail exists for {CLOUDTRAIL_NAME}"
        assert (
            response["trailList"][0]["LogFileValidationEnabled"] is True
        ), f"validation is enabled for {CLOUDTRAIL_NAME}"
    except ClientError as e:
        raise AssertionError(
            f"Error occurred while retrieving CloudTrail details: {str(e)}"
        )
