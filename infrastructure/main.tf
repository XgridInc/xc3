// Terraform Module for Xgrid Cloud Cost Control

module "xccc" {
  source = "./modules/xccc"

  region            = var.region
  vpc_id            = var.vpc_id
  subnet_id         = var.subnet_id
  security_group_id = var.security_group_id
  ses_email_address = var.ses_email_address
  sqs_queue_name    = var.sqs_queue_name
  ssh_key           = var.ssh_key
  instance_type     = var.instance_type
}
