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

// Terraform Remote State

terraform {
  backend "s3" {
    bucket         = "terraform-state-xc3" // S3 bucket for terraform state management
    key            = "xc3/xc3.tfstate"        // Specifies the S3 object key for storing the Terraform state file
    region         = "eu-west-1"
    dynamodb_table = "terraform-lock"
  }
}
