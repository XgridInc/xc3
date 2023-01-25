locals {
  namespace = "XCCC"
  key       = "xccc"
}

// Terraform Module for Xgrid Cloud Cost Control

module "networking" {
  source = "./modules/networking"

  vpc_cidr_block         = var.vpc_cidr_block
  subnet1_cidr_block     = var.subnet1_cidr_block
  allow_traffic          = var.allow_traffic
  security_group_ingress = var.security_group_ingress
  namespace              = local.namespace
  key                    = local.key
}

// Terraform Module for Xgrid Cloud Cost Control

module "xccc" {
  source = "./modules/xccc"

  vpc_id            = module.networking.vpc_id
  subnet_id         = module.networking.subnet_id
  security_group_id = module.networking.security_group_id
  ses_email_address = var.ses_email_address
  sqs_queue_name    = var.sqs_queue_name
  ssh_key           = var.ssh_key
  instance_type     = var.instance_type
  namespace         = local.namespace
  key               = local.key
}
