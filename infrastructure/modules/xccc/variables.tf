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

variable "sqs_queue_name" {
  type        = string
  description = "The name of the SQS queue"
}

variable "namespace" {
  type        = string
  description = "The namespace referring to an env"
}

variable "key" {
  type        = string
  description = "The name of the key used for an env"
}
