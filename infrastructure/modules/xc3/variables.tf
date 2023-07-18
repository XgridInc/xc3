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

variable "region" {
  type        = string
  description = "The name of the region in which infrastructure will be provisioned"
}

variable "vpc_id" {
  type        = string
  description = "The ID of the VPC where the resources will be created"
}

variable "private_subnet_id" {
  type        = list(string)
  description = "The ID of the subnet where the resources will be created"
}

variable "security_group_ids" {
  type        = map(string)
  description = "security group ids"
}

variable "public_subnet_ids" {
  type        = list(string)
  description = "The ID of the public subnet where the bastion host server will be created"
}

variable "instance_type" {
  type        = string
  description = "The type of the EC2 instance"
  default     = "t2.micro"
}

variable "ses_email_address" {
  type        = string
  description = "The email address for SES identity"
}

variable "prometheus_layer" {
  type        = string
  description = "S3 key for prometheus layer"
}

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
  description = "The name of the S3 bucket for storage of cc policies metadata"
}

variable "project" {
  type        = string
  description = "The name of the Project"
}


variable "domain_name" {
  type        = string
  description = "Domain name for Grafana Dashboard"
  default     = ""
}


variable "hosted_zone_id" {
  type        = string
  description = "Public Hosted Zone ID in the Route 53"
}


variable "grafana_api_gateway" {
  type        = string
  description = "The API Gateway link "
}

variable "env" {
  description = "Env variable for Dev/Prod"
  type        = string
}
