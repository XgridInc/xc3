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

from config import (
    ec2privatename,
    ec2publicname,
    publicsecuritygroupname,
    privatesecuritygroupname,
)

try:
    # Initializing EC2 Client
    ec2_client = boto3.client("ec2")
except ClientError as e:
    print(f"Error creating EC2 client: {e}")
    raise e


def test_private_ec2_instance_creation():
    """
    Test if the EC2 instance is created successfully.

    The test uses Boto3 to check if the EC2 instance with the given name exists.
    If the EC2 instance exists,
    the test passes. If the EC2 instance does not exist, the test fails.

    Raises:
        AssertionError: If the EC2 instance with the given name does not exist.
    """

    instance_name = ec2privatename
    try:
        instance_response = ec2_client.describe_instances(
            Filters=[{"Name": "tag:Name", "Values": [instance_name]}]
        )
        instance_status = instance_response["Reservations"][0]["Instances"][0]["State"][
            "Name"
        ]
        assert (
            instance_status == "running"
        ), f"EC2 instance {instance_name} is created successfully"
    except ec2_client.exceptions.ClientError as e:
        error_code = e.response["Error"]["Code"]
        assert (
            error_code == "InvalidInstanceID.NotFound"
        ), f"EC2 instance {instance_name} is not created successfully"


def test_bastion_ec2_instance_creation():
    """
    Test if the EC2 instance is created successfully.

    The test uses Boto3 to check if the EC2 instance with the given name exists.
    If the EC2 instance exists,
    the test passes. If the EC2 instance does not exist, the test fails.

    Raises:
        AssertionError: If the EC2 instance with the given name does not exist.
    """

    instance_name = ec2publicname
    try:
        instance_response = ec2_client.describe_instances(
            Filters=[{"Name": "tag:Name", "Values": [instance_name]}]
        )
        instance_status = instance_response["Reservations"][0]["Instances"][0]["State"][
            "Name"
        ]
        assert (
            instance_status == "running"
        ), f"EC2 instance {instance_name} is created successfully"
    except ec2_client.exceptions.ClientError as e:
        error_code = e.response["Error"]["Code"]
        assert (
            error_code == "InvalidInstanceID.NotFound"
        ), f"EC2 instance {instance_name} is not created successfully"


def test_bastion_ec2_instance_security_group():
    """
    Test if the EC2 instance has the correct security group assigned.

    The test uses Boto3 to check if the EC2 instance with the given name
    has the correct security group assigned to it.
    If the security group is correct, the test passes. If the security group
    is incorrect, the test fails.

    Raises:
        AssertionError: If the EC2 instance does not have the correct security
        group assigned to it.
    """

    instance_name = ec2publicname
    security_group_name = publicsecuritygroupname
    try:
        instance_response = ec2_client.describe_instances(
            Filters=[{"Name": "tag:Name", "Values": [instance_name]}]
        )
        instance_security_groups = instance_response["Reservations"][0]["Instances"][0][
            "SecurityGroups"
        ]
        instance_security_group_ids = [sg["GroupId"] for sg in instance_security_groups]
        security_group_response = ec2_client.describe_security_groups(
            Filters=[{"Name": "group-name", "Values": [security_group_name]}]
        )
        security_group_id = security_group_response["SecurityGroups"][0]["GroupId"]
        assert (
            security_group_id in instance_security_group_ids
        ), f"EC2 instance {instance_name} has the correct sg assigned"
    except ec2_client.exceptions.ClientError as e:
        assert False, f"Error checking EC2 instance {instance_name} security group: {e}"


def test_private_ec2_instance_security_group():
    """
    Test if the EC2 instance has the correct security group assigned.

    The test uses Boto3 to check if the EC2 instance with the given name has
    the correct security group assigned to it.
    If the security group is correct, the test passes. If the security group
    is incorrect, the test fails.

    Raises:
        AssertionError: If the EC2 instance does not have the correct security
        group assigned to it.
    """

    instance_name = ec2privatename
    security_group_name = privatesecuritygroupname
    try:
        instance_response = ec2_client.describe_instances(
            Filters=[{"Name": "tag:Name", "Values": [instance_name]}]
        )
        instance_security_groups = instance_response["Reservations"][0]["Instances"][0][
            "SecurityGroups"
        ]
        instance_security_group_ids = [sg["GroupId"] for sg in instance_security_groups]
        security_group_response = ec2_client.describe_security_groups(
            Filters=[{"Name": "group-name", "Values": [security_group_name]}]
        )
        security_group_id = security_group_response["SecurityGroups"][0]["GroupId"]
        assert (
            security_group_id in instance_security_group_ids
        ), f"EC2 instance {instance_name} has the correct sg assigned"
    except ec2_client.exceptions.ClientError as e:
        assert False, f"Error checking EC2 instance {instance_name} security group: {e}"
