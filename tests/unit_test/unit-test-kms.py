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
import unittest

import boto3
from config import kms_id, region
from moto import mock_kms

try:
    kms_client = boto3.client("kms", region_name=region)
except Exception as e:
    logging.error("Error creating KMS client: " + str(e))


class KMSMockTests(unittest.TestCase):
    @mock_kms
    def test_encrypt_decrypt_data(self):

        # Create a KMS key
        key_alias = f"alias/{kms_id}"
        response = kms_client.create_key()
        key_id = response["KeyMetadata"]["KeyId"]
        kms_client.create_alias(AliasName=key_alias, TargetKeyId=key_id)

        # Encrypt data
        plaintext = "Hello, World!"
        encryption_response = kms_client.encrypt(
            KeyId=key_alias, Plaintext=plaintext.encode()
        )
        ciphertext = encryption_response["CiphertextBlob"]

        # Decrypt data
        decryption_response = kms_client.decrypt(CiphertextBlob=ciphertext)
        decrypted_plaintext = decryption_response["Plaintext"].decode()

        # Assert the original plaintext matches the decrypted plaintext
        self.assertEqual(plaintext, decrypted_plaintext)


if __name__ == "__main__":
    unittest.main()
