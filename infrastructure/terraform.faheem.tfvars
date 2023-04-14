namespace      = "faheem"
region         = "eu-west-1"
account_id     = "201635854701"
vpc_cidr_block = "15.0.0.0/24"
public_subnet_cidr_block = {
  "eu-west-1a" = "15.0.0.0/26"
  "eu-west-1c" = "15.0.0.128/26"
}
domain_name                = ""
hosted_zone_id             = "Z053166920YP1STI0EK5X"
private_subnet_cidr_block  = "15.0.0.64/26"
allow_traffic              = ["39.46.215.160/32", "202.69.61.0/24", "125.209.64.240/28"]
ses_email_address          = "xccc@xgrid.co"
creator_email              = "mfaheem@xgrid.co"
instance_type              = "t2.micro"
total_account_cost_lambda  = "total_account_cost"
total_account_cost_cronjob = "cron(0 0 14 * ? *)"
prometheus_layer           = "lambda_layers/python.zip"
memory_size                = 128
timeout                    = 300
security_group_ingress = {
  "pushgateway" = {
    description = "PushGateway"
    from_port   = 9091
    to_port     = 9091
    protocol    = "tcp"
    cidr_blocks = ["15.0.0.64/26"]
  },
  "prometheus" = {
    description = "Prometheus"
    from_port   = 9000
    to_port     = 9000
    protocol    = "tcp"
    cidr_blocks = ["15.0.0.64/26"]
  },
  "http" = {
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["15.0.0.64/26"]
  },
  "https" = {
    description = "HTTPS"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["15.0.0.64/26"]
  },
  "grafana" = {
    description = "Grafana"
    from_port   = 3000
    to_port     = 3000
    protocol    = "tcp"
    cidr_blocks = ["15.0.0.64/26"]
  }
}

