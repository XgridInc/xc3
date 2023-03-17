resource "aws_lb_target_group" "this" {
  name        = "${var.namespace}-target-group"
  port        = 80
  protocol    = "HTTP"
  vpc_id      = var.vpc_id
  target_type = "instance"

  health_check {
    path                = "/"
    timeout             = 60
    healthy_threshold   = 3
    unhealthy_threshold = 3
    interval            = 90
  }
  tags = merge(local.tags, tomap({ "Name" = "${local.tags.Project}-target-group" }))
}

resource "aws_lb_target_group_attachment" "this" {
  target_group_arn = aws_lb_target_group.this.arn
  target_id        = aws_instance.this.id
  port             = 3000
}

resource "aws_lb" "this" {
  name               = "${var.namespace}-load-balancer"
  internal           = false
  load_balancer_type = "application"

  subnets = [for id in var.public_subnet_ids : id]

  security_groups = [var.security_group_ids.aws_lb_security_group_id]
  tags            = merge(local.tags, tomap({ "Name" = "${local.tags.Project}-load-balancer" }))

}

resource "aws_lb_listener" "this" {
  load_balancer_arn = aws_lb.this.arn
  port              = "443"
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-2016-08"
  certificate_arn   = aws_acm_certificate.this.arn

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.this.arn
  }
}

resource "aws_acm_certificate" "this" {
  domain_name       = var.domain_name
  validation_method = "DNS"

  tags = merge(local.tags, tomap({ "Name" = "${local.tags.Project}-ssl-certificates" }))
}
