# Copyright (c) 2023, Xgrid Inc, https://xgrid.co

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#        http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

locals {
  tags = {
    Owner   = var.owner_email
    Creator = var.creator_email
    Project = var.project
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
          "arn:aws:events:*:*:rule/*",
          "arn:aws:iam::*:role/onboarding-custodian-role"
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
  tags = merge(local.tags, tomap({ "Name" = "${var.namespace}-EC2-Role" }))
}

# Creating EC2 Instance profile

resource "aws_iam_instance_profile" "this" {
  name = "${var.namespace}-ec2-profile"
  role = aws_iam_role.this.name
  tags = merge(local.tags, tomap({ "Name" = "${var.namespace}-EC2-Profile" }))
}


# Creating EC2 Instance that will be hosting Cloud Custodian

resource "aws_instance" "this" {
  #ts:skip=AC-AWS-NS-IN-M-1172 We are aware of the risk and choose to skip this rule
  #ts:skip=AWS.AI.LM.HIGH.0070 We are aware of the risk and choose to skip this rule
  ami                         = data.aws_ami.ubuntu.id
  instance_type               = var.instance_type
  associate_public_ip_address = var.env == "prod" ? false : true
  key_name                    = data.aws_key_pair.key_pair.key_name
  subnet_id                   = var.public_subnet_ids[0]
  vpc_security_group_ids      = [var.security_group_ids.private_security_group_id]
  iam_instance_profile        = aws_iam_instance_profile.this.name
  user_data = templatefile("${path.module}/startup-script.sh.tpl", {
    env_file = var.domain_name != "" ? templatefile(
      "${path.module}/.env-grafana.tpl",
      {
        client_id        = aws_cognito_user_pool_client.grafana_client[0].id,
        client_secret    = aws_cognito_user_pool_client.grafana_client[0].client_secret,
        domain_name      = var.domain_name,
        user_pool_domain = aws_cognito_user_pool_domain.main[0].domain,
        region           = var.region
      }
    ) : " ",
    datasource          = file("${path.module}/datasource.yml"),
    dashboard           = file("${path.module}/dashboard.yml"),
    grafana_api_gateway = var.grafana_api_gateway,
    region              = var.region
    s3_bucket           = aws_s3_bucket.this.id
    }
  )

  root_block_device {
    volume_size = 30
    encrypted   = true
  }

  tags = merge(local.tags, tomap({ "Name" = "${var.namespace}-EC2" }))
}

# Configuring SES Identity and SQS for email notifications
resource "aws_ses_email_identity" "this" {
  email = var.ses_email_address

}

resource "aws_sqs_queue" "this" {
  #ts:skip=AWS.SQS.NetworkSecurity.High.0570 We are aware of the risk and choose to skip this rule
  name = "${var.namespace}-notification-queue"
  tags = merge(local.tags, tomap({ "Name" = "${var.namespace}-SQS-KEY" }))
}

#Configuring SNS for passing payload to lambda functions
resource "aws_sns_topic" "this" {
  #ts:skip=AWS.AST.DP.MEDIUM.0037 We are aware of the risk and choose to skip this rule
  name = "${var.namespace}-notification-topic"
  tags = merge(local.tags, tomap({ "Name" = "${var.namespace}-SNS-Topic" }))
}

#Configuring S3 bucket for storage of cloud custodian policies metadata
resource "aws_s3_bucket" "this" {
  #ts:skip=AWS.S3Bucket.IAM.High.0370
  bucket        = "${var.namespace}-metadata-storage"
  force_destroy = false
  lifecycle {
    ignore_changes = all
  }
  tags = merge(local.tags, tomap({ "Name" = "${var.namespace}-Bucket" }))
}

# Uploading Cloud Custodian Policies and lambda layers in S3 bucket
# tflint-ignore: terraform_required_providers
resource "terraform_data" "upload_files_on_s3" {
  triggers_replace = [aws_s3_bucket.this.arn]

  provisioner "local-exec" {
    command = <<EOT
      aws s3 cp python.zip s3://${aws_s3_bucket.this.id}/lambda_layers/
      aws s3 cp ../custom_dashboard/grafana_dashboards/. s3://${aws_s3_bucket.this.id}/content/ --recursive --exclude "*.md"
      aws s3 cp ../cloud_custodian_policies/ s3://${aws_s3_bucket.this.id}/cloud_custodian_policies/ --recursive --exclude "*.md" --include "*"
   EOT
  }
}

# tflint-ignore: terraform_required_providers
resource "terraform_data" "eicendpoint" {
  count = var.env == "prod" ? 1 : 0
  triggers_replace = [
    aws_instance.this.id
  ]
  provisioner "local-exec" {
    command = "aws ec2 create-instance-connect-endpoint --subnet-id ${var.private_subnet_id[0]} --security-group-id ${var.security_group_ids.private_security_group_id}"
  }
}

# Configuring prometheus layer for lambda functions
# tflint-ignore: terraform_required_providers
resource "aws_lambda_layer_version" "lambda_layer_prometheus" {
  s3_bucket  = aws_s3_bucket.this.id
  s3_key     = var.prometheus_layer
  layer_name = "${var.namespace}-prometheus_layer"

  compatible_runtimes = ["python3.9"]
  depends_on = [
    terraform_data.upload_files_on_s3
  ]
}
