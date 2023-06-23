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
# tflint-ignore: terraform_required_providers
data "archive_file" "total_account_cost" {
  type        = "zip"
  source_file = "../src/budget_details/total_account_cost.py"
  output_path = "${path.module}/total_account_cost.zip"
}

# Creating IAM Role for Lambda functions
# tflint-ignore: terraform_required_providers
resource "aws_iam_role" "total_account_cost" {
  name = "${var.namespace}-${var.total_account_cost_lambda}-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Sid    = "TotalAccountCost"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
  managed_policy_arns = ["arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"]
  tags                = merge(local.tags, tomap({ "Name" = "${var.namespace}-Total-Account-Cost-Role" }))

}

# Creating Inline policy
resource "aws_iam_role_policy" "total_account_cost" {
  name = "${var.namespace}-${var.total_account_cost_lambda}-ce-policy"
  role = aws_iam_role.total_account_cost.id
  policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Sid" : "TotalAccountCost",
        "Effect" : "Allow",
        "Action" : [
          "ce:GetCostAndUsage",
          "ec2:CreateNetworkInterface",
          "ec2:DescribeNetworkInterfaces",
          "ec2:DetachNetworkInterface",
          "ec2:AttachNetworkInterface",
          "ec2:DeleteNetworkInterface"
        ]
        "Resource" : "*"
      },
      {
        "Sid" : "SSMParameter",
        "Effect" : "Allow",
        "Action" : [
          "ssm:GetParameter"
        ]
        "Resource" : "arn:aws:ssm:*:*:parameter/*"
      },
      {
        "Effect" : "Allow",
        "Action" : [
          "s3:PutObject"
        ],
        "Resource" : [
          "arn:aws:s3:::${var.s3_xc3_bucket.id}/*"
        ]
      }
    ]
  })
}

resource "aws_lambda_function" "total_account_cost" {
  #ts:skip=AWS.LambdaFunction.LM.MEIDUM.0063 We are aware of the risk and choose to skip this rule
  #ts:skip=AWS.LambdaFunction.Logging.0470 We are aware of the risk and choose to skip this rule
  #ts:skip=AWS.LambdaFunction.EncryptionandKeyManagement.0471 We are aware of the risk and choose to skip this rule
  function_name = "${var.namespace}-${var.total_account_cost_lambda}"
  role          = aws_iam_role.total_account_cost.arn
  runtime       = "python3.9"
  handler       = "${var.total_account_cost_lambda}.lambda_handler"
  filename      = data.archive_file.total_account_cost.output_path
  environment {
    variables = {
      prometheus_ip       = "${var.prometheus_ip}:9091"
      account_detail      = var.namespace
      bucket_name         = var.s3_xc3_bucket.bucket
      monthly_cost_prefix = var.s3_prefixes.monthly_cost_prefix
    }
  }
  memory_size = var.memory_size
  timeout     = var.timeout
  layers      = [var.prometheus_layer]
  vpc_config {
    subnet_ids         = [var.subnet_id[0]]
    security_group_ids = [var.security_group_id]
  }
  tags = merge(local.tags, tomap({ "Name" = "${var.namespace}-total-account-cost" }))

}
# tflint-ignore: terraform_required_providers
resource "terraform_data" "delete_zip_file" {
  triggers_replace = [aws_lambda_function.total_account_cost.arn]
  provisioner "local-exec" {
    command = "rm -r ${data.archive_file.total_account_cost.output_path}"
  }
}

resource "aws_iam_policy" "total_account_cost" {
  name = "${var.namespace}-total_account_cost_eventbridge_policy"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "lambda:InvokeFunction"
        ]
        Effect   = "Allow"
        Resource = aws_lambda_function.total_account_cost.arn
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "total_account_cost" {
  policy_arn = aws_iam_policy.total_account_cost.arn
  role       = aws_iam_role.total_account_cost.name
}


# Define the EventBridge rule
resource "aws_cloudwatch_event_rule" "total_account_cost" {
  name                = "${var.namespace}-${var.total_account_cost_lambda}-rule"
  description         = "Trigger the Lambda function every two weeks"
  schedule_expression = var.total_account_cost_cronjob
  tags                = merge(local.tags, tomap({ "Name" = "${var.namespace}-total-account-cost-rule" }))
}


# Define the EventBridge target to invoke the Lambda function
resource "aws_cloudwatch_event_target" "total_account_cost" {
  rule = aws_cloudwatch_event_rule.total_account_cost.name
  arn  = aws_lambda_function.total_account_cost.arn
}

# tflint-ignore: terraform_required_providers
resource "aws_lambda_permission" "total_account_cost" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.total_account_cost.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.total_account_cost.arn
}
