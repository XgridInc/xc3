variable "vpc_cidr_block" {
  type        = string
  description = "AWS VPC CIDR range"
}

variable "subnet1_cidr_block" {
  type        = string
  description = "AWS VPC CIDR range for subnet 1"
}

variable "namespace" {
  type        = string
  description = "The namespace referring to an environment"
}

variable "key" {
  type        = string
  description = "The name of the key used for an environment"
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
