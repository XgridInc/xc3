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

from config import ec2privatename, privatesecuritygroupname, vpc_ids


def test_ec2_vpc():
    """
    Test function to check if an EC2 instance has the correct VPC ID assigned to it.
    
    This function initializes an EC2 client, retrieves the VPC ID of the EC2 instance
    with the given 'ec2privatename', and then asserts whether the obtained VPC ID is
    equal to 'vpc_ids'. If the VPC ID matches, the test is considered successful.
    Otherwise, an exception is raised with an error message indicating the mismatch.
    
    Raises:
        AssertionError: If the VPC ID assigned to the EC2 instance does not match 'vpc_ids'.
        Any other exception raised during the execution is caught and also treated as a test failure.
    """

    try:
    # Initialize the EC2 client
        ec2_client = boto3.client('ec2')
        ec2name = ec2privatename

        response = ec2_client.describe_instances(Filters=[{'Name': 'tag:Name', 'Values': [ec2name]}])

        vpc_id = response['Reservations'][0]['Instances'][0]['VpcId']

        assert vpc_id == vpc_ids, f"{ec2name} has the correct VPC ID assigned to it"
        
    except Exception as e:
        assert False, f"VPC is not correct: {e}"

def test_ec2_security_group():
    """
    Test function to check if an EC2 instance has the correct Security Group ID assigned to it.
    
    This function initializes an EC2 client, retrieves the Security Group ID of the EC2 instance
    with the given 'ec2privatename', and then asserts whether the obtained Security Group ID is
    equal to 'privatesecuritygroupname'. If the Security Group ID matches, the test is considered
    successful. Otherwise, an exception is raised with an error message indicating the mismatch.
    
    Raises:
        AssertionError: If the Security Group ID assigned to the EC2 instance does not match 'privatesecuritygroupname'.
        Any other exception raised during the execution is caught and also treated as a test failure.
    """

    try:
    # Initialize the EC2 client
        ec2_client = boto3.client('ec2')
        ec2name = ec2privatename

        response = ec2_client.describe_instances(Filters=[{'Name': 'tag:Name', 'Values': [ec2name]}])

        security_group_id = response['Reservations'][0]['Instances'][0]['SecurityGroups'][0]['GroupId']

        assert security_group_id == privatesecuritygroupname, f"{ec2name} has the correct Security Group ID assigned to it"
        
    except Exception as e:
        assert False, f"Security Group ID is not correct: {e}"