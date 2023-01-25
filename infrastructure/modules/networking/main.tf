resource "aws_vpc" "this" {
  cidr_block           = var.vpc_cidr_block
  enable_dns_hostnames = "true"

  tags = {
    Name = "${var.namespace}-VPC"
  }
}

resource "aws_subnet" "this" {
  vpc_id     = aws_vpc.this.id
  cidr_block = var.subnet1_cidr_block

  tags = {
    Name = "${var.namespace}-Subnet-1"
  }
}

resource "aws_security_group" "this" {
  name        = "${var.key}-security_group"
  vpc_id      = aws_vpc.this.id
  description = "Security Group Rules"

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = [var.allow_traffic]
  }

  tags = {
    Name = "${var.namespace}-SG"
  }
}

resource "aws_security_group_rule" "this" {
  for_each = var.security_group_ingress

  type              = "ingress"
  security_group_id = aws_security_group.this.id
  from_port         = each.value.from_port
  to_port           = each.value.to_port
  protocol          = each.value.protocol
  cidr_blocks       = each.value.cidr_blocks
  description       = each.value.description
}

# Creating Internet Gateway to make subnet public

resource "aws_internet_gateway" "this" {
  vpc_id = aws_vpc.this.id

  tags = {
    Name = "${var.namespace}-Internet-Gateway"
  }
}

# Creating Custom Route Table for Public Subnet 

resource "aws_route_table" "this" {
  vpc_id = aws_vpc.this.id

  route {
    cidr_block = var.allow_traffic
    gateway_id = aws_internet_gateway.this.id
  }

  tags = {
    Name = "${var.namespace}-Public-Route-Table"
  }
}

resource "aws_route_table_association" "this" {
  subnet_id      = aws_subnet.this.id
  route_table_id = aws_route_table.this.id
}
