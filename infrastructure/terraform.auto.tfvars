region                    = "eu-west-1"
vpc_cidr_block            = "10.0.0.0/24"
public_subnet_cidr_block  = "10.0.0.0/25"
private_subnet_cidr_block = "10.0.0.128/25"
ses_email_address         = "mfaheem@xgrid.co"
creator_email             = "saman.batool@xgrid.co"
ssh_key                   = "xccc-key"
instance_type             = "t2.micro"
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
