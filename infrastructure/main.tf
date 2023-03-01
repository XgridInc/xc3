locals {
  namespace   = "X-CCC"
  owner_email = "xccc@xgrid.co"
  key         = "xccc"
}

// Terraform Module for Xgrid Cloud Cost Control

module "networking" {
  source = "./modules/networking"

  vpc_cidr_block            = var.vpc_cidr_block
  public_subnet_cidr_block  = var.public_subnet_cidr_block
  private_subnet_cidr_block = var.private_subnet_cidr_block
  security_group_ingress    = var.security_group_ingress
  namespace                 = local.namespace
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
  namespace                = local.namespace
  key                      = local.key
  owner_email              = local.owner_email
  creator_email            = var.creator_email
}
