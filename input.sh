#!/usr/bin/env bash
# shellcheck disable=SC2034
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

# Variables values that will be used in init script to create resources for XC3 infrastructure
env="dev"
namespace="sp"
project="sp"
region="ap-southeast-2"
allow_traffic="0.0.0.0/0"
domain="" #  [Optional] - If you want to use your own domain then set this variable.
account_id="172931698685"
hosted_zone_id="Z053166920YP1STI0EK5X"
owner_email="103842632@student.swin.edu.au"
creator_email="103842632@student.swin.edu.au"
ses_email_address="103842632@student.swin.edu.au"
bucket_name="terraform-state-example-spxc"

