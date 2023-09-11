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
import pytest

from config import (env, loadbalancer_name, publicsubnetid1, publicsubnetid2,
                    vpc_ids)


def skip_if_not_prod(func):
    def wrapper(*args, **kwargs):
        if env != "prod":
            pytest.skip("Skipping function because env is not prod")
        return func(*args, **kwargs)
    return wrapper

@skip_if_not_prod
def test_loadbalancer_vpcid():
    """
    Test the VPC ID associated with a load balancer.

    This test verifies whether the VPC ID assigned to a specific load balancer matches the expected VPC ID.

    Raises:
        AssertionError: If the VPC ID does not match the expected VPC ID.

    """

    try:
        # Create an ELBV2 client
        elbv2_client = boto3.client('elbv2')

        # Describe the load balancer
        response = elbv2_client.describe_load_balancers(Names=[loadbalancer_name])

        # Print the details of the load balancer
        load_balancer_vpcid = response['LoadBalancers'][0]['VpcId']
        
        assert load_balancer_vpcid == vpc_ids, f"{loadbalancer_name} has the correct VPC ID assigned to it"
    
    except Exception as e:

        assert False, f"{loadbalancer_name} has incorrect VPC ID assigned to it: {e}"


@skip_if_not_prod
def test_loadbalancer_publicsubnet():
    """
    Test the subnet IDs associated with a load balancer.

    This test verifies whether at least one of the subnet IDs associated with a specific load balancer matches
    one of the expected public subnet IDs.

    Raises:
        AssertionError: If none of the subnet IDs match the expected public subnet IDs.

    """
    try:
        # Create an ELBV2 client
        elbv2_client = boto3.client('elbv2')

        # Describe the load balancer
        response = elbv2_client.describe_load_balancers(Names=[loadbalancer_name])

        load_balancer_subnetids = [
            response['LoadBalancers'][0]['AvailabilityZones'][0]['SubnetId'],
            response['LoadBalancers'][0]['AvailabilityZones'][1]['SubnetId']
        ]

        assert any(subnet_id == publicsubnetid1 or subnet_id == publicsubnetid2 for subnet_id in load_balancer_subnetids), f"{loadbalancer_name} has the correct Subnet IDs assigned to it"
    
    except Exception as e:
        
        assert False, f"{loadbalancer_name} has incorrect Subnet ID assigned to it: {e}"