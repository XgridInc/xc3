data "aws_ami" "ubuntu" {
  owners = ["099720109477"]

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-20220914"]
  }
}

data "aws_acm_certificate" "issued" {
  domain      = var.domain_name
  most_recent = true
  types       = ["AMAZON_ISSUED"]
  statuses    = ["ISSUED"]
  key_types   = ["RSA_2048"]
}
