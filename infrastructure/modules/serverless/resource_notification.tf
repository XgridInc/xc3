# IAM Role for resource_notification Lambda Function
# -----------------------------------------
# This resource block defines an IAM role for the Lambda function named resource_notification_lambda.

resource "aws_iam_role" "resource_notification_lambda_role" {
  name = "${var.namespace}-resource_notification_lambda_execution_role"  # Name of the IAM role
  
  # Policy allowing Lambda service to assume the role
  assume_role_policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Effect" : "Allow",
        "Principal" : {
          "Service" : "lambda.amazonaws.com"
        },
        "Action" : "sts:AssumeRole"
      }
    ]
  })

  # Attach required managed policies to the role
  managed_policy_arns = [
    "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole",
    "arn:aws:iam::aws:policy/AmazonSNSFullAccess",
    "arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess"
  ]
  tags = merge(local.tags, tomap({ "Name" = "${var.namespace}-resource-notification-lambda-execution-role" }))
}


# Archive Lambda function code
# -----------------------------
# This data source archives the Lambda function code located in the "src/federated_user" directory.

data "archive_file" "resource_notification_lambda_zip" {
  type        = "zip"
  source_dir  = "../src/federated_user"
  output_path = "${path.module}/resource_notification_lambda.zip"
}


# Lambda Function - resource_notification
# ------------------------------
# This resource block defines the Lambda function named resource_notification_lambda.

resource "aws_lambda_function" "resource_notification_lambda" {
  filename      = data.archive_file.resource_notification_lambda_zip.output_path  # Path to the Lambda function code zip archive
  function_name = "${var.namespace}-resource_notification_lambda"  # Name of the Lambda function
  role          = aws_iam_role.resource_notification_lambda_role.arn  # IAM role ARN attached to the Lambda function
  handler       = "resource_notification.lambda_handler"  # Entry point to the Lambda function
  runtime       = "python3.8"  # Runtime environment for the Lambda function

  # Environment variables passed to the Lambda function
  environment {
    variables = {
      SNS_TOPIC_ARN = aws_sns_topic.resource_alert.arn  # Pass the ARN of the SNS topic as an environment variable
      SLACK_WEBHOOK_URL = var.slack_webhook_url
      NAME_SPACE = var.namespace
    }
  }

# Add tags for better organization and management
  tags = merge(local.tags, tomap({ "Name" = "${var.namespace}-resource-notification-lambda" }))

}


resource "aws_lambda_permission" "allow_list_fed_user_invoke" {
  statement_id  = "AllowExecutionFromListFedUserLambda"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.resource_notification_lambda.arn
  principal     = "lambda.amazonaws.com"
}
