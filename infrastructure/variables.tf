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

variable "region" {
  type        = string
  description = "AWS region where resources will be deployed"
}

variable "vpc_cidr_block" {
  type        = string
  description = "VPC CIDR Block"
}

variable "public_subnet_cidr_block" {
  type        = map(string)
  description = "The CIDR Blocks of the public subnet"
}

variable "private_subnet_cidr_block" {
  type        = map(string)
  description = "The CIDR Block of the private subnet"
}

variable "allow_traffic" {
  type        = list(string)
  description = "IP Address to access bastion host server"
}

variable "ses_email_address" {
  type        = string
  description = "The email address for SES identity"
}

variable "instance_type" {
  type        = string
  description = "The type of the EC2 instance"
  default     = "t2.micro"
}

variable "security_group_ingress" {
  type = map(object({
    description = string
    from_port   = number
    to_port     = number
    protocol    = string
    cidr_blocks = list(string)
  }))
  description = "Security Group Ingress Rules"
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

variable "prometheus_layer" {
  type        = string
  description = "S3 key for prometheus layer"
}

variable "memory_size" {
  type        = number
  description = "The amount of memory to allocate to the lambda function"
}

variable "timeout" {
  type        = number
  description = "The number of seconds before the lambda function times out"
}

variable "total_account_cost_lambda" {
  type        = string
  description = "The name of the lambda function that will be used to calculate cost metrics of provided AWS Account"
}

variable "account_id" {
  type        = string
  description = "AWS Account id in which infrastructure will be deployed"
}

variable "total_account_cost_cronjob" {
  type        = string
  description = "Cron Job frequency for Total Account Cost"
}

variable "domain_name" {
  type        = string
  description = "Domain name for SSL Certificates"
  default     = ""
}


variable "hosted_zone_id" {
  type        = string
  description = "Public Hosted Zone ID in the Route 53"
}

variable "cron_jobs_schedule" {
  description = "Cron job schedule"
  type        = map(string)
  default = {
    resource_list_function_cron  = "cron(0 0 * * ? 1)"
    list_linked_accounts_cron    = "cron(0 0 1 * ? *)"
    most_expensive_service_cron  = "cron(0 0 * * ? 1)"
    cost_report_notifier_cronjob = "cron(0 0 1,15 * ? *)"
  }
}

variable "slack_channel_url" {
  description = "Slack Channel URL"
  type        = string
  default     = ""
}

variable "create_kms" {
  description = "Fetch the KMS if exist"
  type        = bool
}

variable "env" {
  description = "Env variable for Dev/Prod"
  type        = string
  default     = "dev"
}
