output "s3_xccc_bucket" {
  description = "x-ccc metadata storage bucket id"
  value       = aws_s3_bucket.this
}

output "s3_xccc_bucket_arn" {
  description = "x-ccc metadata storage bucket arn"
  value       = aws_s3_bucket.this.arn
}

output "sns_topic_arn" {
  description = "sns topic arn"
  value       = aws_sns_topic.this.arn
}

output "prometheus_layer_arn" {
  description = "Prometheus layer arn"
  value       = aws_lambda_layer_version.lambda_layer_prometheus.arn
}

output "mysql_layer_arn" {
  description = "Mysql layer arn"
  value       = aws_lambda_layer_version.lambda_layer_mysql.arn
}