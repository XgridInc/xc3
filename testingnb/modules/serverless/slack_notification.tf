# IAM Role for Lambda Function
resource "aws_iam_role" "lambda_role" {
  name               = "lambda_basic_execution_role"  # Name of the IAM role
  assume_role_policy = jsonencode({  # Policy allowing Lambda service to assume the role
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

  managed_policy_arns = [  # Attach AWSLambdaBasicExecutionRole policy to the role
    "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole",
    "arn:aws:iam::aws:policy/AmazonSNSFullAccess"  # Amazon SNS Full Access policy
  ]
}

# Archive Lambda function code
data "archive_file" "lambda_function_zip" {
  type        = "zip"
  source_dir  = "src/federated_user"
  output_path = "${path.module}/lambda_function.zip"
}

# Lambda Function
resource "aws_lambda_function" "slack_notification_lambda" {
  filename      = data.archive_file.lambda_function_zip.output_path  # Path to the Lambda function code zip archive
  function_name = "slack_notification_lambda"  # Name of the Lambda function
  role          = aws_iam_role.lambda_role.arn  # IAM role ARN attached to the Lambda function
  handler       = "slack_notification.lambda_handler"  # Entry point to the Lambda function
  runtime       = "python3.8"  # Runtime environment for the Lambda function

  environment {
    variables = {
      SLACK_WEBHOOK_URL = var.slack_webhook_url
    }
  }

# Add tags for better organization and management
  tags = {

    Owner   = var.Owner
    Creator = var.Creator
    Project = var.Project
  }
}

# Permission for SNS Topic to invoke Lambda Function
resource "aws_lambda_permission" "sns_invoke_permission" {
  statement_id  = "AllowExecutionFromSNS"  # ID for the permission statement
  action        = "lambda:InvokeFunction"  # Action to be permitted
  function_name = aws_lambda_function.slack_notification_lambda.function_name  # Name of the Lambda function
  principal     = "sns.amazonaws.com"  # Service principal that invokes the Lambda function

  source_arn = aws_sns_topic.resource_alert.arn  # ARN of the SNS topic
}

