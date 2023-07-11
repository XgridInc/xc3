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

locals {
  default_security_ingress = {
    "ssh" = {
      description              = "SSH"
      from_port                = 22
      to_port                  = 22
      protocol                 = "tcp"
      source_security_group_id = aws_security_group.public_sg.id
    }
    "lambda" = {
      description              = "All Traffic"
      from_port                = 0
      to_port                  = 65535
      protocol                 = "tcp"
      source_security_group_id = aws_security_group.serverless_sg.id
    }
    "mysql" = {
      description              = "MySQL Server"
      from_port                = 3306
      to_port                  = 3306
      protocol                 = "tcp"
      source_security_group_id = aws_security_group.serverless_sg.id
    }
    "grafana" = {
      description              = "Grafana Server"
      from_port                = 3000
      to_port                  = 3000
      protocol                 = "tcp"
      source_security_group_id = aws_security_group.lb_sg.id
    }
  }

  tags = {
    Owner   = var.owner_email
    Creator = var.creator_email
    Project = var.project
  }
}

resource "aws_security_group" "private_sg" {
  name        = "${var.namespace}_private_security_group"
  vpc_id      = aws_vpc.this.id
  description = "Security Group Rules"
  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = var.allow_traffic
  }
  dynamic "ingress" {
    for_each = var.env != "prod" ? [1] : [0]
    content {
      from_port   = 3000
      to_port     = 3000
      description = "Allow Grafana traffic to port 3000"
      protocol    = "TCP"
      cidr_blocks = var.allow_traffic
    }
  }

  ingress {
    description = "All Traffic"
    from_port   = 0
    to_port     = 65535
    protocol    = "tcp"
    cidr_blocks = [for subnet in aws_subnet.private_subnet : subnet.cidr_block]
  }
  egress {
    description = "Allow all egress traffic from the Load Balancer Security Group"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(local.tags, tomap({ "Name" = "${var.namespace}-Private-SG" }))

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
  description = "XC3 Bastion host access for updates"
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

  tags = merge(local.tags, tomap({ "Name" = "${var.namespace}-Public-SG" }))

}

# Creating a Security Group for lambda-ec2 accessibility
resource "aws_security_group" "serverless_sg" {
  description = "XC3 serverless module access for updates"
  name        = "${var.namespace}_serverless_security_group"
  vpc_id      = aws_vpc.this.id
  ingress {
    description = "All Traffic"
    from_port   = 0
    to_port     = 65535
    protocol    = "tcp"
    cidr_blocks = [for subnet in aws_subnet.private_subnet : subnet.cidr_block]

  }

  egress {
    description = "output from serverless sg"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(local.tags, tomap({ "Name" = "${var.namespace}-Serverless-SG" }))

}
# tflint-ignore: terraform_required_providers
resource "aws_security_group" "lb_sg" {
  #ts:skip=AC_AWS_0229 We are aware of the risk and choose to skip this rule
  name_prefix = "${var.namespace}-lb-security-group"
  vpc_id      = aws_vpc.this.id
  description = "XC3 Load Balancer Security Group"
  ingress {
    from_port   = var.domain_name != "" ? 443 : 80
    to_port     = var.domain_name != "" ? 443 : 80
    description = "Allow all ingress traffic to port 443"
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

  tags = merge(local.tags, tomap({ "Name" = "${var.namespace}-lb-sg" }))
}
