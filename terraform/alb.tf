# Application Load Balancer
resource "aws_lb" "main" {
  name               = "${var.app_name}-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = aws_subnet.public[*].id

  enable_deletion_protection = true
  enable_http2              = true

  tags = {
    Name = "${var.app_name}-alb"
  }
}

# ALB Target Group
resource "aws_lb_target_group" "main" {
  name        = "${var.app_name}-tg"
  port        = var.container_port
  protocol    = "HTTP"
  vpc_id      = aws_vpc.main.id
  target_type = "ip"

  health_check {
    healthy_threshold   = 2
    unhealthy_threshold = 2
    timeout             = 5
    interval            = 30
    path                = "/health"
    matcher             = "200"
  }

  stickiness {
    type            = "lb_cookie"
    enabled         = true
    cookie_duration = 86400
  }

  tags = {
    Name = "${var.app_name}-target-group"
  }
}

# ACM Certificate for HTTPS
resource "aws_acm_certificate" "main" {
  domain_name               = var.domain_name
  subject_alternative_names = ["*.${var.domain_name}"]
  validation_method         = "DNS"

  lifecycle {
    create_before_destroy = true
  }

  tags = {
    Name = "${var.app_name}-cert"
  }
}

# DNS validation record (add these CNAMEs to your DNS provider)
resource "aws_acm_certificate_validation" "main" {
  certificate_arn = aws_acm_certificate.main.arn
  # validation_record_fqdns must be added manually to DNS if not using Route53
  # Outputs will show the required CNAME records
}

# ALB Listener — HTTP redirects to HTTPS (port 80 → 443)
resource "aws_lb_listener" "http_redirect" {
  load_balancer_arn = aws_lb.main.arn
  port              = "80"
  protocol          = "HTTP"

  default_action {
    type = "redirect"
    redirect {
      port        = "443"
      protocol    = "HTTPS"
      status_code = "HTTP_301"
    }
  }
}

# ALB Listener — HTTPS (port 443)
resource "aws_lb_listener" "https" {
  load_balancer_arn = aws_lb.main.arn
  port              = "443"
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-TLS13-1-2-2021-06"
  certificate_arn   = aws_acm_certificate.main.arn

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.main.arn
  }

  depends_on = [aws_acm_certificate_validation.main]
}

# Output the DNS validation CNAME records needed for ACM cert
output "acm_validation_records" {
  description = "Add these CNAME records to your DNS provider to validate the ACM certificate"
  value = {
    for dvo in aws_acm_certificate.main.domain_validation_options : dvo.domain_name => {
      name  = dvo.resource_record_name
      type  = dvo.resource_record_type
      value = dvo.resource_record_value
    }
  }
}

# CloudWatch Alarm for ALB Health
resource "aws_cloudwatch_metric_alarm" "alb_unhealthy_hosts" {
  alarm_name          = "${var.app_name}-alb-unhealthy-hosts"
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = "2"
  metric_name         = "UnHealthyHostCount"
  namespace           = "AWS/ApplicationELB"
  period              = "300"
  statistic           = "Average"
  threshold           = "1"
  alarm_description   = "Alert when ALB has unhealthy targets"
  treat_missing_data  = "notBreaching"

  dimensions = {
    LoadBalancer = aws_lb.main.arn_suffix
    TargetGroup  = aws_lb_target_group.main.arn_suffix
  }
}

# CloudWatch Alarm for ALB Target Response Time
resource "aws_cloudwatch_metric_alarm" "alb_response_time" {
  alarm_name          = "${var.app_name}-alb-high-response-time"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "TargetResponseTime"
  namespace           = "AWS/ApplicationELB"
  period              = "300"
  statistic           = "Average"
  threshold           = "1"  # 1 second
  alarm_description   = "Alert when ALB response time exceeds 1 second"
  treat_missing_data  = "notBreaching"

  dimensions = {
    LoadBalancer = aws_lb.main.arn_suffix
  }
}


