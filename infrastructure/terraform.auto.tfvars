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

namespace      = "x-ccc"
region         = "eu-west-1"
account_id     = "201635854701"
vpc_cidr_block = "10.0.0.0/24"
public_subnet_cidr_block = {
  "eu-west-1a" = "10.0.0.0/26"
  "eu-west-1c" = "10.0.0.128/26"
}
domain_name                = "xccc.xgrid.co"
hosted_zone_id             = "Z053166920YP1STI0EK5X"
private_subnet_cidr_block  = "10.0.0.64/26"
allow_traffic              = ["39.46.215.160/32", "202.69.61.0/24"]
ses_email_address          = "xccc@xgrid.co"
creator_email              = "saman.batool@xgrid.co"
instance_type              = "t2.micro"
total_account_cost_lambda  = "total_account_cost"
total_account_cost_cronjob = "cron(0 0 1,15 * ? *)"
prometheus_layer           = "lambda_layers/python.zip"
memory_size                = 128
timeout                    = 300
project                    = "x-ccc"
security_group_ingress = {
  "pushgateway" = {
    description = "PushGateway"
    from_port   = 9091
    to_port     = 9091
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.64/26"]
  },
  "prometheus" = {
    description = "Prometheus"
    from_port   = 9000
    to_port     = 9000
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.64/26"]
  },
  "http" = {
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.64/26"]
  },
  "https" = {
    description = "HTTPS"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.64/26"]
  }
}

project = "x-ccc"
