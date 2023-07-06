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
  lambda_archive = {
    most_expensive_service = {
      source_file = "../src/expensive_services_detail/most_expensive_service.py"
      output_path = "${path.module}/most_expensive_service.zip"
    }
    cost_metrics_of_expensive_services = {
      source_file = "../src/expensive_services_detail/cost_metrics_of_expensive_services.py"
      output_path = "${path.module}/cost_metrics_of_expensive_services.zip"
    }
  }
}

# tflint-ignore: terraform_required_providers
data "archive_file" "src" {
  for_each    = local.lambda_archive
  type        = "zip"
  source_file = each.value.source_file
  output_path = each.value.output_path
}

# Creating IAM Role for Lambda functions
resource "aws_iam_role" "most_expensive_service_role" {
  name = "${var.namespace}-most_expensive_service_role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Sid    = "ExpensiveServiceRole"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
  managed_policy_arns = ["arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"]
  tags                = merge(local.tags, tomap({ "Name" = "${var.namespace}-most_expensive_service_role" }))

}

# Creating Inline policy
resource "aws_iam_role_policy" "most_expensive_service_policy" {
  name = "${var.namespace}-most_expensive_service_policy"
  role = aws_iam_role.most_expensive_service_role.id
  policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Sid" : "ExpensiveServicePermission",
        "Effect" : "Allow",
        "Action" : [
          "ce:GetCostAndUsage",
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
        "Sid" : "SSMParameter",
        "Effect" : "Allow",
        "Action" : [
          "ssm:GetParameter"
        ],
        "Resource" : "arn:aws:ssm:*:*:parameter/*"
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

resource "aws_lambda_function" "most_expensive_service" {
  #ts:skip=AWS.LambdaFunction.LM.MEIDUM.0063 We are aware of the risk and choose to skip this rule
  #ts:skip=AWS.LambdaFunction.Logging.0470 We are aware of the risk and choose to skip this rule
  #ts:skip=AWS.LambdaFunction.EncryptionandKeyManagement.0471 We are aware of the risk and choose to skip this rule
  function_name = "${var.namespace}-most_expensive_service_lambda"
  role          = aws_iam_role.most_expensive_service_role.arn
  runtime       = "python3.9"
  handler       = "most_expensive_service.lambda_handler"
  filename      = values(data.archive_file.src)[1].output_path
  environment {
    variables = {
      account_detail       = var.namespace
      lambda_function_name = aws_lambda_function.cost_metrics_of_expensive_services.arn
    }
  }
  memory_size = var.memory_size
  timeout     = var.timeout
  vpc_config {
    subnet_ids         = [var.subnet_id[0]]
    security_group_ids = [var.security_group_id]
  }
  tags = merge(local.tags, tomap({ "Name" = "${var.namespace}-most_expensive_service" }))

}

resource "aws_lambda_function" "cost_metrics_of_expensive_services" {
  #ts:skip=AWS.LambdaFunction.LM.MEIDUM.0063 We are aware of the risk and choose to skip this rule
  #ts:skip=AWS.LambdaFunction.Logging.0470 We are aware of the risk and choose to skip this rule
  #ts:skip=AWS.LambdaFunction.EncryptionandKeyManagement.0471 We are aware of the risk and choose to skip this rule
  function_name = "${var.namespace}-cost_metrics_of_expensive_services"
  role          = aws_iam_role.most_expensive_service_role.arn
  runtime       = "python3.9"
  handler       = "cost_metrics_of_expensive_services.lambda_handler"
  filename      = values(data.archive_file.src)[0].output_path
  environment {
    variables = {
      prometheus_ip            = "${var.prometheus_ip}:9091"
      bucket_name              = var.s3_xc3_bucket.bucket
      expensive_service_prefix = var.s3_prefixes.expensive_service_prefix
    }
  }
  layers      = [var.prometheus_layer]
  memory_size = var.memory_size
  timeout     = var.timeout
  vpc_config {
    subnet_ids         = [var.subnet_id[0]]
    security_group_ids = [var.security_group_id]
  }
  tags = merge(local.tags, tomap({ "Name" = "${var.namespace}-cost_metrics_of_expensive_services" }))

}

resource "terraform_data" "delete_lambda_zip_files" {
  for_each         = local.lambda_archive
  triggers_replace = ["arn:aws:lambda:${var.region}:${var.account_id}:function:${each.key}"]
  depends_on       = [aws_lambda_function.cost_metrics_of_expensive_services, aws_lambda_function.most_expensive_service]

  provisioner "local-exec" {
    command = "rm -rf ${each.value.output_path}"
  }
}

resource "aws_iam_policy" "most_expensive_service" {
  name = "${var.namespace}-most_expensive_service_eventbridge_policy"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "lambda:InvokeFunction"
        ]
        Effect   = "Allow"
        Resource = aws_lambda_function.most_expensive_service.arn
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "most_expensive_service" {
  policy_arn = aws_iam_policy.most_expensive_service.arn
  role       = aws_iam_role.most_expensive_service_role.name
}

# Define the EventBridge rule
resource "aws_cloudwatch_event_rule" "most_expensive_service" {
  name                = "${var.namespace}-most_expensive_service-rule"
  description         = "Trigger the Lambda function every week on Monday"
  schedule_expression = var.cron_jobs_schedule["most_expensive_service_cron"]
  tags                = merge(local.tags, tomap({ "Name" = "${var.namespace}-most_expensive_service_rule" }))
}

# Define the EventBridge target to invoke the Lambda function
resource "aws_cloudwatch_event_target" "most_expensive_service" {
  rule = aws_cloudwatch_event_rule.most_expensive_service.name
  arn  = aws_lambda_function.most_expensive_service.arn
}

resource "aws_lambda_permission" "most_expensive_service" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.most_expensive_service.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.most_expensive_service.arn
}
