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

data "archive_file" "lambda_function_listusers_zip" {
  type        = "zip"
  source_file = "../src/iam_users/list_iam_users.py"
  output_path = "${path.module}/list_iam_users.zip"

}

data "archive_file" "lambda_function_listcost_zip" {
  type        = "zip"
  source_file = "../src/iam_users/list_iam_user_resources_cost.py"
  output_path = "${path.module}/list_iam_user_resources_cost.zip"

}

# Creating Inline policy
resource "aws_iam_role_policy" "this" {
  name = "${var.namespace}-iam-user-workflow-policy"
  role = aws_iam_role.lambda_execution_role.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid = "CostExplorer"
        Action = [
          "ce:GetCostAndUsage",
          "ec2:CreateNetworkInterface",
          "ec2:DescribeNetworkInterfaces",
          "ec2:DetachNetworkInterface",
          "ec2:AttachNetworkInterface",
          "ec2:DeleteNetworkInterface",
          "SNS:Publish"
        ]
        Effect   = "Allow"
        Resource = "*"
      }
    ]
  })
}

# Creating IAM Role for Lambda functions
resource "aws_iam_role" "lambda_execution_role" {
  name = "${var.namespace}-iam-user-workflow-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Sid    = ""
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
  managed_policy_arns = [
    "arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess",
    "arn:aws:iam::aws:policy/ResourceGroupsandTagEditorReadOnlyAccess",
    "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole",
    "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
  ]

  tags = merge(local.tags, tomap({ "Name" = "${var.namespace}-IAM-User-Lambda-Role" }))
}

resource "aws_lambda_function" "resources_cost_iam_user" {
  #ts:skip=AC_AWS_0485 We are aware of the risk and choose to skip this rule
  #ts:skip=AC_AWS_0483 We are aware of the risk and choose to skip this rule
  #ts:skip=AC_AWS_0484 We are aware of the risk and choose to skip this rule
  function_name = "${var.namespace}-list_iam_user_resources_cost"
  role          = aws_iam_role.lambda_execution_role.arn
  runtime       = "python3.9"
  handler       = "list_iam_user_resources_cost.lambda_handler"
  filename      = data.archive_file.lambda_function_listcost_zip.output_path
  environment {
    variables = {
      prometheus_ip = "${var.prometheus_ip}:9091"
    }
  }
  memory_size = var.memory_size
  timeout     = var.timeout
  layers      = [var.prometheus_layer]
  vpc_config {
    subnet_ids         = [var.subnet_id[0]]
    security_group_ids = [var.security_group_id]
  }
  depends_on = [
    aws_lambda_function.list_iam_user
  ]
  tags = merge(local.tags, tomap({ "Name" = "${var.namespace}-list_resources_cost_metrics" }))

}

resource "terraform_data" "delete_iamuser_zip_file" {
  triggers_replace = [aws_lambda_function.list_iam_user.arn]
  provisioner "local-exec" {
    command = "rm -r ${data.archive_file.lambda_function_listusers_zip.output_path}"
  }
}

resource "terraform_data" "delete_cost_zip_file" {
  triggers_replace = [aws_lambda_function.resources_cost_iam_user.arn]
  provisioner "local-exec" {
    command = "rm -r ${data.archive_file.lambda_function_listcost_zip.output_path}"
  }
}

resource "aws_lambda_function" "list_iam_user" {
  #ts:skip=AC_AWS_0484 We are aware of the risk and choose to skip this rule
  #ts:skip=AC_AWS_0485 We are aware of the risk and choose to skip this rule
  #ts:skip=AC_AWS_0483 We are aware of the risk and choose to skip this rule
  function_name = "${var.namespace}-list_iam_users"
  role          = aws_iam_role.lambda_execution_role.arn
  runtime       = "python3.9"
  handler       = "list_iam_users.lambda_handler"
  filename      = data.archive_file.lambda_function_listusers_zip.output_path
  environment {
    variables = {
      prometheus_ip = "${var.prometheus_ip}:9091"
      REGION        = var.region
      sns_topic     = var.sns_topic_arn

    }
  }
  memory_size = var.memory_size
  timeout     = var.timeout
  layers      = [var.prometheus_layer]
  vpc_config {
    subnet_ids         = [var.subnet_id[0]]
    security_group_ids = [var.security_group_id]
  }
  tags = merge(local.tags, tomap({ "Name" = "${var.namespace}-list_iam_user" }))
}

resource "aws_lambda_permission" "allow_bucket_for_trigger" {
  statement_id  = "AllowExecutionFromS3Bucket"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.list_iam_user.arn
  principal     = "s3.amazonaws.com"
  source_arn    = var.s3_xc3_bucket.arn
}

resource "aws_s3_bucket_notification" "list_iam_user_trigger" {
  bucket = var.s3_xc3_bucket.id
  lambda_function {
    lambda_function_arn = aws_lambda_function.list_iam_user.arn
    filter_prefix       = "iam-user/"
    events              = ["s3:ObjectCreated:Put"]
    filter_suffix       = "resources.json.gz"
  }
}

resource "aws_sns_topic_subscription" "invoke_with_sns" {
  topic_arn = var.sns_topic_arn
  protocol  = "lambda"
  endpoint  = aws_lambda_function.resources_cost_iam_user.arn
}

resource "aws_lambda_permission" "allow_sns_invoke" {
  statement_id  = "AllowExecutionFromSNS"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.resources_cost_iam_user.arn
  principal     = "sns.amazonaws.com"
  source_arn    = var.sns_topic_arn
}
