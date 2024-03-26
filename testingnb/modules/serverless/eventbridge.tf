# Define the EventBridge rule for the cron job
resource "aws_cloudwatch_event_rule" "federated_cron_job" {
  name                = "federated-cron-job"
  description         = "Cron job to invoke lambda to get all the federated users and resources provisioned by them."
  schedule_expression = "cron(0 0 */14 * ? *)"  # Runs every 14 days

  # Runs every minute
  #schedule_expression = "cron(*/1 * * * ? *)"

  # Add tags for better organization and management
  tags = {
    Owner   = "x1"
    Creator = "x1"
    Project = "xc3"
  }
}

# Define the target to invoke the Lambda function
resource "aws_cloudwatch_event_target" "invoke_lambda" {
  rule      = aws_cloudwatch_event_rule.federated_cron_job.name
  target_id = "invoke-lambda-target"
  arn       = "arn:aws:lambda:ap-southeast-2:851725378731:function:sns_payload_lambda"  # Replace <REGION> and <ACCOUNT_ID> with your Lambda's region and account ID
}
