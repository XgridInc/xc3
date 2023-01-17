data "aws_ami_ids" "ubuntu" {
  owners = ["self"]

  filter {
    name   = "xccc-ec2-ami-id"
    values = ["ubuntu/images/ubuntu-*-*-amd64-server-*"]
  }
}
