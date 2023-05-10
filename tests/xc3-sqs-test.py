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
from config import sqs_name


def test_sqs_queue_name():
    """
    Function to test the name of an Amazon Simple Queue Service (SQS) queue.

    Parameters:
        - None

    Returns:
        - None

    Raises:
        - AssertionError: If the name of the SQS queue does not
        match the expected name.

    Usage:
        - Call this function to test the name of an SQS queue.
        The function uses the `boto3` client library to get the URL
        of the queue with the given name,
        and then compares the name in the URL to the expected name.
        If the names do not match,
        an AssertionError is raised.
    """

    sqs_client = boto3.client("sqs")
    queue_name = sqs_name
    try:
        response = sqs_client.get_queue_url(QueueName=queue_name)
        assert response["QueueUrl"].endswith(
            queue_name
        ), f"Queue {queue_name} matches {response['QueueUrl'].split('/')[-1]}"
    except Exception as e:
        assert False, f"Error: {e}"
