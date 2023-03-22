locals {
  tag_filter = {
    Owner   = var.owner_email
    Creator = var.creator_email
    Project = var.namespace
  }
}

data "archive_file" "resource_list_archive" {
  type        = "zip"
  source_file = "../lambda_functions/xmop-services/resource_list.py"
  output_path = "${path.module}/resource_list.zip"
}

data "archive_file" "resource_parsing_archive" {
  type        = "zip"
  source_file = "../lambda_functions/xmop-services/resource_parsing.py"
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
  tags = merge(local.tag_name, tomap({ "Name" = "${local.tag_name.Project}-resource_list_service_role" }))

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
    subnet_ids         = [var.subnet_id]
    security_group_ids = [var.security_group_id]
  }
  tags = merge(local.tag_name, tomap({ "Name" = "${local.tag_name.Project}-resource_list_lambda" }))

}

resource "aws_lambda_function" "resource_parsing_function" {
  function_name = "${var.namespace}-resource_parsing_lambda"
  role          = aws_iam_role.resource_list_service_role.arn
  runtime       = "python3.9"
  handler       = "resource_parsing.lambda_handler"
  filename      = data.archive_file.resource_parsing_archive.output_path
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
  tags = merge(local.tag_name, tomap({ "Name" = "${local.tag_name.Project}-resource_parsing_lambda" }))

}

resource "null_resource" "delete_resource_list_zip_file" {
  triggers = {
    lambda_function_arn = aws_lambda_function.resource_list_function.arn
  }
  provisioner "local-exec" {
    command = "rm -r ${data.archive_file.resource_list_archive.output_path}"
  }
}

resource "null_resource" "delete_resource_parsing_zip_file" {
  triggers = {
    lambda_function_arn = aws_lambda_function.resource_parsing_function.arn
  }
  provisioner "local-exec" {
    command = "rm -r ${data.archive_file.resource_parsing_archive.output_path}"
  }
}

# Define the EventBridge rule
resource "aws_cloudwatch_event_rule" "resource_list" {
  name                = "${var.namespace}-xmop-resource-list-rule"
  description         = "Trigger the Lambda function every week on Monday"
  schedule_expression = "cron(0 0 * * ? 1)"
  tags                = merge(local.tag_name, tomap({ "Name" = "${local.tag_name.Project}-xmop-resource-list" }))
}


# Define the EventBridge target to invoke the Lambda function
resource "aws_cloudwatch_event_target" "resource_list" {
  rule = aws_cloudwatch_event_rule.resource_list.name
  arn  = aws_lambda_function.resource_list_function.arn
}
