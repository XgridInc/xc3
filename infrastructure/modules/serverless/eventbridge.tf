# Define the EventBridge rule for the cron job
resource "aws_cloudwatch_event_rule" "federated_cron_job" {
  name                = "federated-cron-job"
  description         = "Cron job to invoke lambda to get all the federated users and resources provisioned by them."
  schedule_expression = "cron(0 0 */14 * ? *)"  # Runs every 14 days

  # Runs every minute
  # schedule_expression = "cron(*/1 * * * ? *)"

# Add tags for better organization and management
  tags = merge(local.tags, tomap({ "Name" = "${var.namespace}-federatedCron-job" }))
}




data "aws_caller_identity" "current" {}

# Define the target to invoke the Lambda function
resource "aws_cloudwatch_event_target" "invoke_lambda" {
  rule      = aws_cloudwatch_event_rule.federated_cron_job.name
  target_id = "invoke-lambda-target"
  arn       = "arn:aws:lambda:${var.region}:${data.aws_caller_identity.current.account_id}:function:${var.namespace}-list_fed_users"  
}
