import unittest
import boto3
from config import (
    region,
    load_balancer,
    env  # Import the 'env' variable from your config
)

class TestLoadBalancer(unittest.TestCase):

    def setUp(self):
        # Initialize the AWS ELB client
        self.elb_client = boto3.client('elbv2', region_name=region)

        # Replace 'your_load_balancer_name' with the name of your load balancer
        self.load_balancer_name = load_balancer

    @unittest.skipIf(env == 'dev', "Skipping test in dev environment")
    def test_load_balancer_exists(self):
        # Check if the load balancer exists
        try:
            response = self.elb_client.describe_load_balancers(Names=[self.load_balancer_name])
            self.assertEqual(len(response['LoadBalancers']), 1)
        except self.elb_client.exceptions.ClientError as e:
            if e.response['Error']['Code'] == 'LoadBalancerNotFound':
                self.fail(f"Load balancer '{self.load_balancer_name}' not found.")
            else:
                raise

if __name__ == '__main__':
    unittest.main()
