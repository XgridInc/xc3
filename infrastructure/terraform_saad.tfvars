namespace      = "saad"
region         = "eu-west-1"
vpc_cidr_block = "12.0.0.0/24"
account_id     = "201635854701"
domain_name    = "xccc.xgrid.co"
hosted_zone_id = "Z053166920YP1STI0EK5X"
public_subnet_cidr_block = {
  "eu-west-1a" = "12.0.0.0/26"
  "eu-west-1c" = "12.0.0.128/26"
}

lambda_names = {
  "iam_roles_all"          = "../lambda_functions/iam_roles/iam_roles_all.py"
  "iamrolesservice"        = "../lambda_functions/iam_roles/iamrolesservice.py"
  "iamrolesservicemapping" = "../lambda_functions/iam_roles/iamrolesservicemapping.py"
  "instancestatechange"    = "../lambda_functions/iam_roles/instancestatechange.py"
}
private_subnet_cidr_block  = "12.0.0.64/26"
allow_traffic              = ["39.46.255.84/32"]
ses_email_address          = "muhammad.saad@xgrid.co"
sns_topic_name             = "saad-notification-topic"
s3_xccc_bucket             = "saad-metadata-storage"
sqs_queue_name             = "saad-notification-queue"
creator_email              = "muhammad.saad@xgrid.co"
ssh_key                    = "xccc-key"
instance_type              = "t2.micro"
total_account_cost_lambda  = "total_account_cost"
total_account_cost_cronjob = "cron(0 0 14 * ? *)"
prometheus_layer           = "lambda_layers/python.zip"
security_group_ingress = {
  "pushgateway" = {
    description = "PushGateway"
    from_port   = 9091
    to_port     = 9091
    protocol    = "tcp"
    cidr_blocks = ["12.0.0.128/25"]
  },
  "prometheus" = {
    description = "Prometheus"
    from_port   = 9000
    to_port     = 9000
    protocol    = "tcp"
    cidr_blocks = ["12.0.0.128/25"]
  },
  "http" = {
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["12.0.0.128/25"]
  },
  "https" = {
    description = "HTTPS"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["12.0.0.128/25"]
  },
  "grafana" = {
    description = "Grafana"
    from_port   = 3000
    to_port     = 3000
    protocol    = "tcp"
    cidr_blocks = ["12.0.0.128/25"]
  },
  "mysql" = {
    description = "MySQL Server"
    from_port   = 3036
    to_port     = 3036
    protocol    = "tcp"
    cidr_blocks = ["12.0.0.128/25"]
  }
}

memory_size    = 128
timeout        = 300
