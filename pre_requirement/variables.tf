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

variable "namespace" {
  type        = string
  description = "The namespace referring to an env"
}

variable "creator_email" {
  type        = string
  description = "Email address of a person who is provisioning the infrastructure"
}

variable "owner_email" {
  type        = string
  description = "Email address of a person who is owner of the team/project"
}

variable "project" {
  type        = string
  description = "The name of the Project"
}

variable "region" {
  type        = string
  description = "AWS region where resources will be deployed"
}

variable "iam_permission_policies" {
  description = "IAM permission policies"
  type        = map(string)
  default = {
    access_management = "./policies/iam_permission_set.json"
    infra_policy      = "./policies/infra_permission_set.json"
  }
}
