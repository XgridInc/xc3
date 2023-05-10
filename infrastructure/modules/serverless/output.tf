output "grafana_api_gateway" {
  value = aws_api_gateway_rest_api.apiLambda.id
}
