# Copyright (c) 2023, Xgrid Inc, https://xgrid.co

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#        http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

output "s3_xc3_bucket" {
  description = "xc3 metadata storage bucket"
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

output "private_ip" {
  description = "Private IP address of ec2 instance to push prometheus metrics"
  value       = aws_instance.this.private_ip
}

output "xc3_url" {
  description = "DNS of the XC3 Dashboard"
  value       = var.env != "prod" ? aws_instance.this.public_ip : var.domain_name != "" ? var.domain_name : aws_lb.this[0].dns_name
}
