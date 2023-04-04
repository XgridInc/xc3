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

variable "owner_email" {
  type        = string
  description = "Email address of a owner who is leading the team"
}

variable "creator_email" {
  type        = string
  description = "Email of the the Creator who is provisioning the infrastructure"
}


variable "prometheus_ip" {
  description = "The IP address of the Prometheus server"
}

variable "memory_size" {
  description = "The amount of memory to allocate to the lambda function"
}

variable "timeout" {
  type        = number
  description = "The number of seconds before the lambda function times out"
}

variable "prometheus_layer" {
  type        = string
  description = "prometheus layer arn"
}

variable "subnet_id" {
  type        = string
  description = "The ID of the subnet where the resources will be created"
}

variable "security_group_id" {
  type        = string
  description = "The ID of the security group that will be associated with the resources"
}

variable "total_account_cost_lambda" {
  type        = string
  description = "The name of the lambda function that will be used to calculate cost metrics of provided AWS Account"
}

variable "account_id" {
  type        = string
  description = "AWS Account ID"
}

variable "total_account_cost_cronjob" {
  type        = string
  description = "Cron Job frequency for Total Account Cost"
}

variable "sns_topic_arn" {
  type        = string
  description = "SNS Topic for invoking lambda"
}

variable "s3_xccc_bucket" {
  description = "X-CCC metadata storage bucket"
}

variable "region" {
  type        = string
  description = "AWS region where resources will be deployed"
}

variable "lambda_names" {
  type        = map(string)
  description = "The names of lambda functions in IAM Role Workflow"
  default = {
    "iam_roles_all"          = "../lambda_functions/iam_roles/iam_roles_all.py"
    "iamrolesservice"        = "../lambda_functions/iam_roles/iamrolesservice.py"
    "iamrolesservicemapping" = "../lambda_functions/iam_roles/iamrolesservicemapping.py"
    "instancestatechange"    = "../lambda_functions/iam_roles/instancestatechange.py"
  }
}
