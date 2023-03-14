output "s3_xccc_bucket" {
  description = "x-ccc metadata storage bucket"
  value       = aws_s3_bucket.this
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

output "private_ip" {
  description = "Private IP address of ec2 instance to push prometheus metrics"
  value       = aws_instance.this.private_ip
}
