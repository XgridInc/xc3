/*
Copyright (c) 2023, Xgrid Inc, https://xgrid.co

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

SPDX-License-Identifier: Apache-2.0
*/

// Terraform Module for Xgrid Cloud Cost Control

module "networking" {
  source = "./modules/networking"

  vpc_cidr_block            = var.vpc_cidr_block
  public_subnet_cidr_block  = var.public_subnet_cidr_block
  private_subnet_cidr_block = var.private_subnet_cidr_block
  allow_traffic             = var.allow_traffic
  security_group_ingress    = var.security_group_ingress
  namespace                 = var.namespace
  creator_email             = var.creator_email
  owner_email               = var.owner_email
  domain_name               = var.domain_name
  project                   = var.project
  env                       = var.env
}
// Terraform Module for Xgrid Cloud Cost Control

module "xc3" {
  source = "./modules/xc3"

  vpc_id              = module.networking.vpc_id
  private_subnet_id   = module.networking.private_subnet_id
  public_subnet_ids   = module.networking.public_subnet_ids
  security_group_ids  = module.networking.security_group_ids
  ses_email_address   = var.ses_email_address
  instance_type       = var.instance_type
  namespace           = var.namespace
  owner_email         = var.owner_email
  creator_email       = var.creator_email
  project             = var.project
  region              = var.region
  prometheus_layer    = var.prometheus_layer
  domain_name         = var.domain_name
  hosted_zone_id      = var.hosted_zone_id
  grafana_api_gateway = module.serverless.grafana_api_gateway
  env                 = var.env
  depends_on          = [module.networking]
}

// Terraform Module for Serverless Application
module "serverless" {
  source                     = "./modules/serverless"
  namespace                  = var.namespace
  owner_email                = var.owner_email
  creator_email              = var.creator_email
  project                    = var.project
  region                     = var.region
  subnet_id                  = module.networking.private_subnet_id
  security_group_id          = module.networking.security_group_ids.serverless_security_group_id
  s3_xc3_bucket              = module.xc3.s3_xc3_bucket
  sns_topic_arn              = module.xc3.sns_topic_arn
  prometheus_ip              = module.xc3.private_ip
  prometheus_layer           = module.xc3.prometheus_layer_arn
  timeout                    = var.timeout
  memory_size                = var.memory_size
  total_account_cost_lambda  = var.total_account_cost_lambda
  account_id                 = var.account_id
  total_account_cost_cronjob = var.total_account_cost_cronjob
  cron_jobs_schedule         = var.cron_jobs_schedule
  slack_channel_url          = var.slack_channel_url
  create_kms                 = var.create_kms

}
