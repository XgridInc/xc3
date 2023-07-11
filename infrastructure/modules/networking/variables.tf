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

variable "vpc_cidr_block" {
  type        = string
  description = "AWS VPC CIDR range"
}

variable "public_subnet_cidr_block" {
  type        = map(string)
  description = "The CIDR Blocks of the public subnet"
}

variable "allow_traffic" {
  type        = list(string)
  description = "IP Address to access bastion host server"
}

variable "private_subnet_cidr_block" {
  type        = map(string)
  description = "AWS VPC CIDR range for private subnet"
}

variable "namespace" {
  type        = string
  description = "The namespace referring to an environment"
}

variable "owner_email" {
  type        = string
  description = "Email address of the team working in this project"
}

variable "creator_email" {
  type        = string
  description = "Email address of a person who is provisioning the infrastructure of XC3"
}

variable "project" {
  type        = string
  description = "The name of the Project"
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

variable "domain_name" {
  type        = string
  description = "Domain name for SSL Certificates"
}

variable "env" {
  description = "Env variable for Dev/Prod"
  type        = string
}
