profile            = "faheem" // aws profile
region             = "eu-west-1"
vpc_cidr_block     = "10.0.0.0/24"
subnet1_cidr_block = "10.0.0.0/25"
ses_email_address  = "mfaheem@xgrid.co"
ssh_key            = "xccc-key"
instance_type      = "t2.micro"
allow_traffic      = "125.209.64.242/24"
security_group_ingress = {
  "pushgateway" = {
    description = "PushGateway"
    from_port   = 9091
    to_port     = 9091
    protocol    = "tcp"
    cidr_blocks = ["125.209.64.242/24"]
  },
  "http" = {
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["125.209.64.242/24"]
  },
  "ssh" = {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["125.209.64.242/24"]
  },
  "grafana" = {
    description = "Grafana"
    from_port   = 3000
    to_port     = 3000
    protocol    = "tcp"
    cidr_blocks = ["125.209.64.242/24"]
  },
  "mysql" = {
    description = "MySQL Server"
    from_port   = 3036
    to_port     = 3036
    protocol    = "tcp"
    cidr_blocks = ["125.209.64.242/24"]
  }
}
