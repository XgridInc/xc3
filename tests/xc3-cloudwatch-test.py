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
from config import (
    cloudwatch_most_expensive_name,
    cloudwatch_project_spend_name,
    cloudwatch_resource_list_name,
    cloudwatch_total_account_cost_name,
    cloudwatch_cost_report_notifier_name,
    cloudwatch_linked_list_name,
)

# Initialize the CloudWatch client
cloudwatch = boto3.client("events")


def test_cloudwatch_event_cost_report_rule_exists():
    """Checks whether an Amazon CloudWatch event rule with the
    given name exists and has the expected details.

    Args:
        None

    Returns:
        None

    Raises:
        AssertionError: If the event rule does not exist or has
        unexpected details.

    The function tries to retrieve an Amazon CloudWatch event rule by
    name using the `describe_rule()` method of the `cloudwatch` client.
    If the rule is not found, the function raises an `AssertionError`
    with a message indicating that the rule does not exist.
    If the rule is found, the function checks whether its name matches the
    expected value. If not, the function raises an `AssertionError`
    with a message indicating that the rule name is unexpected.

    """
    try:
        response = cloudwatch.describe_rule(Name=cloudwatch_cost_report_notifier_name)
        # The event rule exists, check its details
        assert (
            response["Name"] == cloudwatch_cost_report_notifier_name
        ), "Unexpected event rule name"
    except cloudwatch.exceptions.ResourceNotFoundException:
        # The event rule does not exist
        assert (
            False
        ), f"The {cloudwatch_cost_report_notifier_name} event rule does not exist."


def test_cloudwatch_event_most_expensive_rule_exists():
    """Checks whether an Amazon CloudWatch event rule with the
    given name exists and has the expected details.

    Args:
        None

    Returns:
        None

    Raises:
        AssertionError: If the event rule does not exist or has
        unexpected details.

    The function tries to retrieve an Amazon CloudWatch event rule by
    name using the `describe_rule()` method of the `cloudwatch` client.
    If the rule is not found, the function raises an `AssertionError`
    with a message indicating that the rule does not exist.
    If the rule is found, the function checks whether its name matches
    the expected value. If not, the function raises an `AssertionError`
    with a message indicating that the rule name is unexpected.

    """
    try:
        response = cloudwatch.describe_rule(Name=cloudwatch_most_expensive_name)
        # The event rule exists, check its details
        assert (
            response["Name"] == cloudwatch_most_expensive_name
        ), "Unexpected event rule name"
    except cloudwatch.exceptions.ResourceNotFoundException:
        # The event rule does not exist
        assert False, f"The {cloudwatch_most_expensive_name} event rule does not exist."


def test_cloudwatch_event_project_spend_rule_exists():
    """Checks whether an Amazon CloudWatch event rule with the
    given name exists and has the expected details.

    Args:
        None

    Returns:
        None

    Raises:
        AssertionError: If the event rule does not exist or
        has unexpected details.

    The function tries to retrieve an Amazon CloudWatch event rule by name
    using the `describe_rule()` method of the `cloudwatch` client.
    If the rule is not found, the function raises an `AssertionError`
    with a message indicating that the rule does not exist.
    If the rule is found, the function checks whether its name matches
    the expected value. If not, the function raises an `AssertionError`
    with a message indicating that the rule name is unexpected.

    """
    try:
        response = cloudwatch.describe_rule(Name=cloudwatch_project_spend_name)
    except cloudwatch.exceptions.ResourceNotFoundException:
        # The event rule does not exist
        assert False, f"The {cloudwatch_project_spend_name} event rule does not exist."
    else:
        # The event rule exists, check its details
        assert (
            response["Name"] == cloudwatch_project_spend_name
        ), "Unexpected event rule name"


def test_cloudwatch_event_resource_list_rule_exists():
    """Checks whether an Amazon CloudWatch event rule with the given name
    exists and has the expected details.

    Args:
        None

    Returns:
        None

    Raises:
        AssertionError: If the event rule does not exist or
        has unexpected details.

    The function tries to retrieve an Amazon CloudWatch event rule by name
    using the `describe_rule()` method of the `cloudwatch` client.
    If the rule is not found, the function raises an `AssertionError`
    with a message indicating that the rule does not exist.
    If the rule is found, the function checks whether its name matches
    the expected value. If not, the function raises an `AssertionError`
    with a message indicating that the rule name is unexpected.

    """
    try:
        response = cloudwatch.describe_rule(Name=cloudwatch_resource_list_name)
    except cloudwatch.exceptions.ResourceNotFoundException:
        # The event rule does not exist
        assert False, f"The {cloudwatch_resource_list_name} event rule does not exist."
    else:
        # The event rule exists, check its details
        assert (
            response["Name"] == cloudwatch_resource_list_name
        ), "Unexpected event rule name"


def test_cloudwatch_event_total_account_cost_rule_exists():
    """Checks whether an Amazon CloudWatch event rule with the given name
    exists and has the expected details.

    Args:
        None

    Returns:
        None

    Raises:
        AssertionError: If the event rule does not exist or
        has unexpected details.

    The function tries to retrieve an Amazon CloudWatch event rule by
    name using the `describe_rule()` method of the `cloudwatch` client.
    If the rule is not found, the function raises an `AssertionError`
    with a message indicating that the rule does not exist.
    If the rule is found, the function checks whether its name matches
    the expected value. If not, the function raises an `AssertionError`
    with a message indicating that the rule name is unexpected.

    """
    try:
        response = cloudwatch.describe_rule(Name=cloudwatch_total_account_cost_name)
    except cloudwatch.exceptions.ResourceNotFoundException:
        # The event rule does not exist
        assert (
            False
        ), f"The {cloudwatch_total_account_cost_name} event rule does not exist."
    else:
        # The event rule exists, check its details
        assert (
            response["Name"] == cloudwatch_total_account_cost_name
        ), "Unexpected event rule name"


def test_cloudwatch_event_linked_list_rule_exists():
    """Checks whether an Amazon CloudWatch event rule with the given name
    exists and has the expected details.

    Args:
        None

    Returns:
        None

    Raises:
        AssertionError: If the event rule does not exist or
        has unexpected details.

    The function tries to retrieve an Amazon CloudWatch event rule by
    name using the `describe_rule()` method of the `cloudwatch` client.
    If the rule is not found, the function raises an `AssertionError`
    with a message indicating that the rule does not exist.
    If the rule is found, the function checks whether its name matches
    the expected value. If not, the function raises an `AssertionError`
    with a message indicating that the rule name is unexpected.

    """
    try:
        response = cloudwatch.describe_rule(Name=cloudwatch_linked_list_name)
    except cloudwatch.exceptions.ResourceNotFoundException:
        # The event rule does not exist
        assert False, f"The {cloudwatch_linked_list_name} event rule does not exist."
    else:
        # The event rule exists, check its details
        assert (
            response["Name"] == cloudwatch_linked_list_name
        ), "Unexpected event rule name"
