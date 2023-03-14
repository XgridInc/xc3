variable "region" {
  type        = string
  description = "The name of the region in which infrastructure will be provisioned"
}

variable "vpc_id" {
  type        = string
  description = "The ID of the VPC where the resources will be created"
}

variable "subnet_id" {
  type        = string
  description = "The ID of the subnet where the resources will be created"
}

variable "security_group_id" {
  type        = string
  description = "The ID of the security group that will be associated with the resources"
}

variable "public_subnet_id" {
  type        = string
  description = "The ID of the public subnet where the bastion host server will be created"
}

variable "public_security_group_id" {
  type        = string
  description = "The ID of the security group that will be associated with the bastion host"
}

variable "instance_type" {
  type        = string
  description = "The type of the EC2 instance"
  default     = "t2.micro"
}

variable "ssh_key" {
  type        = string
  description = "SSH Key Name for the EC2 instance"
}

variable "ses_email_address" {
  type        = string
  description = "The email address for SES identity"
}

variable "prometheus_layer" {
  description = "S3 key for prometheus layer"
}

variable "mysql_layer" {
  description = "S3 key for mysql layer"
}

variable "namespace" {
  type        = string
  description = "The namespace referring to an env"
}

variable "owner_email" {
  type        = string
  description = "Email address of a owner who is leading the team"
}

variable "creator_email" {
  type        = string
  description = "The name of the S3 bucket for storage of cc policies metadata"
}
