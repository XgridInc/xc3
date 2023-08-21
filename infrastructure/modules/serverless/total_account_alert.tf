# Define the IAM role for the Lambda function
resource "aws_iam_role" "total_account_alert" {
  name = "${var.namespace}_total_account_alert"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = "sts:AssumeRole",
        Effect = "Allow",
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

# Creating Inline policy
resource "aws_iam_role_policy" "total_account_alert" {
  name = "${var.namespace}-total-account-alert-role-ce-policy"
  role = aws_iam_role.total_account_alert.id
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
          "ec2:DeleteNetworkInterface",
          "ses:SendEmail"
        ],
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

# Define the Lambda function code inline
data "archive_file" "total_account_alert" {
  type        = "zip"
  source_file = "../src/budget_details/total_account_alert.py"
  output_path = "${path.module}/total_account_alert.zip"
}

# AWS Lambda Function
resource "aws_lambda_function" "total_account_alert" {
  filename      = data.archive_file.total_account_alert.output_path
  function_name = "${var.namespace}-TotalAccountAlert"
  role          = aws_iam_role.total_account_alert.arn
  handler       = "total_account_alert.lambda_handler"
  runtime       = "python3.9"
  timeout       = 10

  environment {
    variables = {
      BUDGET_AMOUNT     = var.budget_amount
      SLACK_WEBHOOK_URL = var.slack_channel_url
      SES_EMAIL_ADDRESS = var.ses_email_address
      SNS_TOPIC_ARN     = var.sns_topic_arn2
    }
  }
  publish = true
}

resource "aws_iam_policy" "total_account_alert" {
  name = "${var.namespace}-total_account_alert_eventbridge_policy"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "lambda:InvokeFunction"
        ]
        Effect   = "Allow"
        Resource = aws_lambda_function.total_account_alert.arn
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "total_account_alert" {
  policy_arn = aws_iam_policy.total_account_alert.arn
  role       = aws_iam_role.total_account_alert.name
}

# Define the EventBridge rule
resource "aws_cloudwatch_event_rule" "total_account_alert" {
  name                = "${var.namespace}-total_account_alert-rule"
  description         = "Trigger the Lambda function at a specific interval"
  schedule_expression = var.total_account_cost_cronjob
  tags                = merge(local.tags, tomap({ "Name" = "${var.namespace}-total-account-alert-rule" }))
}

# Define the EventBridge target to invoke the Lambda function
resource "aws_cloudwatch_event_target" "total_account_alert" {
  rule = aws_cloudwatch_event_rule.total_account_alert.name
  arn  = aws_lambda_function.total_account_alert.arn
}

# Create a CloudWatch Alarm
resource "aws_cloudwatch_metric_alarm" "cloud_alarm" {
  alarm_name          = "${var.namespace}_CloudAlarm"
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = "1"
  metric_name         = "TotalCost"
  namespace           = "AccountCost"
  period              = "60"          # 1-minute period
  statistic           = "SampleCount" # Use SampleCount for custom metrics
  threshold           = "0.1"         # Your threshold value
  alarm_description   = "Alarm triggered when TotalCost exceeds 0"
  alarm_actions       = [var.sns_topic_arn2] # Use the existing SNS topic ARN
  # dimensions = {
  #   LambdaFunctionName = aws_lambda_function.total_account_alert.function_name
  # }
}

# IAM Policy: GetCostAndUsage Policy
resource "aws_iam_policy" "get_cost_and_usage" {
  name = "TotalAccountGetCostAndUsagePolicy"
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = [
          "ce:GetCostAndUsage",
          "s3:GetObject"
        ]
        Effect   = "Allow",
        Resource = "*"
      },
      {
        Sid    = "IAMListUsersPermissions"
        Effect = "Allow"
        Action = [
          "iam:ListUsers",
          "iam:GetUser" # Add the iam:GetUser permission here
        ]
        Resource = "*"
      }
    ]
  })
}

# IAM Policy: SES Full Access Policy
resource "aws_iam_policy" "ses_full_access_policy" {
  name = "${var.namespace}_SESFullAccessPolicy"
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action   = "ses:*",
        Effect   = "Allow",
        Resource = "*"
      }
    ]
  })
}


# IAM Policy: CloudWatch PutMetricData Policy
resource "aws_iam_policy" "totalaccount_put_metric_data_policy" {
  name = "${var.namespace}_TotalAccountPutMetricDataPolicy"
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action   = "cloudwatch:PutMetricData",
        Effect   = "Allow",
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_policy" "totalaccount_alarm_actions" {
  name = "TotalAccountAlarmActionsPolicy"
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action   = ["sns:Publish"],
        Effect   = "Allow",
        Resource = var.sns_topic_arn
      }
    ]
  })
}

# Attach the inline policies to the Lambda role
resource "aws_iam_policy_attachment" "total_account_lambda_inline_policy_attachments" {
  name       = "TotalAccountLambdaInlinePolicyAttachment"
  policy_arn = aws_iam_policy.get_cost_and_usage.arn
  roles      = [aws_iam_role.total_account_alert.name]
}

resource "aws_iam_policy_attachment" "total_account_ses_full_access_attachment" {
  name       = "TotalAccountSESFullAccessAttachment"
  policy_arn = aws_iam_policy.ses_full_access_policy.arn
  roles      = [aws_iam_role.total_account_alert.name]
}

resource "aws_iam_policy_attachment" "totalaccount_put_metric_data_attachment" {
  name       = "TotalAccountPutMetricDataAttachment"
  policy_arn = aws_iam_policy.totalaccount_put_metric_data_policy.arn
  roles      = [aws_iam_role.total_account_alert.name]
}

resource "aws_iam_policy_attachment" "totalaccount_alarm_actions_attachment" {
  name       = "TotalAccountAlarmActionsAttachment"
  policy_arn = aws_iam_policy.totalaccount_alarm_actions.arn
  roles      = [aws_iam_role.total_account_alert.name]
}


resource "aws_iam_role_policy_attachment" "total_account_lambda_policy_attachment" {
  policy_arn = aws_iam_policy.totalaccount_put_metric_data_policy.arn
  role       = aws_iam_role.total_account_alert.name
}

# tflint-ignore: terraform_required_providers
resource "aws_lambda_permission" "total_account_alert" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.total_account_alert.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.total_account_alert.arn
}
