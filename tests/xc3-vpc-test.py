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
from config import vpc, vpc_cidr, subnetid1, subnetid2, subnetid3, routetable


def test_vpc_cidr():
    """
    Test if the VPC has the correct CIDR block assigned.

    The test uses Boto3 to check if the VPC with the given name
    has the correct CIDR block assigned to it.
    If the CIDR block is correct, the test passes.
    If the CIDR block is incorrect, the test fails.

    Raises:
        AssertionError: If the VPC does not have the correct CIDR block assigned to it.
    """
    try:
        ec2_client = boto3.client("ec2")
        vpc_name = vpc
        vpc_response = ec2_client.describe_vpcs(
            Filters=[{"Name": "tag:Name", "Values": [vpc_name]}]
        )
        vpc_cidr_block = vpc_response["Vpcs"][0]["CidrBlock"]
        assert (
            vpc_cidr_block == vpc_cidr
        ), f"VPC {vpc_name} has the correct CIDR block assigned to it"
    except Exception as e:
        assert False, f"Error during test_vpc_cidr: {e}"


def test_vpc_subnets():
    """
    Test if the VPC has the correct subnets assigned to it.

    The test uses Boto3 to check if the VPC with the given name
    has the correct subnets assigned to it.
    If the subnets are correct, the test passes.
    If the subnets are incorrect, the test fails.

    Raises:
        AssertionError: If the VPC does not have the correct subnets assigned to it.
    """
    try:
        ec2_client = boto3.client("ec2")
        vpc_name = vpc
        vpc_response = ec2_client.describe_vpcs(
            Filters=[{"Name": "tag:Name", "Values": [vpc_name]}]
        )
        vpc_id = vpc_response["Vpcs"][0]["VpcId"]
        subnet_response = ec2_client.describe_subnets(
            Filters=[{"Name": "vpc-id", "Values": [vpc_id]}]
        )
        subnet_ids = [subnet["SubnetId"] for subnet in subnet_response["Subnets"]]
        expected_subnets = [subnetid1, subnetid2, subnetid3]
        assert set(subnet_ids) == set(
            expected_subnets
        ), f"VPC {vpc_name} has the correct subnets assigned to it"
    except Exception as e:
        assert False, f"Error during test_vpc_subnets: {e}"


def test_vpc_route_table():
    """
    Test if the VPC has the correct route table assigned to it.

    The test uses Boto3 to check if the VPC with the given name
    has the correct route table assigned to it.
    If the route table is correct, the test passes.
    If the route table is incorrect, the test fails.

    Raises:
        AssertionError: If the VPC does not have the correct route table assigned to it.
    """
    try:
        ec2_client = boto3.client("ec2")
        vpc_name = vpc
        vpc_response = ec2_client.describe_vpcs(
            Filters=[{"Name": "tag:Name", "Values": [vpc_name]}]
        )
        vpc_id = vpc_response["Vpcs"][0]["VpcId"]
        route_table_response = ec2_client.describe_route_tables(
            Filters=[{"Name": "vpc-id", "Values": [vpc_id]}]
        )

        route_table_id = route_table_response["RouteTables"][0]["Associations"][0][
            "RouteTableId"
        ]
        expected_route_table = routetable
        assert (
            route_table_id == expected_route_table
        ), f"VPC {vpc_name} has the correct route table assigned to it"
    except Exception as e:
        assert False, f"Error during test_vpc_route_table: {e}"
