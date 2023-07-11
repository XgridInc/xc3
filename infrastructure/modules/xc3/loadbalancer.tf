# Copyright (c) 2023, Xgrid Inc, https://xgrid.co

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#        http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

resource "aws_lb_target_group" "this" {
  count = var.env == "prod" ? 1 : 0
  #ts:skip=AWS.ALTG.IS.MEDIUM.0042 We are aware of the risk and choose to skip this rule
  name        = "${var.namespace}-target-group"
  port        = 80
  protocol    = "HTTP"
  vpc_id      = var.vpc_id
  target_type = "instance"

  health_check {
    path                = "/"
    timeout             = 120
    healthy_threshold   = 3
    unhealthy_threshold = 3
    interval            = 200
  }
  tags = merge(local.tags, tomap({ "Name" = "${var.namespace}-target-group" }))
}

resource "aws_lb_target_group_attachment" "this" {
  count            = var.env == "prod" ? 1 : 0
  target_group_arn = aws_lb_target_group.this[0].arn
  target_id        = aws_instance.this.id
  port             = 3000

}

resource "aws_lb" "this" {
  count                      = var.env == "prod" ? 1 : 0
  name                       = "${var.namespace}-load-balancer"
  internal                   = false
  load_balancer_type         = "application"
  enable_deletion_protection = false

  subnets = [for id in var.public_subnet_ids : id]

  security_groups = [var.security_group_ids.aws_lb_security_group_id]
  tags            = merge(local.tags, tomap({ "Name" = "${var.namespace}-load-balancer" }))

  drop_invalid_header_fields = true

}

resource "aws_lb_listener" "this" {
  count             = var.env == "prod" && var.domain_name != "" ? 1 : 0
  load_balancer_arn = aws_lb.this[0].arn
  port              = "443"
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-TLS-1-2-2017-01"
  certificate_arn   = data.aws_acm_certificate.issued[0].arn
  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.this[0].arn
  }
}

resource "aws_lb_listener" "http" {
  #ts:skip=AWS.ALL.IS.MEDIUM.0046
  count             = var.env == "prod" && var.domain_name == "" ? 1 : 0
  load_balancer_arn = aws_lb.this[0].arn
  port              = "80"
  protocol          = "HTTP"
  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.this[0].arn
  }
}

resource "aws_route53_record" "xc3_alias" {
  count   = var.domain_name != "" ? 1 : 0
  name    = var.domain_name
  type    = "A"
  zone_id = var.hosted_zone_id

  alias {
    name                   = aws_lb.this[0].dns_name
    zone_id                = aws_lb.this[0].zone_id
    evaluate_target_health = true
  }

}
