# AWS SNS Topic creation
# -----------------------
# This section creates an AWS SNS Topic named "resource_alert" to be used for resource alerts.

resource "aws_sns_topic" "resource_alert" {
  # Topic Name
  # ----------
  # Specifies the name of the SNS topic.
  name        = "${var.namespace}-resource_alert"
  
  # Display Name
  # ------------
  # Specifies the display name of the SNS topic.
  display_name = "Resource Alert"
}

# Subscription of an email address to the SNS topic
# -------------------------------------------------
# This section subscribes an email address to the "resource_alert" SNS topic for receiving notifications.

resource "aws_sns_topic_subscription" "email_subscription" {
  # Topic ARN
  # ---------
  # Specifies the ARN of the SNS topic to which the subscription will be made.
  topic_arn = aws_sns_topic.resource_alert.arn
  
  # Protocol
  # --------
  # Specifies the protocol for the subscription. In this case, it's email.
  protocol  = "email"
  
  # Endpoint
  # --------
  # Specifies the endpoint for the subscription, which is an email address.
  endpoint  = var.snsendpoint


}
