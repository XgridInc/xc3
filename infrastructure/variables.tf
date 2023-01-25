variable "profile" {
  type        = string
  description = "The name of AWS Profile"
}

variable "region" {
  type        = string
  description = "AWS region where resources will be deployed"
}
variable "vpc_cidr_block" {
  type        = string
  description = "VPC CIDR Block"
}

variable "subnet1_cidr_block" {
  type        = string
  description = "The CIDR Block of the subnet 1"
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

variable "allow_traffic" {
  type        = string
  description = "CIDR Block to allow traffic"
}

variable "security_group_ingress" {
  type = map(object({
    description = string
    from_port   = number
    to_port     = number
    protocol    = string
    cidr_blocks = list(string)
  }))
  description = "Security Group Ingress Rules"
}
