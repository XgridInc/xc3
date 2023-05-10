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
from config import kms_name


def test_kms_key_exists():
    """
    Unit test method for testing the existence of a KMS key with
    the given name or alias.

    Parameters:
        - None

    Returns:
        - None

    Raises:
        - AssertionError: If the KMS key with the given name or
        alias does not exist.

    Usage:
        - Call this method to test the existence of a KMS key
        with the given name or alias.
        The method uses the Boto3 client to describe the key
        with the provided ID or alias,
        and then asserts that the key exists. If the key
        does not exist, an AssertionError is raised.
    """

    # Initialize the KMS client
    kms = boto3.client("kms")

    # Replace with your KMS key ID or alias
    key_id = f"alias/{kms_name}"

    # Check if the key exists
    try:
        kms.describe_key(KeyId=key_id)
        key_exists = True
    except kms.exceptions.NotFoundException:
        key_exists = False

    # Assert that the key exists
    assert key_exists is True, f"{key_id} exists"
    assert key_exists is False, f"{key_id} doesn't exists"
