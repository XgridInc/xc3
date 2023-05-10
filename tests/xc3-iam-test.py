# Copyright (c) 2023, Xgrid Inc, https://xgrid.co

# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

# http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import boto3
from config import iam_role_name


def test_iam_role_creation():
    """
    Test if the IAM role is created by Terraform.

    The test uses Boto3 to check if the IAM role with the given name exists.
    If the IAM role exists,
    the test passes. If the IAM role does not exist, the test fails.

    Raises:
        AssertionError: If the IAM role with the given name does not exist.
    """
    iam_client = boto3.client("iam")
    role_name = iam_role_name
    try:
        role_response = iam_client.get_role(RoleName=role_name)
        assert (
            role_response["Role"]["RoleName"] == role_name
        ), f"IAM role {role_name} does exist"
    except iam_client.exceptions.NoSuchEntityException:
        assert False, f"IAM role {role_name} does not exist"
