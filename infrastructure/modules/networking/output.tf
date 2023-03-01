output "vpc_id" {
  description = "VPC ID"
  value       = aws_vpc.this.id
}

output "serverless_security_group_id" {
  description = "Serverless Security Group ID"
  value       = aws_security_group.serverless_sg.id
}

output "private_security_group_id" {
  description = "Private Security Group ID"
  value       = aws_security_group.private_sg.id
}

output "public_security_group_id" {
  description = "Public Security Group ID"
  value       = aws_security_group.public_sg.id
}

output "public_subnet_id" {
  description = "Public Subnet ID"
  value       = aws_subnet.public_subnet.id
}

output "private_subnet_id" {
  description = "Private Subnet ID"
  value       = aws_subnet.private_subnet.id
}
