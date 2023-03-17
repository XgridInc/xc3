variable "namespace" {
  type        = string
  description = "The namespace referring to an env"
}

variable "region" {
  type        = string
  description = "AWS region where resources will be deployed"
}

variable "vpc_cidr_block" {
  type        = string
  description = "VPC CIDR Block"
}

variable "public_subnet_cidr_block" {
  type        = map(string)
  description = "The CIDR Blocks of the public subnet"
}

variable "private_subnet_cidr_block" {
  type        = string
  description = "The CIDR Block of the private subnet"
}

variable "allow_traffic" {
  type        = list(string)
  description = "IP Address to access bastion host server"
}

variable "ses_email_address" {
  type        = string
  description = "The email address for SES identity"
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

variable "creator_email" {
  type        = string
  description = "Email address of a person who is provisioning the infrastructure"
}

variable "prometheus_layer" {
  description = "S3 key for prometheus layer"
}

variable "mysql_layer" {
  description = "S3 key for mysql layer"
}

variable "memory_size" {
  description = "The amount of memory to allocate to the lambda function"
}

variable "timeout" {
  type        = number
  description = "The number of seconds before the lambda function times out"
}

variable "total_account_cost_lambda" {
  type        = string
  description = "The name of the lambda function that will be used to calculate cost metrics of provided AWS Account"
}

variable "account_id" {
  type        = string
  description = "AWS Account id in which infrastructure will be deployed"
}

variable "total_account_cost_cronjob" {
  type        = string
  description = "Cron Job frequency for Total Account Cost"
}

variable "domain_name" {
  type        = string
  description = "Domain name for SSL Certificates"
}
