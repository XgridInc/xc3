variable "profile" {
  type        = string
  description = "The name of aws profile"
}

variable "region" {
  type        = string
  description = "AWS region where resources will be deployed"
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

variable "ses_email_address" {
  type        = string
  description = "The email address for SES identity"
}

variable "sqs_queue_name" {
  type        = string
  default     = "xccc-notification-queue"
  description = "The name of the SQS queue"
}

variable "instance_type" {
  type        = string
  description = "The type of the EC2 instance"
  default     = "t2.micro"
}

variable "ssh_key" {
  type        = string
  description = "The Name of SSH Key Pair for EC2 instance"
}
