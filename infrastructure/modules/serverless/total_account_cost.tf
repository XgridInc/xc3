locals {
  tags = {
    Owner   = var.owner_email
    Creator = var.creator_email
    Project = var.namespace
  }
}

data "archive_file" "total_account_cost" {
  type        = "zip"
  source_file = "../lambda_functions/budget_details/total_account_cost.py"
  output_path = "${path.module}/total_account_cost.zip"
}

# Creating IAM Role for Lambda functions
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
  tags                = merge(local.tags, tomap({ "Name" = "${local.tags.Project}-Total-Account-Cost-Role" }))

}

# Creating Inline policy
resource "aws_iam_role_policy" "total_account_cost" {
  name = "${var.total_account_cost_lambda}-ce-policy"
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
      }
    ]
  })
}

resource "aws_lambda_function" "total_account_cost" {
  function_name = var.total_account_cost_lambda
  role          = aws_iam_role.total_account_cost.arn
  runtime       = "python3.9"
  handler       = "${var.total_account_cost_lambda}.lambda_handler"
  filename      = data.archive_file.total_account_cost.output_path
  environment {
    variables = {
      prometheus_ip = "${var.prometheus_ip}:9091"
      account_id    = var.account_id
    }
  }
  memory_size = var.memory_size
  timeout     = var.timeout
  layers      = [var.prometheus_layer]
  vpc_config {
    subnet_ids         = [var.subnet_id]
    security_group_ids = [var.security_group_id]
  }
  tags = merge(local.tags, tomap({ "Name" = "${local.tags.Project}-total-account-cost" }))

}

resource "null_resource" "delete_zip_file" {
  triggers = {
    lambda_function_arn = aws_lambda_function.total_account_cost.arn
  }
  provisioner "local-exec" {
    command = "rm -r ${data.archive_file.total_account_cost.output_path}"
  }
}

# Define the EventBridge rule
resource "aws_cloudwatch_event_rule" "total_account_cost" {
  name                = "${var.total_account_cost_lambda}-rule"
  description         = "Trigger the Lambda function every two weeks"
  schedule_expression = var.total_account_cost_cronjob
  tags                = merge(local.tags, tomap({ "Name" = "${local.tags.Project}-total-account-cost-rule" }))
}


# Define the EventBridge target to invoke the Lambda function
resource "aws_cloudwatch_event_target" "total_account_cost" {
  rule = aws_cloudwatch_event_rule.total_account_cost.name
  arn  = aws_lambda_function.total_account_cost.arn
}
