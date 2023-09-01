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

#Creating archive files
locals {
  project_lambda_archive = {
    project_spend_cost = {
      source_file = "../src/budget_details/project_spend_cost.py"
      output_path = "${path.module}/project_spend_cost.zip"
    }
    project_cost_breakdown = {
      source_file = "../src/budget_details/project_cost_breakdown.py"
      output_path = "${path.module}/project_cost_breakdown.zip"
    }
  }
}

data "archive_file" "project_cost_lambda_src" {
  for_each    = local.project_lambda_archive
  type        = "zip"
  source_file = each.value.source_file
  output_path = each.value.output_path
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
        "Sid" : "LambdaInvokePermission",
        "Effect" : "Allow",
        "Action" : [
          "lambda:InvokeFunction"
        ],
        "Resource" : [
          "arn:aws:lambda:*:*:function:*"
        ]
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

resource "aws_lambda_function" "ProjectCostBreakdown" {
  #ts:skip=AWS.LambdaFunction.LM.MEIDUM.0063 We are aware of the risk and choose to skip this rule
  #ts:skip=AWS.LambdaFunction.Logging.0470 We are aware of the risk and choose to skip this rule
  #ts:skip=AWS.LambdaFunction.EncryptionandKeyManagement.0471 We are aware of the risk and choose to skip this rule
  function_name = "${var.namespace}-project-cost-breakdown"
  role          = aws_iam_role.ProjectSpendCost.arn
  runtime       = "python3.9"
  handler       = "project_cost_breakdown.lambda_handler"
  filename      = values(data.archive_file.project_cost_lambda_src)[0].output_path
  environment {
    variables = {
      prometheus_ip                 = "${var.prometheus_ip}:9091"
      bucket_name                   = var.s3_xc3_bucket.bucket
      project_cost_breakdown_prefix = var.s3_prefixes.project_cost_breakdown_prefix
    }
  }
  layers      = [var.prometheus_layer]
  memory_size = var.memory_size
  timeout     = var.timeout
  vpc_config {
    subnet_ids         = [var.subnet_id[0]]
    security_group_ids = [var.security_group_id]
  }
  tags = merge(local.tags, tomap({ "Name" = "${var.namespace}-project_cost_breakdown" }))

}

resource "aws_lambda_function" "ProjectSpendCost" {
  #ts:skip=AWS.LambdaFunction.LM.MEIDUM.0063 We are aware of the risk and choose to skip this rule
  #ts:skip=AWS.LambdaFunction.Logging.0470 We are aware of the risk and choose to skip this rule
  #ts:skip=AWS.LambdaFunction.EncryptionandKeyManagement.0471 We are aware of the risk and choose to skip this rule
  function_name = "${var.namespace}-project-spend-cost"
  role          = aws_iam_role.ProjectSpendCost.arn
  runtime       = "python3.9"
  handler       = "project_spend_cost.lambda_handler"
  filename      = values(data.archive_file.project_cost_lambda_src)[1].output_path
  environment {
    variables = {
      prometheus_ip        = "${var.prometheus_ip}:9091"
      bucket_name          = var.s3_xc3_bucket.bucket
      project_spend_prefix = var.s3_prefixes.project_spend_prefix
      lambda_function_name = aws_lambda_function.ProjectCostBreakdown.arn
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


resource "terraform_data" "delete_project_lambda_zip_files" {
  for_each         = local.project_lambda_archive
  triggers_replace = ["arn:aws:lambda:${var.region}:${var.account_id}:function:${each.key}"]
  depends_on       = [aws_lambda_function.ProjectCostBreakdown, aws_lambda_function.ProjectSpendCost]

  provisioner "local-exec" {
    command = "rm -rf ${each.value.output_path}"
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
