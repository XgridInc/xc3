locals {
  owner_email = "xccc@xgrid.co"
  key         = "xccc"
}

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
  owner_email               = local.owner_email
  key                       = local.key
}

// Terraform Module for Xgrid Cloud Cost Control

module "xccc" {
  source = "./modules/xccc"

  vpc_id                   = module.networking.vpc_id
  subnet_id                = module.networking.private_subnet_id
  public_subnet_id         = module.networking.public_subnet_id
  security_group_id        = module.networking.private_security_group_id
  public_security_group_id = module.networking.public_security_group_id
  ses_email_address        = var.ses_email_address
  sqs_queue_name           = var.sqs_queue_name
  ssh_key                  = var.ssh_key
  instance_type            = var.instance_type
  namespace                = var.namespace
  key                      = local.key
  owner_email              = local.owner_email
  creator_email            = var.creator_email
  region                   = var.region
  sns_topic_name           = var.sns_topic_name
  s3_xccc_bucket           = var.s3_xccc_bucket
  prometheus_layer         = var.prometheus_layer
  mysql_layer              = var.mysql_layer
  username                 = var.username
  password                 = var.password
}

// Terraform Module for Serverless Application
module "serverless" {
  source                     = "./modules/serverless"
  namespace                  = var.namespace
  owner_email                = local.owner_email
  creator_email              = var.creator_email
  total_account_cost_lambda  = var.total_account_cost_lambda
  subnet_id                  = module.networking.private_subnet_id
  security_group_id          = module.networking.serverless_security_group_id
  prometheus_ip              = module.xccc.private_ip
  prometheus_layer           = module.xccc.prometheus_layer_arn
  timeout                    = var.timeout
  memory_size                = var.memory_size
  account_id                 = var.account_id
  total_account_cost_cronjob = var.total_account_cost_cronjob
}
