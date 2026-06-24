# AWS WAF v2 — rate limiting + OWASP managed rules attached to the ALB
# Blocks: per-IP rate abuse, common web exploits, SQLi, known bad inputs.

resource "aws_wafv2_web_acl" "main" {
  name        = "${var.app_name}-waf"
  description = "Vantro WAF — rate limiting and OWASP managed rule groups"
  scope       = "REGIONAL"

  default_action {
    allow {}
  }

  # Rule 1: Per-IP rate limit — 2000 requests per 5 minutes
  rule {
    name     = "rate-limit-per-ip"
    priority = 1
    action { block {} }
    statement {
      rate_based_statement {
        limit              = 2000
        aggregate_key_type = "IP"
      }
    }
    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "${var.app_name}-rate-limit"
      sampled_requests_enabled   = true
    }
  }

  # Rule 2: Strict rate limit on auth endpoints — 100 per IP per 5 minutes
  rule {
    name     = "rate-limit-auth"
    priority = 2
    action { block {} }
    statement {
      rate_based_statement {
        limit              = 100
        aggregate_key_type = "IP"
        scope_down_statement {
          byte_match_statement {
            search_string         = "/api/auth/"
            positional_constraint = "STARTS_WITH"
            field_to_match { uri_path {} }
            text_transformation {
              priority = 0
              type     = "LOWERCASE"
            }
          }
        }
      }
    }
    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "${var.app_name}-auth-rate-limit"
      sampled_requests_enabled   = true
    }
  }

  # Rule 3: AWS Managed Common Rules (XSS, LFI, RFI, path traversal, etc.)
  rule {
    name     = "aws-managed-common-rules"
    priority = 3
    override_action { none {} }
    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesCommonRuleSet"
        vendor_name = "AWS"
      }
    }
    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "${var.app_name}-common-rules"
      sampled_requests_enabled   = true
    }
  }

  # Rule 4: AWS Managed SQL Injection Rules
  rule {
    name     = "aws-managed-sqli-rules"
    priority = 4
    override_action { none {} }
    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesSQLiRuleSet"
        vendor_name = "AWS"
      }
    }
    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "${var.app_name}-sqli-rules"
      sampled_requests_enabled   = true
    }
  }

  # Rule 5: AWS Known Bad Inputs (Log4J shellcode, etc.)
  rule {
    name     = "aws-managed-known-bad-inputs"
    priority = 5
    override_action { none {} }
    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesKnownBadInputsRuleSet"
        vendor_name = "AWS"
      }
    }
    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "${var.app_name}-known-bad-inputs"
      sampled_requests_enabled   = true
    }
  }

  visibility_config {
    cloudwatch_metrics_enabled = true
    metric_name                = "${var.app_name}-waf"
    sampled_requests_enabled   = true
  }

  tags = {
    Name        = "${var.app_name}-waf"
    Environment = var.environment
  }
}

# Associate WAF with the ALB
resource "aws_wafv2_web_acl_association" "alb" {
  resource_arn = aws_lb.main.arn
  web_acl_arn  = aws_wafv2_web_acl.main.arn
}

# Alarm: WAF blocking surge — potential DDoS or scanning attack
resource "aws_cloudwatch_metric_alarm" "waf_blocked_surge" {
  alarm_name          = "${var.app_name}-waf-blocked-surge"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "BlockedRequests"
  namespace           = "AWS/WAFV2"
  period              = "300"
  statistic           = "Sum"
  threshold           = "200"
  alarm_description   = "WAF blocking >200 requests in 5 min — potential attack in progress"
  treat_missing_data  = "notBreaching"
  alarm_actions       = [aws_sns_topic.alerts.arn]

  dimensions = {
    WebACL = aws_wafv2_web_acl.main.name
    Rule   = "ALL"
    Region = var.region
  }
}

output "waf_web_acl_arn" {
  description = "WAF WebACL ARN — can also be attached to CloudFront for edge protection"
  value       = aws_wafv2_web_acl.main.arn
}
