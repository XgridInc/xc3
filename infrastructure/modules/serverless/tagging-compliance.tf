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

data "archive_file" "resource_list_archive" {
  type        = "zip"
  source_file = "../src/tagging-compliance/resource_list.py"
  output_path = "${path.module}/resource_list.zip"
}

data "archive_file" "resource_parsing_archive" {
  type        = "zip"
  source_file = "../src/tagging-compliance/resource_parsing.py"
  output_path = "${path.module}/resource_parsing.zip"
}

# Creating IAM Role for Lambda functions
resource "aws_iam_role" "resource_list_service_role" {
  name = "${var.namespace}-resource_list_service_role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Sid    = "ResourceListPermission"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
  managed_policy_arns = [
    "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole",
    "arn:aws:iam::aws:policy/ResourceGroupsandTagEditorReadOnlyAccess",
    "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"
  ]
  tags = merge(local.tags, tomap({ "Name" = "${var.namespace}-resource_list_service_role" }))

}

# Creating Inline policy
resource "aws_iam_role_policy" "resource_list_service_policy" {
  name = "${var.namespace}-resource_list_service_policy"
  role = aws_iam_role.resource_list_service_role.id
  policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Sid" : "ResourceList",
        "Effect" : "Allow",
        "Action" : [
          "ec2:CreateNetworkInterface",
          "ec2:DescribeNetworkInterfaces",
          "ec2:DetachNetworkInterface",
          "ec2:AttachNetworkInterface",
          "ec2:DeleteNetworkInterface",
          "ec2:DescribeRegions"
        ]
        "Resource" : "*"
      },
      {
        "Sid" : "LambdaInvokePermission",
        "Effect" : "Allow",
        "Action" : [
          "lambda:InvokeFunction"
        ]
        "Resource" : ["arn:aws:lambda:*:*:function:*"]
      }
    ]
  })
}

resource "aws_lambda_function" "resource_list_function" {
  #ts:skip=AWS.LambdaFunction.LM.MEIDUM.0063 We are aware of the risk and choose to skip this rule
  #ts:skip=AWS.LambdaFunction.Logging.0470 We are aware of the risk and choose to skip this rule
  #ts:skip=AWS.LambdaFunction.EncryptionandKeyManagement.0471 We are aware of the risk and choose to skip this rule
  function_name = "${var.namespace}-resource_list_lambda"
  role          = aws_iam_role.resource_list_service_role.arn
  runtime       = "python3.9"
  handler       = "resource_list.lambda_handler"
  filename      = data.archive_file.resource_list_archive.output_path
  environment {
    variables = {
      resource_list_lambda_function = aws_lambda_function.resource_parsing_function.arn
    }
  }
  memory_size = var.memory_size
  timeout     = var.timeout
  vpc_config {
    subnet_ids         = [var.subnet_id[0]]
    security_group_ids = [var.security_group_id]
  }
  tags = merge(local.tags, tomap({ "Name" = "${var.namespace}-resource_list_lambda" }))

}

resource "aws_lambda_function" "resource_parsing_function" {
  #ts:skip=AWS.LambdaFunction.LM.MEIDUM.0063 We are aware of the risk and choose to skip this rule
  #ts:skip=AWS.LambdaFunction.Logging.0470 We are aware of the risk and choose to skip this rule
  #ts:skip=AWS.LambdaFunction.EncryptionandKeyManagement.0471 We are aware of the risk and choose to skip this rule
  function_name = "${var.namespace}-resource_parsing_lambda"
  role          = aws_iam_role.resource_list_service_role.arn
  runtime       = "python3.9"
  handler       = "resource_parsing.lambda_handler"
  filename      = data.archive_file.resource_parsing_archive.output_path
  environment {
    variables = {
      prometheus_ip = "${var.prometheus_ip}:9091"
      account_id    = var.account_id
      tagging_list  = jsonencode(keys(local.tags))
    }
  }
  memory_size = var.memory_size
  timeout     = var.timeout
  layers      = [var.prometheus_layer]
  vpc_config {
    subnet_ids         = [var.subnet_id[0]]
    security_group_ids = [var.security_group_id]
  }
  tags = merge(local.tags, tomap({ "Name" = "${var.namespace}-resource_parsing_lambda" }))

}

resource "terraform_data" "delete_resource_list_zip_file" {
  triggers_replace = [aws_lambda_function.resource_list_function.arn]
  provisioner "local-exec" {
    command = "rm -r ${data.archive_file.resource_list_archive.output_path}"
  }
}

resource "terraform_data" "delete_resource_parsing_zip_file" {
  triggers_replace = [aws_lambda_function.resource_parsing_function.arn]
  provisioner "local-exec" {
    command = "rm -r ${data.archive_file.resource_parsing_archive.output_path}"
  }
}

resource "aws_iam_policy" "this" {
  name = "${var.namespace}-resource_list_eventbridge_policy"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "lambda:InvokeFunction"
        ]
        Effect   = "Allow"
        Resource = aws_lambda_function.resource_list_function.arn
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "this" {
  policy_arn = aws_iam_policy.this.arn
  role       = aws_iam_role.resource_list_service_role.name
}

# Define the EventBridge rule
resource "aws_cloudwatch_event_rule" "resource_list" {
  name                = "${var.namespace}-resource-list-rule"
  description         = "Trigger the Lambda function every week on Monday"
  schedule_expression = var.cron_jobs_schedule["resource_list_function_cron"]
  tags                = merge(local.tags, tomap({ "Name" = "${var.namespace}-resource-list" }))
}


# Define the EventBridge target to invoke the Lambda function
resource "aws_cloudwatch_event_target" "resource_list" {
  rule = aws_cloudwatch_event_rule.resource_list.name
  arn  = aws_lambda_function.resource_list_function.arn
}

resource "aws_lambda_permission" "resource_list" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.resource_list_function.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.resource_list.arn
}
