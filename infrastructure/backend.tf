// Terraform Remote State

terraform {
  backend "s3" {
    bucket         = "terraform-state-xccc"
    key            = "xccc/xccc.tfstate"
    region         = "eu-west-1"
    dynamodb_table = "terraform-lock"
  }
}
