variable "vpc_cidr_block" {
  type        = string
  description = "AWS VPC CIDR range"
}

variable "public_subnet_cidr_block" {
  type        = string
  description = "AWS VPC CIDR range for public subnet"
}

variable "allow_traffic" {
  type        = list(string)
  description = "IP Address to access bastion host server"
}

variable "private_subnet_cidr_block" {
  type        = string
  description = "AWS VPC CIDR range for private subnet"
}

variable "namespace" {
  type        = string
  description = "The namespace referring to an environment"
}

variable "owner_email" {
  type        = string
  description = "Email address of the team working in this project"
}

variable "creator_email" {
  type        = string
  description = "Email address of a person who is provisioning the infrastructure of x-ccc"
}

variable "key" {
  type        = string
  description = "The name of the key used for an environment"
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
