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
  services_resources_lambda_archive = {
    services_cost = {
      source_file = "../src/expensive_services_detail/top_5_expensive_services.py"
      output_path = "${path.module}/top_5_expensive_services.zip"
    }
    resources_cost = {
      source_file = "../src/expensive_services_detail/resources_breakdown.py"
      output_path = "${path.module}/resources_breakdown.zip"
    }
  }
}

data "archive_file" "services_resources_cost_lambda_src" {
  for_each    = local.services_resources_lambda_archive
  type        = "zip"
  source_file = each.value.source_file
  output_path = each.value.output_path
}




# Creating Inline policy
resource "aws_iam_role_policy" "ServicesResourcesCost" {
  name = "${var.namespace}-lambda-inline-policy"
  role = aws_iam_role.ServicesResourcesCost.id
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
          "ec2:AttachNetworkInterface",
          "ec2:DetachNetworkInterface",
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
          "s3:GetBucketAcl",
          "s3:PutObject",
          "s3:GetObject",
          "s3:ListBucket"
        ],
        "Resource" : [
          "arn:aws:s3:::${var.s3_xc3_bucket.id}",
          "arn:aws:s3:::${var.s3_xc3_bucket.id}/*"
        ]
      }
    ]
  })
}

# Creating IAM Role for Lambda functions
resource "aws_iam_role" "ServicesResourcesCost" {
  name = "${var.namespace}-services-resources-cost-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Sid    = "servicesresourcesrole"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
  managed_policy_arns = ["arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"]
  tags                = merge(local.tags, tomap({ "Name" = "${var.namespace}-Services-Resources-Cost-Role" }))
}

resource "aws_lambda_function" "ResourcesCost" {
  #ts:skip=AWS.LambdaFunction.LM.MEIDUM.0063 We are aware of the risk and choose to skip this rule
  #ts:skip=AWS.LambdaFunction.Logging.0470 We are aware of the risk and choose to skip this rule
  #ts:skip=AWS.LambdaFunction.EncryptionandKeyManagement.0471 We are aware of the risk and choose to skip this rule
  function_name = "${var.namespace}-resources-cost-breakdown"
  role          = aws_iam_role.ServicesResourcesCost.arn
  runtime       = "python3.9"
  handler       = "resources_breakdown.lambda_handler"
  filename      = values(data.archive_file.services_resources_cost_lambda_src)[0].output_path
  environment {
    variables = {
      prometheus_ip                 = "${var.prometheus_ip}:9091"
      bucket_name                   = var.s3_xc3_bucket.bucket
      bucket_name_get_report        = var.s3_xc3_bucket.bucket
      report_prefix                 = var.s3_prefixes.report
      top5_expensive_service_prefix = var.s3_prefixes.top5_expensive_service_prefix
    }
  }
  layers      = [var.prometheus_layer]
  memory_size = var.memory_size
  timeout     = var.timeout
  vpc_config {
    subnet_ids         = [var.subnet_id[0]]
    security_group_ids = [var.security_group_id]
  }
  tags = merge(local.tags, tomap({ "Name" = "${var.namespace}-resources_cost_breakdown" }))

}

resource "aws_lambda_function" "ServicesCost" {
  #ts:skip=AWS.LambdaFunction.LM.MEIDUM.0063 We are aware of the risk and choose to skip this rule
  #ts:skip=AWS.LambdaFunction.Logging.0470 We are aware of the risk and choose to skip this rule
  #ts:skip=AWS.LambdaFunction.EncryptionandKeyManagement.0471 We are aware of the risk and choose to skip this rule
  function_name = "${var.namespace}-expensive-services-cost"
  role          = aws_iam_role.ServicesResourcesCost.arn
  runtime       = "python3.9"
  handler       = "top_5_expensive_services.lambda_handler"
  filename      = values(data.archive_file.services_resources_cost_lambda_src)[1].output_path
  environment {
    variables = {
      prometheus_ip                 = "${var.prometheus_ip}:9091"
      bucket_name                   = var.s3_xc3_bucket.bucket
      bucket_name_get_report        = var.s3_xc3_bucket.bucket
      report_prefix                 = var.s3_prefixes.report
      top5_expensive_service_prefix = var.s3_prefixes.top5_expensive_service_prefix
      lambda_function_name          = aws_lambda_function.ResourcesCost.arn

    }
  }
  memory_size = var.memory_size
  timeout     = var.timeout
  layers      = [var.prometheus_layer]

  vpc_config {
    subnet_ids         = [var.subnet_id[0]]
    security_group_ids = [var.security_group_id]
  }

  tags = merge(local.tags, tomap({ "Name" = "${var.namespace}-services_cost_function" }))

}


resource "terraform_data" "delete_services_resources_lambda_zip_files" {
  for_each         = local.services_resources_lambda_archive
  triggers_replace = ["arn:aws:lambda:${var.region}:${var.account_id}:function:${each.key}"]
  depends_on       = [aws_lambda_function.ResourcesCost, aws_lambda_function.ServicesCost]

  provisioner "local-exec" {
    command = "rm -rf ${each.value.output_path}"
  }
}

resource "aws_s3_bucket_notification" "bucket_notification" {
  bucket      = var.s3_xc3_bucket.id
  eventbridge = true
}

# EventBridge Rule
resource "aws_cloudwatch_event_rule" "s3_event_rule" {
  name        = "s3_event_rule"
  description = "Rule to trigger Lambda functions on S3 events"

  event_pattern = <<EOF
{
  "source": [
    "aws.s3"
  ],
  "detail-type": [
    "Object Created"
  ],
  "detail": {
    "bucket": {
      "name": ["${var.s3_xc3_bucket.bucket}"]
    },
    "object": {
      "key": [{
        "prefix": "report/"
      }]
    }
  }
}
EOF
}

# Define the EventBridge target to invoke the Lambda function
resource "aws_cloudwatch_event_target" "services_cost" {
  rule = aws_cloudwatch_event_rule.s3_event_rule.name
  arn  = aws_lambda_function.ServicesCost.arn
}

# resource "aws_cloudwatch_event_target" "resources_cost" {
#   rule = aws_cloudwatch_event_rule.s3_event_rule.name
#   arn  = aws_lambda_function.ResourcesCost.arn
# }

resource "aws_iam_policy" "service_resources_event_policy" {
  name = "${var.namespace}-serviceresourceseventpolicy"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "lambda:InvokeFunction"
        ]
        Effect   = "Allow"
        Resource = [aws_lambda_function.ServicesCost.arn]
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "services_resources_policy_attachment" {
  policy_arn = aws_iam_policy.service_resources_event_policy.arn
  role       = aws_iam_role.ServicesResourcesCost.name
}


resource "aws_lambda_permission" "services_cost_breakdown" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.ServicesCost.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.s3_event_rule.arn
}

# resource "aws_lambda_permission" "resources_cost_breakdown" {
#   statement_id  = "AllowExecutionFromEventBridge"
#   action        = "lambda:InvokeFunction"
#   function_name = aws_lambda_function.ResourcesCost.function_name
#   principal     = "events.amazonaws.com"
#   source_arn    = aws_cloudwatch_event_rule.s3_event_rule.arn
# }
