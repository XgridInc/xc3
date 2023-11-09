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

import logging
import re
import unittest

import boto3
import pytest
from botocore.exceptions import ClientError
from config import ec2_ami, ec2_ami_count, ec2_az, region
from moto import mock_ec2, settings


class EC2Test(unittest.TestCase):
    def setUp(self):
        try:
            self.client = boto3.client("ec2", region_name=region)
        except Exception as e:
            logging.error("Error creating EC2 client: " + str(e))

    @mock_ec2
    def test_instance_launch_and_terminate(self):

        with pytest.raises(ClientError) as ex:
            self.client.run_instances(
                ImageId=ec2_ami, MinCount=1, MaxCount=ec2_ami_count, DryRun=True
            )
        ex.value.response["ResponseMetadata"]["HTTPStatusCode"] == 412
        ex.value.response["Error"]["Code"] == "DryRunOperation"
        ex.value.response["Error"][
            "Message"
        ] == """An error occurred (DryRunOperation)
        when calling the RunInstances operation:
        Request would have succeeded, but DryRun flag is set"""

        reservation = self.client.run_instances(
            ImageId=ec2_ami, MinCount=1, MaxCount=ec2_ami_count
        )
        len(reservation["Instances"]) == ec2_ami_count
        instance = reservation["Instances"][0]
        instance["State"] == {"Code": 0, "Name": "pending"}
        instance_id = instance["InstanceId"]

        reservations = self.client.describe_instances(InstanceIds=[instance_id])[
            "Reservations"
        ]
        len(reservations) == ec2_ami_count
        reservations[0]["ReservationId"] == reservation["ReservationId"]
        instances = reservations[0]["Instances"]
        len(instances) == ec2_ami_count
        instance = instances[0]
        instance["InstanceId"] == instance_id
        instance["State"] == {"Code": 16, "Name": "running"}
        if settings.TEST_SERVER_MODE:
            # Exact value can't be determined in ServerMode
            instance.should.have.key("LaunchTime")
        else:
            launch_time = instance["LaunchTime"].strftime("%Y-%m-%dT%H:%M:%S.000Z")
            logging.info("Launch Time: %s", launch_time)
        if instance["VpcId"] is not None:
            logging.info("EC2 in VPC")
        instance["Placement"]["AvailabilityZone"] == ec2_az

        root_device_name = instance["RootDeviceName"]
        mapping = instance["BlockDeviceMappings"][0]
        mapping["DeviceName"] == root_device_name
        mapping["Ebs"]["Status"] == "in-use"
        volume_id = mapping["Ebs"]["VolumeId"]
        re.match(r"vol-\w+", volume_id)

        volume = self.client.describe_volumes(VolumeIds=[volume_id])["Volumes"][0]
        volume["Attachments"][0]["InstanceId"] == instance_id
        volume["State"] == "in-use"

        with pytest.raises(ClientError) as ex:
            self.client.terminate_instances(InstanceIds=[instance_id], DryRun=True)
        ex.value.response["ResponseMetadata"]["HTTPStatusCode"] == 412
        ex.value.response["Error"]["Code"] == "DryRunOperation"
        ex.value.response["Error"][
            "Message"
        ] == """An error occurred (DryRunOperation) when calling
        the TerminateInstances operation:
        Request would have succeeded, but DryRun flag is set"""

        response = self.client.terminate_instances(InstanceIds=[instance_id])
        len(response["TerminatingInstances"]) == ec2_ami_count
        instance = response["TerminatingInstances"][0]
        instance["InstanceId"] == instance_id
        instance["PreviousState"] == {"Code": 16, "Name": "running"}
        instance["CurrentState"] == {"Code": 32, "Name": "shutting-down"}

        reservations = self.client.describe_instances(InstanceIds=[instance_id])[
            "Reservations"
        ]
        instance = reservations[0]["Instances"][0]
        instance["State"] == {"Code": 48, "Name": "terminated"}


if __name__ == "__main__":
    unittest.main()
