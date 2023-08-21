# Define the Lambda function code inline
data "archive_file" "total_cost_by_service" {
  type        = "zip"
  source_file = "../src/budget_details/total_cost_by_service.py"
  output_path = "${path.module}/total_cost_by_service.zip"
}

resource "aws_sns_topic" "my_sns_topic2" {
  name = "TotalCostSNSTopic"
}

resource "aws_lambda_function" "total_cost_by_service" {
  function_name = "${var.namespace}-TotalCostByService"
  role          = aws_iam_role.total_cost_by_service.arn
  handler       = "total_cost_by_service.lambda_handler" # Updated Lambda function filename and handler
  runtime       = "python3.9"
  filename      = data.archive_file.total_cost_by_service.output_path
  timeout       = 10

  environment {
    variables = {
      SERVICES_BUDGET_AMOUNT = var.services_budget_amount
      SLACK_WEBHOOK_URL      = var.slack_channel_url
      SES_EMAIL_ADDRESS      = var.ses_email_address
      SNS_TOPIC_ARN          = var.sns_topic_arn2
      BUCKET_NAME            = var.bucket_name
    }
  }
  publish = true
}

resource "aws_iam_role" "total_cost_by_service" {
  name = "${var.namespace}_LambdaCostbyServicesRole"

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

resource "aws_iam_policy" "lambda_total_cost_by_service_policy" {
  name        = "${var.namespace}_LambdaTotalCostByServicePolicy"
  description = "Policies for Lambda function to get Cost by Service"
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action   = ["logs:CreateLogGroup", "logs:CreateLogStream", "logs:PutLogEvents"],
        Effect   = "Allow",
        Resource = "*"
      },
      {
        Action   = ["s3:GetObject"],
        Effect   = "Allow",
        Resource = "arn:aws:s3:::${var.bucket_name}/*"
      },
      {
        Action   = ["cloudwatch:PutMetricData"],
        Effect   = "Allow",
        Resource = "*"
      },
      {
        Action   = ["ses:SendEmail"],
        Effect   = "Allow",
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_total_cost_by_service_policy_attachment" {
  policy_arn = aws_iam_policy.lambda_total_cost_by_service_policy.arn
  role       = aws_iam_role.total_cost_by_service.name
}

resource "aws_lambda_permission" "allow_cloudwatch" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.total_cost_by_service.function_name
  principal     = "events.amazonaws.com"
}

resource "aws_ses_email_identity" "from_email" {
  email = var.ses_email_address # Update with your desired sender email address
}

resource "aws_ses_template" "notification_template" {
  name = "NotificationTemplate" # Added missing "name" attribute

  html    = "The cost of your AWS account has exceeded the budget. Please review the details below:<br><br>{{details}}"
  subject = "High AWS Cost Alert"
  text    = "The cost of your AWS account has exceeded the budget. Please review the details below:\n\n{{details}}"
}

resource "aws_lambda_permission" "allow_ses" {
  statement_id  = "AllowExecutionFromSES"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.total_cost_by_service.function_name
  principal     = "ses.amazonaws.com"
}

# -------------------------------------For cronjob------------------------------------------------------
# IAM Role: EventBridge Scheduler Execution Role
resource "aws_iam_role" "total_cost_by_service_iam" {
  name = "${var.namespace}-ServiceCostEventBridgeRole"
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = "sts:AssumeRole",
        Effect = "Allow",
        Principal = {
          Service = "events.amazonaws.com"
        }
      }
    ]
  })
}

# IAM Policy: Amazon EventBridge Scheduler Execution Policy
resource "aws_iam_policy" "eventbridge_scheduler_execution" {
  name        = "${var.namespace}-EventBridgeSchedulerExecutionPolicy"
  path        = "/"
  description = "Policy for Amazon EventBridge Scheduler execution"

  # JSON-encoded policy document for EventBridge Scheduler execution permissions.
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = "lambda:InvokeFunction",
        Effect = "Allow",
        Resource = [
          aws_lambda_function.total_cost_by_service.arn,
          "${aws_lambda_function.total_cost_by_service.arn}:*",
        ]
      }
    ]
  })
}

# IAM Policy Attachment: EventBridge Scheduler Execution Policy
resource "aws_iam_policy_attachment" "total_cost_by_service" {
  name       = "${var.namespace}-EventbridgeScheduler}"
  policy_arn = aws_iam_policy.eventbridge_scheduler_execution.arn
  roles      = [aws_iam_role.total_cost_by_service_iam.name]
}

# Attach the IAM policy to the IAM role
# resource "aws_iam_role_policy_attachment" "lambda_policy_attachment" {
#   policy_arn = aws_iam_policy.lambda_policy.arn
#   role       = aws_iam_role.total_cost_by_service.name
# }

# Amazon EventBridge (CloudWatch Events) Rule for Cron Job
resource "aws_cloudwatch_event_rule" "total_cost_by_service" {
  name                = "${var.namespace}-LambdaCronJobRule"
  description         = "Event rule to trigger Lambda function"
  schedule_expression = var.cron_jobs_schedule.total_cost_by_service_cronjob
}

# Amazon EventBridge (CloudWatch Events) Rule Target (Lambda Function)
resource "aws_cloudwatch_event_target" "total_cost_by_service_target" {
  rule      = aws_cloudwatch_event_rule.total_cost_by_service.name
  arn       = aws_lambda_function.total_cost_by_service.arn
  target_id = "${var.namespace}-LambdaFunction"
}

# Amazon EventBridge (CloudWatch Events) Rule Permission
resource "aws_lambda_permission" "total_cost_by_service" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.total_cost_by_service.arn
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.total_cost_by_service.arn
}

# Define local variables for outputs
# locals {
#   lambda_role_name = aws_iam_role.total_cost_by_service.name
# }
