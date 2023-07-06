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

data "archive_file" "cost_report_notifier" {
  count       = var.slack_channel_url != "" ? 1 : 0
  type        = "zip"
  source_file = "../src/notifier/cost_report_notifier.py"
  output_path = "${path.module}/cost_report_notifier.zip"
}

# Creating Inline policy for Cost Report Notifier to have the access of S3 Bucket and EC2 Interfaces
resource "aws_iam_role_policy" "cost_report_notifier" {
  count = var.slack_channel_url != "" ? 1 : 0
  name  = "${var.namespace}-cost-report-notifier"
  role  = aws_iam_role.cost_report_notifier[0].id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid = "S3Access"
        "Effect" : "Allow",
        "Action" : [
          "s3:GetObject",
          "s3:ListBucket"
        ],
        "Resource" : [
          "arn:aws:s3:::${var.s3_xc3_bucket.id}/*",
          "arn:aws:s3:::${var.s3_xc3_bucket.id}"
        ]
      },
      {
        "Sid" : "EC2Access",
        "Effect" : "Allow",
        "Action" : [
          "ec2:CreateNetworkInterface",
          "ec2:DescribeNetworkInterfaces",
          "ec2:DetachNetworkInterface",
          "ec2:AttachNetworkInterface",
          "ec2:DeleteNetworkInterface"
        ]
        "Resource" : "*"
      },
    ]
  })
}

# Creating IAM Role for Cost Report Notifier that will be assumed by lambda function
resource "aws_iam_role" "cost_report_notifier" {
  count = var.slack_channel_url != "" ? 1 : 0
  name  = "${var.namespace}-cost-report-notifier"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Sid    = "CRIrole"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
  managed_policy_arns = []
  tags                = merge(local.tags, tomap({ "Name" = "${var.namespace}-cost-report-notifier" }))
}

resource "aws_lambda_function" "cost_report_notifier" {
  count = var.slack_channel_url != "" ? 1 : 0
  #ts:skip=AWS.LambdaFunction.LM.MEIDUM.0063 We are aware of the risk and choose to skip this rule
  #ts:skip=AWS.LambdaFunction.Logging.0470 We are aware of the risk and choose to skip this rule
  #ts:skip=AWS.LambdaFunction.EncryptionandKeyManagement.0471 We are aware of the risk and choose to skip this rule
  function_name = "${var.namespace}-cost-report-notifier"
  role          = aws_iam_role.cost_report_notifier[0].arn
  runtime       = "python3.9"
  handler       = "cost_report_notifier.lambda_handler"
  filename      = data.archive_file.cost_report_notifier[0].output_path
  environment {
    variables = {
      prometheus_ip            = "${var.prometheus_ip}:9091"
      bucket_name              = var.s3_xc3_bucket.bucket
      project_spend_prefix     = var.s3_prefixes.project_spend_prefix
      slack_channel_url        = var.slack_channel_url
      monthly_cost_prefix      = var.s3_prefixes.monthly_cost_prefix
      expensive_service_prefix = var.s3_prefixes.expensive_service_prefix

    }
  }
  memory_size = var.memory_size
  timeout     = var.timeout
  layers      = [aws_lambda_layer_version.apprise_layer[0].arn]

  vpc_config {
    subnet_ids         = [var.subnet_id[0]]
    security_group_ids = [var.security_group_id]
  }

  tags = merge(local.tags, tomap({ "Name" = "${var.namespace}-cost-report-notifier" }))

}

resource "terraform_data" "delete_cost_report_notifier_zip_file" {
  count            = var.slack_channel_url != "" ? 1 : 0
  triggers_replace = [aws_lambda_function.cost_report_notifier[0].arn]
  provisioner "local-exec" {
    command = "rm -r ${data.archive_file.cost_report_notifier[0].output_path}"
  }
}

# Define the EventBridge rule
resource "aws_cloudwatch_event_rule" "cost_report_notifier" {
  count               = var.slack_channel_url != "" ? 1 : 0
  name                = "${var.namespace}-cost-report-notifier-rule"
  description         = "Trigger the Lambda function every two weeks"
  schedule_expression = var.cron_jobs_schedule.cost_report_notifier_cronjob
  tags                = merge(local.tags, tomap({ "Name" = "${var.namespace}-cost-report-notifier-rule" }))
}

# Define the EventBridge target to invoke the Lambda function
resource "aws_cloudwatch_event_target" "cost_report_notifier" {
  count = var.slack_channel_url != "" ? 1 : 0
  rule  = aws_cloudwatch_event_rule.cost_report_notifier[0].name
  arn   = aws_lambda_function.cost_report_notifier[0].arn
}

resource "aws_iam_policy" "cri_eventbridge_policy" {
  count = var.slack_channel_url != "" ? 1 : 0
  name  = "${var.namespace}-cri-eventbridge_policy"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "lambda:InvokeFunction"
        ]
        Effect   = "Allow"
        Resource = [aws_lambda_function.cost_report_notifier[0].arn]
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "cri_eventbridge_policy_attachment" {
  count      = var.slack_channel_url != "" ? 1 : 0
  policy_arn = aws_iam_policy.cri_eventbridge_policy[0].arn
  role       = aws_iam_role.cost_report_notifier[0].name
}

resource "aws_lambda_permission" "cost_report_notifier" {
  count         = var.slack_channel_url != "" ? 1 : 0
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.cost_report_notifier[0].function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.cost_report_notifier[0].arn
}

resource "aws_lambda_layer_version" "apprise_layer" {
  count      = var.slack_channel_url != "" ? 1 : 0
  s3_bucket  = var.s3_xc3_bucket.id
  s3_key     = "apprise/python.zip"
  layer_name = "${var.namespace}-apprise-layer"

  compatible_runtimes = ["python3.9"]
  depends_on = [
    terraform_data.upload_files_on_s3
  ]
}
