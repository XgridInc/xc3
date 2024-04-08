# IAM Role for sns_payload Lambda Function
# -----------------------------------------
# This resource block defines an IAM role for the Lambda function named sns_payload_lambda.

resource "aws_iam_role" "sns_payload_lambda_role" {
  name = "sns_payload_lambda_execution_role"  # Name of the IAM role
  
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
}


# Archive Lambda function code
# -----------------------------
# This data source archives the Lambda function code located in the "src/federated_user" directory.

data "archive_file" "sns_payload_lambda_zip" {
  type        = "zip"
  source_dir  = "src/federated_user"
  output_path = "${path.module}/sns_payload_lambda.zip"
}


# Lambda Function - sns_payload
# ------------------------------
# This resource block defines the Lambda function named sns_payload_lambda.

resource "aws_lambda_function" "sns_payload_lambda" {
  filename      = data.archive_file.sns_payload_lambda_zip.output_path  # Path to the Lambda function code zip archive
  function_name = "sns_payload_lambda"  # Name of the Lambda function
  role          = aws_iam_role.sns_payload_lambda_role.arn  # IAM role ARN attached to the Lambda function
  handler       = "sns_payload.lambda_handler"  # Entry point to the Lambda function
  runtime       = "python3.8"  # Runtime environment for the Lambda function

  # Environment variables passed to the Lambda function
  environment {
    variables = {
      SNS_TOPIC_ARN = aws_sns_topic.resource_alert.arn  # Pass the ARN of the SNS topic as an environment variable
    }
  }

# Add tags for better organization and management
  tags = {

    Owner   = var.Owner
    Creator = var.Creator
    Project = var.Project
  }

}

# Grant permission to EventBridge to invoke the Lambda function
# -------------------------------------------------------------
#resource "aws_lambda_permission" "allow_eventbridge_invoke" {
 # statement_id  = "AllowExecutionFromEventBridge"
 # action        = "lambda:InvokeFunction"
 # function_name = aws_lambda_function.sns_payload_lambda.function_name
 # principal     = "events.amazonaws.com"
 # source_arn    = aws_cloudwatch_event_rule.federated_cron_job.arn
#}

resource "aws_lambda_permission" "allow_untagged_resource_lambda_invoke" {
  statement_id  = "AllowExecutionFromUntaggedResourceLambda"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.sns_payload_lambda.arn
  principal     = "lambda.amazonaws.com"
}
