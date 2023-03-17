output "vpc_id" {
  description = "VPC ID"
  value       = aws_vpc.this.id
}

output "security_group_ids" {
  description = "Map of security group IDs"
  value = {
    aws_lb_security_group_id     = aws_security_group.lb_sg.id
    serverless_security_group_id = aws_security_group.serverless_sg.id
    private_security_group_id    = aws_security_group.private_sg.id
    public_security_group_id     = aws_security_group.public_sg.id
  }
}

output "public_subnet_ids" {
  description = "List of Public Subnet IDs"
  value       = [for subnet in aws_subnet.public_subnet : subnet.id]
}

output "private_subnet_id" {
  description = "Private Subnet ID"
  value       = aws_subnet.private_subnet.id
}
