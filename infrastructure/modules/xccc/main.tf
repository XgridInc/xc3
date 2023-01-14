# Assumption: An IAM role for EC2 might be given by the customer, 
# so we will be making the following logic dynamic


# Creating IAM Role for EC2 Instance 
resource "aws_iam_role" "this" {
  name = "xccc-sts-role"
  assume_role_policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Effect" : "Allow",
        "Principal" : {
          "Service" : "ec2.amazonaws.com"
        },
        "Action" : "sts:AssumeRole"
      }
    ]
  })
  managed_policy_arns = ["arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess", "arn:aws:iam::aws:policy/AmazonEC2ReadOnlyAccess"]
  tags = {
    Name = "XCCC-EC2-Role"
  }
}


# Creating EC2 Instance profile 

resource "aws_iam_instance_profile" "this" {
  name = "xccc-ec2-profile"
  role = aws_iam_role.this.name
  tags = {
    Name = "XCCC-EC2-Profile"
  }
}

# Creating EC2 Instance that will be hosting Cloud Custodian

resource "aws_instance" "this" {
  ami           = data.aws_ami_ids.ubuntu.id
  instance_type = var.instance_type

  key_name             = var.ssh_key
  subnet_id            = var.subnet_id
  security_groups      = [var.security_group_id]
  iam_instance_profile = aws_iam_instance_profile.this.name

  user_data = file("${path.module}/startup-script.sh")

  tags = {
    Name = "XCCC-EC2"
  }
}

resource "aws_key_pair" "this" {
  key_name   = "xccc-key"
  public_key = file("xccc-key.pub")
  tags       = { Name = "XCCC-SSH-KEY" }
}


# Configuring SES Identity and SQS for email notifications

resource "aws_ses_email_identity" "this" {
  email = var.ses_email_address
}

resource "aws_sqs_queue" "this" {
  name = var.sqs_queue_name
  tags = { Name = "XCCC-SQS-KEY" }
}
