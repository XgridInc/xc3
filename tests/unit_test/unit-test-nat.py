import logging
import unittest

import boto3
from config import region, vpc_cidr
from moto import mock_ec2

try:
    ec2_client = boto3.client("ec2", region_name=region)
except Exception as e:
    logging.error("Error creating EC2 client: " + str(e))


class NATGatewayMockTests(unittest.TestCase):
    @mock_ec2
    def test_create_describe_delete_nat_gateway(self):

        # Create a VPC
        vpc_response = ec2_client.create_vpc(CidrBlock=vpc_cidr)
        vpc_id = vpc_response["Vpc"]["VpcId"]

        # Create a subnet
        subnet_response = ec2_client.create_subnet(VpcId=vpc_id, CidrBlock=vpc_cidr)
        subnet_id = subnet_response["Subnet"]["SubnetId"]

        # Create an elastic IP
        elastic_ip_response = ec2_client.allocate_address(Domain="vpc")
        elastic_ip = elastic_ip_response["AllocationId"]

        # Create a NAT Gateway
        nat_gateway_response = ec2_client.create_nat_gateway(
            SubnetId=subnet_id, AllocationId=elastic_ip
        )
        nat_gateway_id = nat_gateway_response["NatGateway"]["NatGatewayId"]

        # Describe NAT Gateway
        nat_gateway_info = ec2_client.describe_nat_gateways(
            NatGatewayIds=[nat_gateway_id]
        )
        nat_gateway_state = nat_gateway_info["NatGateways"][0]["State"]

        # Assert NAT Gateway state
        self.assertEqual(nat_gateway_state, "available")


if __name__ == "__main__":
    unittest.main()
