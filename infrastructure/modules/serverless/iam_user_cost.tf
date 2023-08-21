# Create an IAM role for the Lambda function
resource "aws_iam_role" "iam_user_cost" {
  name = "${var.namespace}_iam_user_cost" # Name of the IAM role

  # Assume role policy allows Lambda service to assume this role
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

# Define an IAM policy for Lambda function's S3 access
resource "aws_iam_policy" "iam_user_cost_policy" {
  name = "Lambda_IAM_User_Cost_Policy" # Name of the IAM policy

  # Policy document allowing S3:GetObject on specified bucket
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action   = ["s3:GetObject"],
        Effect   = "Allow",
        Resource = "arn:aws:s3:::${var.namespace}-metadata-storage/cost-metrics/*"
      }
    ]
  })
}

# Define an inline policy to allow SES full access
resource "aws_iam_role_policy" "iam_user_cost_ses_policy" {
  name = "Lambda_IAM_User_Cost_SES_Policy"
  role = aws_iam_role.iam_user_cost.id

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

# Define an inline policy to allow CloudWatch PutMetricData
resource "aws_iam_role_policy" "iam_user_cost_cw_policy" {
  name = "Lambda_IAM_User_Cost_CloudWatch_Policy"
  role = aws_iam_role.iam_user_cost.id

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

# IAM Role: EventBridge Scheduler Execution Role
resource "aws_iam_role" "iam_user_cost_eventb_scheduler_role" {
  name = "eventbridge-scheduler-execution-role-IAM"
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
resource "aws_iam_policy" "iam_user_cost_evb_scheduler_exec" {
  name        = "EventBridgeSchedulerExecutionPolicy"
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
          aws_lambda_function.iam_user_cost.arn,
          "${aws_lambda_function.iam_user_cost.arn}:*",
        ]
      }
    ]
  })
}

# IAM Policy Attachment: EventBridge Scheduler Execution Policy
resource "aws_iam_policy_attachment" "iam_user_cost_evb_scheduler_attachment" {
  name       = "EventBridgeSchedulerExecutionAttachment"
  policy_arn = aws_iam_policy.iam_user_cost_evb_scheduler_exec.arn
  roles      = [aws_iam_role.iam_user_cost_eventb_scheduler_role.name]
}

# Attach the IAM policy to the IAM role
resource "aws_iam_role_policy_attachment" "iam_user_cost_role_policy_attachment" {
  policy_arn = aws_iam_policy.iam_user_cost_policy.arn
  role       = aws_iam_role.iam_user_cost.name
}

# Create a ZIP file containing the Lambda function code
data "archive_file" "iam_user_cost" {
  type        = "zip"
  source_file = "../src/iam_users/iam_user_cost.py"
  output_path = "${path.module}/iam_user_cost.zip"
}

# Define the Lambda function resource
resource "aws_lambda_function" "iam_user_cost" {
  function_name = "${var.namespace}-iam_user_cost"            # Name of the Lambda function
  role          = aws_iam_role.iam_user_cost.arn              # IAM role ARN for the Lambda function
  handler       = "iam_user_cost.lambda_handler"              # Name of the Python function to execute
  runtime       = "python3.9"                                 # Python runtime version
  filename      = data.archive_file.iam_user_cost.output_path # Name of the ZIP file containing function code
  timeout       = 5                                           # Set the timeout to 5 seconds
  environment {
    variables = {
      IAM_BUDGET_AMOUNT = var.iam_budget_amount
      SLACK_WEBHOOK_URL = var.slack_channel_url
      SES_EMAIL_ADDRESS = var.ses_email_address
      BUCKET_NAME       = var.bucket_name
    }
  }
}

# Amazon EventBridge (CloudWatch Events) Rule for Cron Job
resource "aws_cloudwatch_event_rule" "iam_user_cost_lambda_cron_job" {
  name                = "${var.namespace}-iam_user_cost_LambdaCronJobRule"
  description         = "Event rule to trigger Lambda function at a specific interval"
  schedule_expression = var.cron_jobs_schedule.iam_user_cost_cronjob
}

# Amazon EventBridge (CloudWatch Events) Rule Target (Lambda Function)
resource "aws_cloudwatch_event_target" "iam_user_cost_lambda_target" {
  rule      = aws_cloudwatch_event_rule.iam_user_cost_lambda_cron_job.name
  arn       = aws_lambda_function.iam_user_cost.arn
  target_id = "TargetLambdaFunction"
}

# Amazon EventBridge (CloudWatch Events) Rule Permission
resource "aws_lambda_permission" "iam_user_cost_eventbridge_perm" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.iam_user_cost.arn
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.iam_user_cost_lambda_cron_job.arn
}

# Define local variables for outputs
# locals {
#   lambda_role_name = aws_iam_role.lambda_role.name
# }

# # Output the ARN of the created IAM role
# output "lambda_role_arn" {
#   value = aws_iam_role.lambda_role.arn
# }

# # Output the ARN of the created Lambda function
# output "lambda_function_arn" {
#   value = aws_lambda_function.IAM_User_Cost.arn
# }
