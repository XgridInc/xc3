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
from config import natgatewayname
from config import natgatewayid
from config import natgatewaysubnetid

# Initializing EC2 Client
ec2_client = boto3.client("ec2")


def test_nat_gateway_allocation_id():
    """
    Test if the NAT gateway has the correct allocation ID.

    The test uses Boto3 to check if the NAT gateway has
    the correct allocation ID.
    If the allocation ID is correct, the test passes.
    If the allocation ID is incorrect, the test fails.

    Raises:
        AssertionError: If the NAT gateway does not have the correct allocation ID.
    """

    try:
        nat_gateway_response = ec2_client.describe_nat_gateways(
            Filters=[{"Name": "tag:Name", "Values": [natgatewayname]}]
        )
        allocation_id = nat_gateway_response["NatGateways"][0]["NatGatewayAddresses"][
            0
        ]["AllocationId"]
        expected_allocation_id = natgatewayid
        assert (
            allocation_id == expected_allocation_id
        ), f"NAT gateway has the correct allocation ID assigned: {allocation_id}"
    except Exception as e:
        assert False, f"Error: {e}"


def test_nat_gateway_subnet():
    """
    Test if the NAT gateway is in the correct subnet.

    The test uses Boto3 to check if the NAT gateway
    is in the correct subnet.
    If the subnet is correct, the test passes.
    If the subnet is incorrect, the test fails.

    Raises:
        AssertionError: If the NAT gateway is not in the correct subnet.
    """

    try:
        nat_gateway_response = ec2_client.describe_nat_gateways(
            Filters=[{"Name": "tag:Name", "Values": [natgatewayname]}]
        )
        subnet_id = nat_gateway_response["NatGateways"][0]["SubnetId"]
        expected_subnet_id = natgatewaysubnetid
        assert (
            subnet_id == expected_subnet_id
        ), f"NAT gateway is in the correct subnet: {subnet_id}"
    except Exception as e:
        assert False, f"Error: {e}"
