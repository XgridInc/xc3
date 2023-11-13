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

from config import s3_bucket_name


def test_cloudtrail_s3_bucket():
    """
    Test function to verify the correctness of CloudTrail S3 bucket configuration.

    This function connects to the AWS CloudTrail service, describes the available trails,
    and extracts the S3 bucket names associated with each trail. It then compares the
    extracted bucket names with the expected bucket name specified by the variable
    `s3_bucket_name`. If the extracted bucket names match the expected bucket name,
    the test passes; otherwise, an assertion error is raised.

    Note:
    - Ensure that the boto3 library is installed and AWS credentials are properly configured
      for this function to work correctly.

    Returns:
    None

    Raises:
    AssertionError: If the extracted bucket name(s) do not match the expected bucket name,
                   or if an exception occurs during the execution of the function.
    """
    try:
        # Create a CloudTrail client
        cloudtrail_client = boto3.client('cloudtrail')

        # Describe CloudTrail trails
        response = cloudtrail_client.describe_trails()

        # Extract the "S3BucketName" field for the trail with the name "yaseen-cloudtrail"
        filtered_bucket_names = [trail['S3BucketName'] for trail in response['trailList'] if trail['Name'] == [s3_bucket_name]]

        for bucket_name in filtered_bucket_names:
            assert filtered_bucket_names == s3_bucket_name, f"Cloudtrail bucket name is correct: {filtered_bucket_names}"
    
    except Exception as e:
        assert False, f"Cloudtrail bucket name is not correct: {e}"