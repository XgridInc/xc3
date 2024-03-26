variable "region" {
    type = string
    description = "Region for your AWS"
}

variable "snsendpoint" {
    type = string
    description = "endpoint for email notification"
}

variable "slack_webhook_url" {
    type = string
    description = "Webhook URL for slack notification."
}