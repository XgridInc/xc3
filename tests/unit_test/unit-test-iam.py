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

import json
import unittest

import boto3
from config import (
    iam_role_list_linked_accounts_assumed_policy,
    iam_role_list_linked_accounts_name,
    iam_role_most_expensive_service_role_name,
    iam_role_project_spend_cost_assumed_policy,
    iam_role_project_spend_cost_name,
    iam_role_resource_list_assumed_policy,
    iam_role_resource_list_name,
    iam_role_total_account_cost_assumed_policy,
    iam_role_total_account_cost_name,
    mes_role_assumed_policy,
    region,
)
from moto import mock_iam


class IAMRoleMockTests(unittest.TestCase):
    @mock_iam
    def test_create_describe_delete_iam_roles(self):
        iam_client = boto3.client("iam", region_name=region)
        roles = [
            {
                "role_name": iam_role_project_spend_cost_name,
                "assume_role_policy": iam_role_project_spend_cost_assumed_policy,
            },
            {
                "role_name": iam_role_list_linked_accounts_name,
                "assume_role_policy": iam_role_list_linked_accounts_assumed_policy,
            },
            {
                "role_name": iam_role_total_account_cost_name,
                "assume_role_policy": iam_role_total_account_cost_assumed_policy,
            },
            {
                "role_name": iam_role_resource_list_name,
                "assume_role_policy": iam_role_resource_list_assumed_policy,
            },
            {
                "role_name": iam_role_most_expensive_service_role_name,
                "assume_role_policy": mes_role_assumed_policy,
            },
        ]

        for roles_data in roles:
            # Create an IAM role
            response = iam_client.create_role(
                RoleName=roles_data["role_name"],
                AssumeRolePolicyDocument=json.dumps(roles_data["assume_role_policy"]),
            )
            # Verify the role was created
            self.assertEqual(response["ResponseMetadata"]["HTTPStatusCode"], 200)

            # Describe the IAM role
            response = iam_client.get_role(RoleName=roles_data["role_name"])
            role = response["Role"]

            # Verify the role attributes
            self.assertEqual(role["RoleName"], roles_data["role_name"])
            self.assertEqual(
                role["AssumeRolePolicyDocument"], roles_data["assume_role_policy"]
            )

            # Delete the IAM role
            response = iam_client.delete_role(RoleName=roles_data["role_name"])

            # Verify the role was deleted
            self.assertEqual(response["ResponseMetadata"]["HTTPStatusCode"], 200)

    @mock_iam
    def test_create_describe_delete_iam_instance_profile(self):
        iam_client = boto3.client("iam", region_name=region)

        # Create an IAM instance profile
        instance_profile_name = "test-instance-profile"
        response = iam_client.create_instance_profile(
            InstanceProfileName=instance_profile_name
        )

        # Verify the instance profile was created
        self.assertEqual(response["ResponseMetadata"]["HTTPStatusCode"], 200)

        # Describe the IAM instance profile
        response = iam_client.get_instance_profile(
            InstanceProfileName=instance_profile_name
        )
        instance_profile = response["InstanceProfile"]

        # Verify the instance profile attributes
        self.assertEqual(instance_profile["InstanceProfileName"], instance_profile_name)

        # Delete the IAM instance profile
        response = iam_client.delete_instance_profile(
            InstanceProfileName=instance_profile_name
        )

        # Verify the instance profile was deleted
        self.assertEqual(response["ResponseMetadata"]["HTTPStatusCode"], 200)


if __name__ == "__main__":
    unittest.main()
