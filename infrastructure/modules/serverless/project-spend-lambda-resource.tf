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

data "archive_file" "project_spend_cost" {
  type        = "zip"
  source_file = "../src/budget_details/project_spend_cost.py"
  output_path = "${path.module}/project_spend_cost.zip"
}


# Creating Inline policy
resource "aws_iam_role_policy" "ProjectSpendCost" {
  name = "${var.namespace}-lambda-inline-policy"
  role = aws_iam_role.ProjectSpendCost.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid = "CostExplorerAccess"
        Action = [
          "aws-portal:ViewBilling",
          "ce:GetCostAndUsage",
          "ec2:DescribeInstances",
          "ec2:CreateNetworkInterface",
          "ec2:DescribeNetworkInterfaces",
          "ec2:DeleteNetworkInterface",
          "ec2:AttachNetworkInterface"
        ]
        Effect   = "Allow"
        Resource = "*"
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

# Creating IAM Role for Lambda functions
resource "aws_iam_role" "ProjectSpendCost" {
  name = "${var.namespace}-project-spend-cost-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Sid    = "projectspendcostrole"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
  managed_policy_arns = []
  tags                = merge(local.tags, tomap({ "Name" = "${var.namespace}-Project-Spend-Cost-Role" }))
}

resource "aws_lambda_function" "ProjectSpendCost" {
  #ts:skip=AWS.LambdaFunction.LM.MEIDUM.0063 We are aware of the risk and choose to skip this rule
  #ts:skip=AWS.LambdaFunction.Logging.0470 We are aware of the risk and choose to skip this rule
  #ts:skip=AWS.LambdaFunction.EncryptionandKeyManagement.0471 We are aware of the risk and choose to skip this rule
  function_name = "${var.namespace}-project-spend-cost"
  role          = aws_iam_role.ProjectSpendCost.arn
  runtime       = "python3.9"
  handler       = "project_spend_cost.lambda_handler"
  filename      = data.archive_file.project_spend_cost.output_path
  environment {
    variables = {
      prometheus_ip        = "${var.prometheus_ip}:9091"
      bucket_name          = var.s3_xc3_bucket.bucket
      project_spend_prefix = var.s3_prefixes.project_spend_prefix
    }
  }
  memory_size = var.memory_size
  timeout     = var.timeout
  layers      = [var.prometheus_layer]

  vpc_config {
    subnet_ids         = [var.subnet_id[0]]
    security_group_ids = [var.security_group_id]
  }

  tags = merge(local.tags, tomap({ "Name" = "${var.namespace}-project_cost_function" }))

}


resource "terraform_data" "delete_project_spend_cost_zip_file" {
  triggers_replace = [aws_lambda_function.ProjectSpendCost.arn]
  provisioner "local-exec" {
    command = "rm -r ${data.archive_file.project_spend_cost.output_path}"
  }
}

# Define the EventBridge rule
resource "aws_cloudwatch_event_rule" "project_spend_cost" {
  name                = "${var.namespace}-project-spend-cost-rule"
  description         = "Trigger the Lambda function every two weeks"
  schedule_expression = var.total_account_cost_cronjob
  tags                = merge(local.tags, tomap({ "Name" = "${var.namespace}-project-spend-cost-rule" }))
}


# Define the EventBridge target to invoke the Lambda function
resource "aws_cloudwatch_event_target" "project_spend_cost" {
  rule = aws_cloudwatch_event_rule.project_spend_cost.name
  arn  = aws_lambda_function.ProjectSpendCost.arn
}

resource "aws_iam_policy" "eventbridge_policy" {
  name = "${var.namespace}-eventbridge_policy"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "lambda:InvokeFunction"
        ]
        Effect   = "Allow"
        Resource = [aws_lambda_function.ProjectSpendCost.arn]
      }
    ]
  })
}
resource "aws_iam_role_policy_attachment" "eventbridge_policy_attachment" {
  policy_arn = aws_iam_policy.eventbridge_policy.arn
  role       = aws_iam_role.ProjectSpendCost.name
}

resource "aws_lambda_permission" "project_spend" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.ProjectSpendCost.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.project_spend_cost.arn
}
