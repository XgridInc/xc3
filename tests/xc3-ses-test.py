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
from config import ses_name


def test_email_identity_exists():
    """
    Unit test method for testing the existence of an email identity in
    Amazon Simple Email Service (SES).

    Parameters:
        - None

    Returns:
        - None

    Raises:
        - AssertionError: If the email identity does not exist.

    Usage:
        - Call this method to test the existence of an email identity in SES.
        The method uses the `boto3` client library to list all the
        email identities in SES, and then asserts that the given email identity
        is present in the list of identities.
        If the email identity is not present, an AssertionError is raised."""

    ses = boto3.client("ses")
    email_identity = ses_name
    try:
        response = ses.list_identities(IdentityType="EmailAddress")
        identities = response["Identities"]
        assert email_identity in identities, f"{ses_name} exists"
    except Exception as e:
        assert False, f"Error: {e}"
