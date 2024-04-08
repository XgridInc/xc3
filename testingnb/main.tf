# Module Declaration
# ------------------
# This declares the usage of the "serverless" module to provision serverless resources.

module "serverless" {
  # Module Source
  # -------------
  # Specifies the path to the directory containing the Terraform configuration for the "serverless" module.
  source = "./modules/serverless"

  region = var.region
  Owner = var.Owner
  Creator = var.Creator
  Project = var.Project
  snsendpoint = var.snsendpoint
  slack_webhook_url = var.slack_webhook_url
  namespace = var.namespace
}
