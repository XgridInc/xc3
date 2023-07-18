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

namespace      = "testing"
region         = "eu-west-1"
account_id     = "123456789012"
vpc_cidr_block = "15.0.0.0/16"
public_subnet_cidr_block = {
  "eu-west-1a" = "15.0.1.0/24"
  "eu-west-1c" = "15.0.2.0/24"
}

domain_name    = ""
hosted_zone_id = ""
private_subnet_cidr_block = {
  "eu-west-1a" = "15.0.3.0/26"
}

allow_traffic              = ["39.50.156.207/32"]
ses_email_address          = "admin@example.co"
creator_email              = "admin@example.co"
owner_email                = "admin@example.co"
instance_type              = "t2.micro"
total_account_cost_lambda  = "total_account_cost"
total_account_cost_cronjob = "cron(0 0 1,15 * ? *)"     // flexible can be set according to need
prometheus_layer           = "lambda_layers/python.zip" // s3 key for lambda layer
memory_size                = 128
timeout                    = 300
project                    = "example"
security_group_ingress = {
  "pushgateway" = {
    description = "PushGateway"
    from_port   = 9091
    to_port     = 9091
    protocol    = "tcp"
    cidr_blocks = ["15.0.4.0/24"]
  },
  "prometheus" = {
    description = "Prometheus"
    from_port   = 9000
    to_port     = 9000
    protocol    = "tcp"
    cidr_blocks = ["15.0.5.0/24"]
  },
  "http" = {
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["15.0.6.0/24"]
  },
  "https" = {
    description = "HTTPS"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["15.0.7.0/24"]
  }
}
