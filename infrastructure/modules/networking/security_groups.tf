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
    "mysql" = {
      description              = "MySQL Server"
      from_port                = 3306
      to_port                  = 3306
      protocol                 = "tcp"
      source_security_group_id = "${aws_security_group.serverless_sg.id}"
    }
    "grafana" = {
      description              = "Grafana Server"
      from_port                = 3000
      to_port                  = 3000
      protocol                 = "tcp"
      source_security_group_id = "${aws_security_group.lb_sg.id}"
    }
  }

  tags = {
    Owner   = var.owner_email
    Creator = var.creator_email
    Project = var.namespace
  }
}

resource "aws_security_group" "private_sg" {
  name        = "${var.namespace}_private_security_group"
  vpc_id      = aws_vpc.this.id
  description = "Security Group Rules"
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(local.tags, tomap({ "Name" = "${local.tags.Project}-Private-SG" }))

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
  name        = "${var.namespace}_public_security_group"
  vpc_id      = aws_vpc.this.id
  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = var.allow_traffic
  }
  egress {
    description = "output from bastion host"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(local.tags, tomap({ "Name" = "${local.tags.Project}-Public-SG" }))

}

# Creating a Security Group for lambda-ec2 accessibility
resource "aws_security_group" "serverless_sg" {
  description = "X-CCC serverless module access for updates"
  name        = "${var.namespace}_serverless_security_group"
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

  tags = merge(local.tags, tomap({ "Name" = "${local.tags.Project}-Serverless-SG" }))

}

resource "aws_security_group" "lb_sg" {
  name_prefix = "${var.namespace}-lb-security-group"
  vpc_id      = aws_vpc.this.id
  description = "X-CCC Load Balancer Security Group"
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "TCP"
    cidr_blocks = ["0.0.0.0/0"]
  }
  egress {
    description = "Egress SG Rule"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(local.tags, tomap({ "Name" = "${local.tags.Project}-lb-sg" }))
}
