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

resource "aws_vpc" "this" {
  #ts:skip=AWS.VPC.Logging.Medium.0470 We are aware of the risk and choose to skip this rule
  cidr_block           = var.vpc_cidr_block
  enable_dns_hostnames = "true"

  tags = merge(local.tags, tomap({ "Name" = "${var.namespace}-VPC" }))
}

resource "aws_subnet" "public_subnet" {
  for_each = var.public_subnet_cidr_block

  vpc_id                  = aws_vpc.this.id
  map_public_ip_on_launch = false
  cidr_block              = each.value
  availability_zone       = each.key
  tags                    = merge(local.tags, tomap({ "Name" = "${var.namespace}-Public-Subnet-${each.key}" }))

}

resource "aws_subnet" "private_subnet" {
  for_each = var.private_subnet_cidr_block

  vpc_id                  = aws_vpc.this.id
  cidr_block              = each.value
  availability_zone       = each.key
  map_public_ip_on_launch = false

  tags = merge(local.tags, tomap({ "Name" = "${var.namespace}-Private-Subnet-${each.key}" }))

}

# Creating Internet Gateway to make subnet public

resource "aws_internet_gateway" "this" {
  vpc_id = aws_vpc.this.id

  tags = merge(local.tags, tomap({ "Name" = "${var.namespace}-Internet-Gateway" }))

}

# Creating Custom Route Table for Public Subnet

resource "aws_route_table" "this" {
  vpc_id = aws_vpc.this.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.this.id
  }

  tags = merge(local.tags, tomap({ "Name" = "${var.namespace}-Public-Route-Table" }))

}

resource "aws_route_table_association" "this" {
  for_each       = aws_subnet.public_subnet
  subnet_id      = each.value.id
  route_table_id = aws_route_table.this.id

}

# Creating an Elastic IP for the NAT Gateway!
resource "aws_eip" "this" {
  domain = "vpc"

  tags = merge(local.tags, tomap({ "Name" = "${var.namespace}-eip" }))

}

# Creating a NAT Gateway!
resource "aws_nat_gateway" "this" {
  # Allocating the Elastic IP to the NAT Gateway!
  allocation_id = aws_eip.this.id

  # Associating it in the Public Subnet!
  subnet_id = values(aws_subnet.public_subnet)[0].id

  tags = merge(local.tags, tomap({ "Name" = "${var.namespace}-Nat-Gateway" }))

}

# Creating a Route Table for the Nat Gateway!
resource "aws_route_table" "private_rt" {
  vpc_id = aws_vpc.this.id

  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.this.id
  }

  tags = merge(local.tags, tomap({ "Name" = "${var.namespace}-Private-Route-Table" }))


}

# Creating an Route Table Association of the NAT Gateway route table with the Private Subnet!
resource "aws_route_table_association" "private_rt_association" {
  for_each       = aws_subnet.private_subnet
  subnet_id      = each.value.id
  route_table_id = aws_route_table.private_rt.id
}
