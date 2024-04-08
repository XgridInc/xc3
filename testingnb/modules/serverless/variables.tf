 variable "snsendpoint" {
    type = string
    description = "endpoint for email notification"
}

variable "slack_webhook_url" {
    type = string
    description = "Webhook URL for slack notification."
}

variable "region" {
    type = string
    description = "Region for your AWS"
}

variable "Owner" {
    type = string
    description = "Owner of the resource"
}

variable "Creator" {
    type = string
    description = "Creator of the resource"
}

variable "Project" {
    type = string
    description = "Name of the project"
}

variable "namespace" {
  type        = string
  description = "The namespace referring to an env"
}

