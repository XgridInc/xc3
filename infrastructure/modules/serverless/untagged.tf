# IAM Role for untagged_resource Lambda Function
# -----------------------------------------
# This resource block defines an IAM role for the Lambda function named untagged_resource_lambda.

resource "aws_iam_role" "untagged_resource_lambda_role" {
  name = "${var.namespace}-untagged_resource_lambda_execution_role"  # Name of the IAM role
  
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
    "arn:aws:iam::aws:policy/AmazonEC2ReadOnlyAccess",
    "arn:aws:iam::aws:policy/AWSLambda_FullAccess",
    "arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess"
  ]
  tags = merge(local.tags, tomap({ "Name" = "${var.namespace}-untagged-resource-lambda-execution-role" }))
}


# Archive Lambda function code
# -----------------------------
# This data source archives the Lambda function code located in the "src" directory.

data "archive_file" "untagged_resource_lambda_zip" {
  type        = "zip"
  source_dir  = "../src/federated_user"
  output_path = "${path.module}/untagged_resource_lambda.zip"
}


# Lambda Function - untagged_resource
# ------------------------------
# This resource block defines the Lambda function named untagged_resource_lambda.

resource "aws_lambda_function" "untagged_resource_lambda" {
  filename      = data.archive_file.untagged_resource_lambda_zip.output_path  # Path to the Lambda function code zip archive
  function_name = "${var.namespace}-untagged_resource_lambda"  # Name of the Lambda function
  role          = aws_iam_role.untagged_resource_lambda_role.arn  # IAM role ARN attached to the Lambda function
  handler       = "untagged.lambda_handler"  # Entry point to the Lambda function
  runtime       = "python3.8"  # Runtime environment for the Lambda function
  timeout = 30


  # Environment variables passed to the Lambda function
  environment {
    variables = {
      RESOURCE_NOTIFICATION_LAMBDA_ARN = aws_lambda_function.resource_notification_lambda.arn
      ACC_NUM = data.aws_caller_identity.current.account_id
      NAME_SPACE = var.namespace
    }
  }

# Add tags for better organization and management
  tags = merge(local.tags, tomap({ "Name" = "${var.namespace}-untagged-resource-lambda" }))

}




# # Grant permission to EventBridge to invoke the Lambda function
# # -------------------------------------------------------------
# resource "aws_lambda_permission" "allow_eventbridge_invoke" {
#   statement_id  = "AllowExecutionFromEventBridge"
#   action        = "lambda:InvokeFunction"
#   function_name = aws_lambda_function.untagged_resource_lambda.function_name
#   principal     = "events.amazonaws.com"
#   source_arn    = aws_cloudwatch_event_rule.federated_cron_job.arn
# }

resource "aws_lambda_permission" "allow_list_fed_resource_lambda_invoke" {
  statement_id  = "AllowExecutionFromListFedResourceLambda"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.untagged_resource_lambda.arn
  principal     = "lambda.amazonaws.com"
}
