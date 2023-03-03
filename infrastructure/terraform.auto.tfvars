region                    = "eu-west-1"
vpc_cidr_block            = "10.0.0.0/24"
public_subnet_cidr_block  = "10.0.0.0/26"
private_subnet_cidr_block = "10.0.0.64/26"
allow_traffic             = "39.46.255.84/32"
ses_email_address         = "mfaheem@xgrid.co"
sns_topic_name            = "xccc-notification-topic"
s3_xccc_bucket            = "xccc-metadata-storage"
sqs_queue_name            = "xccc-notification-queue"
creator_email             = "saman.batool@xgrid.co"
ssh_key                   = "xccc-key"
instance_type             = "t2.micro"
prometheus_layer          = "lambda_layers/python.zip"
mysql_layer               = "lambda_layers/layer-mysql-prometheus.zip"
security_group_ingress = {
  "pushgateway" = {
    description = "PushGateway"
    from_port   = 9091
    to_port     = 9091
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.128/25"]
  },
  "prometheus" = {
    description = "Prometheus"
    from_port   = 9000
    to_port     = 9000
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.128/25"]
  },
  "http" = {
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.128/25"]
  },
  "https" = {
    description = "HTTPS"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.128/25"]
  },
  "grafana" = {
    description = "Grafana"
    from_port   = 3000
    to_port     = 3000
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.128/25"]
  },
  "mysql" = {
    description = "MySQL Server"
    from_port   = 3036
    to_port     = 3036
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.128/25"]
  }
}
