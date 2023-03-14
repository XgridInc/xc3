locals {
  tags = {
    Owner   = var.owner_email
    Creator = var.creator_email
    Project = var.namespace
  }
}
# Assumption: An IAM role for EC2 might be given by the customer,
# So we will be making the following logic dynamic if IAM role is provided. 
resource "aws_iam_role_policy" "this" {
  name = "${var.namespace}-sts-role-policy"
  role = aws_iam_role.this.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid = "IAMUserWorkflow"
        Action = [
          "s3:PutObject",
          "lambda:GetFunction",
          "lambda:CreateFunction",
          "lambda:InvokeFunction",
          "iam:PassRole",
          "lambda:TagResource",
          "lambda:GetFunctionConfiguration",
          "lambda:AddPermission",
          "events:DescribeRule",
          "events:PutRule",
          "events:PutTargets",
          "events:ListTargetsByRule",
          "lambda:UpdateFunctionCode",
          "events:ListRules"
        ]
        Effect = "Allow"
        Resource = [
          "arn:aws:s3:::${aws_s3_bucket.this.id}",
          "arn:aws:s3:::${aws_s3_bucket.this.id}/*",
          "arn:aws:lambda:*:*:function:*",
          "arn:aws:events:*:*:rule:*",
          "arn:aws:events:*:*:rule/*"
        ]
      },
      {
        Sid = "IAMUserAccess"
        Action = [
          "iam:ListUsers",
          "iam:GetUser",
          "iam:ListRoles",
          "iam:GetRole",
          "iam:ListAccountAliases"
        ]
        Effect   = "Allow"
        Resource = "*"
      }
    ]
  })
}

# Creating IAM Role for EC2 Instance
resource "aws_iam_role" "this" {
  name = "${var.namespace}-sts-role"
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
  managed_policy_arns = [
    "arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess",
    "arn:aws:iam::aws:policy/AmazonEC2ReadOnlyAccess",
    "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole",
    "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
  ]
  tags = merge(local.tags, tomap({ "Name" = "${local.tags.Project}-EC2-Role" }))
}

# Creating EC2 Instance profile

resource "aws_iam_instance_profile" "this" {
  name = "${var.namespace}-ec2-profile"
  role = aws_iam_role.this.name
  tags = merge(local.tags, tomap({ "Name" = "${local.tags.Project}-EC2-Profile" }))
}

# Creating EC2 Instance that will be hosting Cloud Custodian

resource "aws_instance" "this" {
  ami                         = data.aws_ami.ubuntu.id
  instance_type               = var.instance_type
  associate_public_ip_address = false
  key_name                    = aws_key_pair.this.key_name
  subnet_id                   = var.subnet_id
  vpc_security_group_ids      = [var.security_group_id]
  iam_instance_profile        = aws_iam_instance_profile.this.name
  user_data                   = file("${path.module}/startup-script.sh")

  tags = merge(local.tags, tomap({ "Name" = "${local.tags.Project}-EC2" }))
}

# Creating Bastion Host Server

resource "aws_instance" "bastion_host" {
  ami                         = data.aws_ami.ubuntu.id
  instance_type               = var.instance_type
  associate_public_ip_address = true
  key_name                    = aws_key_pair.this.key_name
  subnet_id                   = var.public_subnet_id
  vpc_security_group_ids      = [var.public_security_group_id]
  iam_instance_profile        = aws_iam_instance_profile.this.name

  tags = merge(local.tags, tomap({ "Name" = "${local.tags.Project}-Bastion-Host-Server" }))
}

resource "aws_key_pair" "this" {
  key_name   = var.ssh_key
  public_key = file("${var.ssh_key}.pub")
  tags       = merge(local.tags, tomap({ "Name" = "${local.tags.Project}-SSH-KEY" }))
}

# Configuring SES Identity and SQS for email notifications
resource "aws_ses_email_identity" "this" {
  email = var.ses_email_address

}

resource "aws_sqs_queue" "this" {
  name = "${var.namespace}-notification-queue"
  tags = merge(local.tags, tomap({ "Name" = "${local.tags.Project}-SQS-KEY" }))
}

#Configuring SNS for passing payload to lambda functions
resource "aws_sns_topic" "this" {
  name = "${var.namespace}-notification-topic"
  tags = merge(local.tags, tomap({ "Name" = "${local.tags.Project}-SNS-Topic" }))
}

#Configuring S3 bucket for storage of cloud custodian policies metadata
resource "aws_s3_bucket" "this" {
  bucket        = "${var.namespace}-metadata-storage"
  force_destroy = false
  tags          = merge(local.tags, tomap({ "Name" = "${local.tags.Project}-Bucket" }))
}

# Uploading Cloud Custodian Policies and lambda layers in S3 bucket
resource "null_resource" "upload_files_on_s3" {
  triggers = {
    s3_bucket = aws_s3_bucket.this.arn
  }

  provisioner "local-exec" {
    command = <<EOT
      aws s3 cp ../cloud_custodian_policies/ s3://${aws_s3_bucket.this.id}/cloud_custodian_policies/  --recursive
      aws s3 cp python.zip s3://${aws_s3_bucket.this.id}/lambda_layers/
      aws s3 cp layer-mysql-prometheus.zip s3://${aws_s3_bucket.this.id}/lambda_layers/
   EOT
  }
}

# Configuring prometheus layer for lambda functions
resource "aws_lambda_layer_version" "lambda_layer_prometheus" {
  s3_bucket  = aws_s3_bucket.this.id
  s3_key     = var.prometheus_layer
  layer_name = "${var.namespace}-prometheus_layer"

  compatible_runtimes = ["python3.9"]
  depends_on = [
    null_resource.upload_files_on_s3
  ]
}

# Configuring mysql layer for lambda functions
resource "aws_lambda_layer_version" "lambda_layer_mysql" {
  s3_bucket  = aws_s3_bucket.this.id
  s3_key     = var.mysql_layer
  layer_name = "${var.namespace}-mysql_layer"

  compatible_runtimes = ["python3.9"]
  depends_on = [
    null_resource.upload_files_on_s3
  ]
}
