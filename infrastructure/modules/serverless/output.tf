output "grafana_api_gateway" {
  value = aws_api_gateway_rest_api.apiLambda.id
}

# Output: EventBridge Rule ARN
# output "eventbridge_rule_arn" {
#   value = aws_cloudwatch_event_rule.total_acc_cost_cron_job.arn
# }

# Output: Lambda Function ARN
# output "lambda_function_arn" {
#   value = aws_lambda_function.notification_new.arn
# }

# Output: Lambda Function ARN
output "total_account_alert_arn" {
  value = aws_lambda_function.total_account_alert.arn
}

output "sns_topic_arn2" {
  value = aws_sns_topic.my_sns_topic2.arn
}

# Output the ARN of the created IAM role
output "lambda_role_arn" {
  value = aws_iam_role.total_cost_by_service.arn
}

# Output the ARN of the created Lambda function
output "lambda_function_arn" {
  value = aws_lambda_function.total_cost_by_service.arn
}
