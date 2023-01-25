output "vpc_id" {
  description = "VPC ID"
  value       = aws_vpc.this.id
}

output "security_group_id" {
  description = "Security Group ID"
  value       = aws_security_group.this.id
}

output "subnet_id" {
  description = "Subnet ID"
  value       = aws_subnet.this.id
}
