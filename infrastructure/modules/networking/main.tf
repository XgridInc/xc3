locals {
  default_security_ingress = {
    "ssh" = {
      description              = "SSH"
      from_port                = 22
      to_port                  = 22
      protocol                 = "tcp"
      source_security_group_id = "${aws_security_group.public_sg.id}"
    }
    "lambda" = {
      description              = "All Traffic"
      from_port                = 0
      to_port                  = 65535
      protocol                 = "tcp"
      source_security_group_id = "${aws_security_group.serverless_sg.id}"
    }
  }
}
resource "aws_vpc" "this" {
  cidr_block           = var.vpc_cidr_block
  enable_dns_hostnames = "true"

  tags = {
    Name    = "${var.namespace}-VPC"
    Project = "${var.namespace}"
    Owner   = "${var.owner_email}"
    Creator = "${var.creator_email}"
  }
}

resource "aws_subnet" "public_subnet" {
  vpc_id                  = aws_vpc.this.id
  cidr_block              = var.public_subnet_cidr_block
  map_public_ip_on_launch = true

  tags = {
    Name    = "${var.namespace}-Public-Subnet-1"
    Project = "${var.namespace}"
    Owner   = "${var.owner_email}"
    Creator = "${var.creator_email}"
  }
}

resource "aws_subnet" "private_subnet" {
  vpc_id                  = aws_vpc.this.id
  cidr_block              = var.private_subnet_cidr_block
  map_public_ip_on_launch = false

  tags = {
    Name    = "${var.namespace}-Private-Subnet-1"
    Project = var.namespace
    Owner   = var.owner_email
    Creator = var.creator_email
  }
}

resource "aws_security_group" "private_sg" {
  name        = "${var.key}_private_security_group"
  vpc_id      = aws_vpc.this.id
  description = "Security Group Rules"
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name    = "${var.namespace}-Private-SG"
    Project = var.namespace
    Owner   = var.owner_email
    Creator = var.creator_email
  }
}

resource "aws_security_group_rule" "private_sg_rule" {
  for_each = var.security_group_ingress

  type              = "ingress"
  security_group_id = aws_security_group.private_sg.id
  from_port         = each.value.from_port
  to_port           = each.value.to_port
  protocol          = each.value.protocol
  cidr_blocks       = each.value.cidr_blocks
  description       = each.value.description
}

resource "aws_security_group_rule" "private_default_sg_rule" {
  for_each = local.default_security_ingress

  type                     = "ingress"
  security_group_id        = aws_security_group.private_sg.id
  from_port                = each.value.from_port
  to_port                  = each.value.to_port
  protocol                 = each.value.protocol
  source_security_group_id = each.value.source_security_group_id
  description              = each.value.description
}

# Creating a Security Group for bastion host
resource "aws_security_group" "public_sg" {
  description = "X-CCC Bastion host access for updates"
  name        = "${var.key}_public_security_group"
  vpc_id      = aws_vpc.this.id
  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  egress {
    description = "output from bastion host"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  tags = {
    Name    = "${var.namespace}-Public-SG"
    Project = var.namespace
    Owner   = var.owner_email
    Creator = var.creator_email
  }
}

# Creating a Security Group for lambda-ec2 accessibility
resource "aws_security_group" "serverless_sg" {
  description = "X-CCC serverless module access for updates"
  name        = "${var.key}_serverless_security_group"
  vpc_id      = aws_vpc.this.id
  ingress {
    description = "All Traffic"
    from_port   = 0
    to_port     = 65535
    protocol    = "tcp"
    cidr_blocks = [aws_subnet.private_subnet.cidr_block]
  }

  egress {
    description = "output from serverless sg"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  tags = {
    Name    = "${var.namespace}-Serverless-SG"
    Project = var.namespace
    Owner   = var.owner_email
    Creator = var.creator_email
  }
}

# Creating Internet Gateway to make subnet public

resource "aws_internet_gateway" "this" {
  vpc_id = aws_vpc.this.id

  tags = {
    Name    = "${var.namespace}-Internet-Gateway"
    Project = var.namespace
    Owner   = var.owner_email
    Creator = var.creator_email
  }
}

# Creating Custom Route Table for Public Subnet

resource "aws_route_table" "this" {
  vpc_id = aws_vpc.this.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.this.id
  }

  tags = {
    Name    = "${var.namespace}-Public-Route-Table"
    Project = var.namespace
    Owner   = var.owner_email
    Creator = var.creator_email
  }
}

resource "aws_route_table_association" "this" {
  subnet_id      = aws_subnet.public_subnet.id
  route_table_id = aws_route_table.this.id
}

# Creating an Elastic IP for the NAT Gateway!
resource "aws_eip" "this" {
  vpc = true
  tags = {
    Name    = "${var.namespace}-eip"
    Project = var.namespace
    Owner   = var.owner_email
    Creator = var.creator_email
  }
}

# Creating a NAT Gateway!
resource "aws_nat_gateway" "this" {
  # Allocating the Elastic IP to the NAT Gateway!
  allocation_id = aws_eip.this.id

  # Associating it in the Public Subnet!
  subnet_id = aws_subnet.public_subnet.id
  tags = {
    Name    = "${var.namespace}-Nat-Gateway"
    Project = var.namespace
    Owner   = var.owner_email
    Creator = var.creator_email
  }
}

# Creating a Route Table for the Nat Gateway!
resource "aws_route_table" "private_rt" {
  vpc_id = aws_vpc.this.id

  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.this.id
  }

  tags = {
    Name    = "${var.namespace}-Private-Route-Table"
    Project = var.namespace
    Owner   = var.owner_email
    Creator = var.creator_email
  }

}

# Creating an Route Table Association of the NAT Gateway route table with the Private Subnet!
resource "aws_route_table_association" "private_rt_association" {
  subnet_id      = aws_subnet.private_subnet.id
  route_table_id = aws_route_table.private_rt.id
}
