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

data "aws_ami" "ubuntu" {
  owners = ["099720109477"]

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-20220914"]
  }
}

data "aws_key_pair" "key_pair" {
  key_name = "${var.namespace}-key"
}

data "aws_acm_certificate" "issued" {
  count       = var.domain_name != "" ? 1 : 0
  domain      = var.domain_name
  most_recent = true
  types       = ["AMAZON_ISSUED"]
  statuses    = ["ISSUED"]
  key_types   = ["RSA_2048"]
}
