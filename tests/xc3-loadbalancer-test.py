import boto3
import json
from botocore.exceptions import ClientError
from config import loadbalancer_name, region

def test_load_balancer():
    """
    Unit test method for testing the configuration of an Elastic Load Balancer (ELB).

    Parameters:
        - None

    Returns:
        - None

    Raises:
        - AssertionError: If the ELB is not active, if the ELB name is incorrect or
        if the Boto3 command fails.

    Usage:
        - Call this method to test the configuration of an ELB. The method uses Boto3
        to get the details of the ELB with the given name and region, and then asserts
        that the ELB is active, and that the ELB name matches the given name.
        If any of these conditions are not met, an AssertionError is raised.
    """
    lb_name = loadbalancer_name
    elbv2 = boto3.client('elbv2', region_name=region)
    try:
        response = elbv2.describe_load_balancers(Names=[lb_name])
        lb_info = response['LoadBalancers'][0]
        assert lb_info['LoadBalancerName'] == lb_name, f"Unexpected load balancer name: {lb_info['LoadBalancerName']}"
        assert lb_info['State']['Code'] == 'active', f"Load balancer is not active: {lb_info['State']}"
    except ClientError as e:
        assert False, f"Error: {e}"

