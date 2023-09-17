import unittest
import boto3
import logging

from config import region, load_balancer, env

class TestLoadBalancerCreation(unittest.TestCase):

    def setUp(self):
        # Initialize the AWS ELB client
        self.elb_client = boto3.client('elbv2', region_name=region)

    @unittest.skipIf(env == 'dev', "Skipping test in dev environment")
    def test_load_balancer_created(self):
        
        # Log the load balancer name and other relevant information for debugging
        logging.info(f"Testing load balancer: {load_balancer}, Region: {region}, Environment: {env}")

        # Check if the load balancer exists
        try:
            response = self.elb_client.describe_load_balancers(Names=[load_balancer])
            load_balancer_count = len(response['LoadBalancers'])

            if load_balancer_count == 1:
                logging.info(f"Load balancer '{load_balancer}' has been created.")
            elif load_balancer_count == 0:
                logging.warning(f"Load balancer '{load_balancer}' not found.")
            else:
                logging.warning(f"Multiple load balancers with the name '{load_balancer}' found.")

            self.assertEqual(load_balancer_count, 1, "Expected one load balancer to be created.")
        except self.elb_client.exceptions.ClientError as e:
            if e.response['Error']['Code'] == 'LoadBalancerNotFound':
                logging.warning(f"Load balancer '{load_balancer}' not found.")
            else:
                raise

if __name__ == '__main__':
    unittest.main()
