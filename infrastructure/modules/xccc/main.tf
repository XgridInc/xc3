# Assumption: An IAM role for EC2 might be given by the customer, 
# So we will be making the following logic dynamic if IAM role is provided.


# Creating IAM Role for EC2 Instance 
resource "aws_iam_role" "this" {
  name = "${var.key}-sts-role"
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
    Name = "${var.namespace}-EC2-Role"
  }
}

# Creating EC2 Instance profile

resource "aws_iam_instance_profile" "this" {
  name = "${var.namespace}-ec2-profile"
  role = aws_iam_role.this.name
  tags = {
    Name = "${var.namespace}-EC2-Profile"
  }
}

# Creating EC2 Instance that will be hosting Cloud Custodian

resource "aws_instance" "this" {
  ami                         = data.aws_ami.ubuntu.id
  instance_type               = var.instance_type
  associate_public_ip_address = true
  key_name                    = aws_key_pair.this.key_name
  subnet_id                   = var.subnet_id
  security_groups             = [var.security_group_id]
  iam_instance_profile        = aws_iam_instance_profile.this.name

  user_data = file("${path.module}/startup-script.sh")

  tags = {
    Name = "${var.namespace}-EC2"
  }
}

resource "aws_key_pair" "this" {
  key_name   = "${var.key}-key"
  public_key = file("${var.key}-key.pub")
  tags       = { Name = "${var.namespace}-SSH-KEY" }
}

# Configuring SES Identity and SQS for email notifications

resource "aws_ses_email_identity" "this" {
  email = var.ses_email_address
}

resource "aws_sqs_queue" "this" {
  name = var.sqs_queue_name
  tags = { Name = "${var.namespace}-SQS-KEY" }
}
