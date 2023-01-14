// Terraform Remote State

terraform {
  backend "s3" {
    bucket     = "terraform-state-xccc"
    key        = "xccc/xccc.tfstate"
    region     = "eu-west-1"
    state-lock = "terraform-lock"
  }
}
