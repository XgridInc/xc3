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

data "archive_file" "list_linked_accounts" {
  type        = "zip"
  source_file = "../src/organization/list_linked_accounts.py"
  output_path = "${path.module}/list_linked_accounts.zip"
}

# Creating IAM Role for Lambda functions
resource "aws_iam_role" "list_linked_accounts" {
  name = "${var.namespace}-list-linked-accounts-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Sid    = "ListLinkedAccounts"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
  managed_policy_arns = ["arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"]
  tags                = merge(local.tags, tomap({ "Name" = "${var.namespace}-list_linked_accounts-Role" }))

}

# Creating Inline policy
resource "aws_iam_role_policy" "list_linked_accounts" {
  name = "${var.namespace}-list-linked-accounts-policy"
  role = aws_iam_role.list_linked_accounts.id
  policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Sid" : "lambdaAllowListAccounts",
        "Action" : [
          "organizations:ListAWSServiceAccessForOrganization",
          "organizations:ListAccounts",
          "organizations:ListAccountsForParent",
          "organizations:ListChildren",
          "ec2:CreateNetworkInterface",
          "ec2:DescribeNetworkInterfaces",
          "ec2:DetachNetworkInterface",
          "ec2:AttachNetworkInterface",
          "ec2:DeleteNetworkInterface",
          "ec2:DescribeRegions",
          "organizations:DescribeOrganization"
        ],
        "Effect" : "Allow",
        "Resource" : "*"
      },
      {
        "Sid" : "SSMParameter",
        "Effect" : "Allow",
        "Action" : [
          "ssm:PutParameter"
        ],
        "Resource" : "arn:aws:ssm:*:*:parameter/*"
      }
    ]
  })
}

resource "aws_lambda_function" "list_linked_accounts" {
  #ts:skip=AWS.LambdaFunction.LM.MEIDUM.0063 We are aware of the risk and choose to skip this rule
  #ts:skip=AWS.LambdaFunction.Logging.0470 We are aware of the risk and choose to skip this rule
  #ts:skip=AWS.LambdaFunction.EncryptionandKeyManagement.0471 We are aware of the risk and choose to skip this rule
  function_name = "${var.namespace}-list_linked_accounts"
  role          = aws_iam_role.list_linked_accounts.arn
  runtime       = "python3.9"
  handler       = "list_linked_accounts.lambda_handler"
  filename      = data.archive_file.list_linked_accounts.output_path
  environment {
    variables = {
      account_detail = var.namespace
    }
  }
  memory_size = var.memory_size
  timeout     = var.timeout
  vpc_config {
    subnet_ids         = [var.subnet_id[0]]
    security_group_ids = [var.security_group_id]
  }
  tags = merge(local.tags, tomap({ "Name" = "${var.namespace}-list_linked_accounts" }))

}

resource "terraform_data" "list_linked_accounts" {
  triggers_replace = [aws_lambda_function.list_linked_accounts.arn]
  provisioner "local-exec" {
    command = "rm -r ${data.archive_file.list_linked_accounts.output_path}"
  }
}

resource "aws_iam_policy" "list_linked_accounts" {
  name = "${var.namespace}-list_linked_accounts_eventbridge_policy"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "lambda:InvokeFunction"
        ]
        Effect   = "Allow"
        Resource = aws_lambda_function.list_linked_accounts.arn
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "list_linked_accounts" {
  policy_arn = aws_iam_policy.list_linked_accounts.arn
  role       = aws_iam_role.list_linked_accounts.name
}


# Define the EventBridge rule
resource "aws_cloudwatch_event_rule" "list_linked_accounts" {
  name                = "${var.namespace}-list-linked-account-rule"
  description         = "Trigger the Lambda function once in a month"
  schedule_expression = var.cron_jobs_schedule["list_linked_accounts_cron"]
  tags                = merge(local.tags, tomap({ "Name" = "${var.namespace}-list_linked_accounts-rule" }))
}


# Define the EventBridge target to invoke the Lambda function
resource "aws_cloudwatch_event_target" "list_linked_accounts" {
  rule = aws_cloudwatch_event_rule.list_linked_accounts.name
  arn  = aws_lambda_function.list_linked_accounts.arn
}

resource "aws_lambda_permission" "list_linked_accounts" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.list_linked_accounts.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.list_linked_accounts.arn
}
