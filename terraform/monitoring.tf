# SNS Topic for all CloudWatch alarm notifications
resource "aws_sns_topic" "alerts" {
  name = "${var.app_name}-alerts"

  tags = {
    Name = "${var.app_name}-alerts"
  }
}

resource "aws_sns_topic_subscription" "admin_email" {
  topic_arn = aws_sns_topic.alerts.arn
  protocol  = "email"
  endpoint  = var.admin_email
}

locals {
  sns_arn = aws_sns_topic.alerts.arn
}

# SNS-wired alarms (dedicated notification alarms separate from base alarms)
resource "aws_cloudwatch_metric_alarm" "alb_unhealthy_hosts_sns" {
  alarm_name          = "${var.app_name}-alb-unhealthy-hosts-notify"
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = "2"
  metric_name         = "UnHealthyHostCount"
  namespace           = "AWS/ApplicationELB"
  period              = "300"
  statistic           = "Average"
  threshold           = "1"
  alarm_description   = "ALB has unhealthy targets — notify admin"
  treat_missing_data  = "notBreaching"
  alarm_actions       = [local.sns_arn]
  ok_actions          = [local.sns_arn]

  dimensions = {
    LoadBalancer = aws_lb.main.arn_suffix
    TargetGroup  = aws_lb_target_group.main.arn_suffix
  }
}

resource "aws_cloudwatch_metric_alarm" "ecs_cpu_sns" {
  alarm_name          = "${var.app_name}-ecs-high-cpu-notify"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/ECS"
  period              = "300"
  statistic           = "Average"
  threshold           = "85"
  alarm_description   = "ECS CPU >85% — may need manual scale-up"
  treat_missing_data  = "notBreaching"
  alarm_actions       = [local.sns_arn]

  dimensions = {
    ClusterName = aws_ecs_cluster.main.name
    ServiceName = aws_ecs_service.main.name
  }
}

resource "aws_cloudwatch_metric_alarm" "rds_cpu_sns" {
  alarm_name          = "${var.app_name}-rds-high-cpu-notify"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/RDS"
  period              = "300"
  statistic           = "Average"
  threshold           = "80"
  alarm_description   = "RDS CPU >80%"
  treat_missing_data  = "notBreaching"
  alarm_actions       = [local.sns_arn]

  dimensions = {
    DBInstanceIdentifier = aws_db_instance.main.id
  }
}

resource "aws_cloudwatch_metric_alarm" "sqs_depth_sns" {
  alarm_name          = "${var.app_name}-sqs-deep-queue-notify"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "ApproximateNumberOfMessagesVisible"
  namespace           = "AWS/SQS"
  period              = "300"
  statistic           = "Average"
  threshold           = "100"
  alarm_description   = "SQS queue depth >100 — worker may be backed up"
  treat_missing_data  = "notBreaching"
  alarm_actions       = [local.sns_arn]

  dimensions = {
    QueueName = aws_sqs_queue.media_jobs.name
  }
}

# ALB 5xx error rate — fires when server-side errors spike
resource "aws_cloudwatch_metric_alarm" "alb_5xx_errors" {
  alarm_name          = "${var.app_name}-alb-5xx-spike"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "HTTPCode_Target_5XX_Count"
  namespace           = "AWS/ApplicationELB"
  period              = "300"
  statistic           = "Sum"
  threshold           = "10"
  alarm_description   = "ALB recording >10 5xx errors in 5 minutes — investigate immediately"
  treat_missing_data  = "notBreaching"
  alarm_actions       = [local.sns_arn]
  ok_actions          = [local.sns_arn]

  dimensions = {
    LoadBalancer = aws_lb.main.arn_suffix
  }
}

# DLQ depth — jobs that failed all 3 SQS retries need human review
resource "aws_cloudwatch_metric_alarm" "sqs_dlq_depth" {
  alarm_name          = "${var.app_name}-sqs-dlq-not-empty"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "ApproximateNumberOfMessagesVisible"
  namespace           = "AWS/SQS"
  period              = "300"
  statistic           = "Sum"
  threshold           = "0"
  alarm_description   = "SQS DLQ has messages — jobs are failing after all retries"
  treat_missing_data  = "notBreaching"
  alarm_actions       = [local.sns_arn]

  dimensions = {
    QueueName = aws_sqs_queue.media_jobs_dlq.name
  }
}

# ECS memory pressure — fires before OOM kills start
resource "aws_cloudwatch_metric_alarm" "ecs_memory_sns" {
  alarm_name          = "${var.app_name}-ecs-high-memory-notify"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "MemoryUtilization"
  namespace           = "AWS/ECS"
  period              = "300"
  statistic           = "Average"
  threshold           = "85"
  alarm_description   = "ECS memory >85% — scale-out or investigate memory leak"
  treat_missing_data  = "notBreaching"
  alarm_actions       = [local.sns_arn]

  dimensions = {
    ClusterName = aws_ecs_cluster.main.name
    ServiceName = aws_ecs_service.main.name
  }
}

# CloudWatch Dashboard — single pane of glass for production health
resource "aws_cloudwatch_dashboard" "main" {
  dashboard_name = "${var.app_name}-production"

  dashboard_body = jsonencode({
    widgets = [
      {
        type   = "metric"
        x      = 0
        y      = 0
        width  = 12
        height = 6
        properties = {
          title  = "ECS CPU & Memory"
          view   = "timeSeries"
          region = var.region
          metrics = [
            ["AWS/ECS", "CPUUtilization", "ClusterName", "${var.app_name}-cluster", "ServiceName", "${var.app_name}-service", { label = "CPU %" }],
            ["AWS/ECS", "MemoryUtilization", "ClusterName", "${var.app_name}-cluster", "ServiceName", "${var.app_name}-service", { label = "Memory %" }]
          ]
          yAxis = { left = { min = 0, max = 100 } }
        }
      },
      {
        type   = "metric"
        x      = 12
        y      = 0
        width  = 12
        height = 6
        properties = {
          title  = "ALB Request Count & Errors"
          view   = "timeSeries"
          region = var.region
          metrics = [
            ["AWS/ApplicationELB", "RequestCount", "LoadBalancer", "${var.app_name}-alb", { stat = "Sum", label = "Total Requests" }],
            ["AWS/ApplicationELB", "HTTPCode_Target_5XX_Count", "LoadBalancer", "${var.app_name}-alb", { stat = "Sum", label = "5xx Errors" }],
            ["AWS/ApplicationELB", "TargetResponseTime", "LoadBalancer", "${var.app_name}-alb", { stat = "Average", label = "Response Time (s)" }]
          ]
        }
      },
      {
        type   = "metric"
        x      = 0
        y      = 6
        width  = 12
        height = 6
        properties = {
          title  = "RDS Performance"
          view   = "timeSeries"
          region = var.region
          metrics = [
            ["AWS/RDS", "CPUUtilization", "DBInstanceIdentifier", "${var.app_name}-db", { label = "CPU %" }],
            ["AWS/RDS", "DatabaseConnections", "DBInstanceIdentifier", "${var.app_name}-db", { label = "Connections" }],
            ["AWS/RDS", "FreeStorageSpace", "DBInstanceIdentifier", "${var.app_name}-db", { label = "Free Storage (bytes)" }]
          ]
        }
      },
      {
        type   = "metric"
        x      = 12
        y      = 6
        width  = 12
        height = 6
        properties = {
          title  = "SQS Queue Depth"
          view   = "timeSeries"
          region = var.region
          metrics = [
            ["AWS/SQS", "ApproximateNumberOfMessagesVisible", "QueueName", "${var.app_name}-media-jobs.fifo", { label = "Queue Depth" }],
            ["AWS/SQS", "ApproximateAgeOfOldestMessage", "QueueName", "${var.app_name}-media-jobs.fifo", { label = "Oldest Message Age (s)" }],
            ["AWS/SQS", "ApproximateNumberOfMessagesVisible", "QueueName", "${var.app_name}-media-jobs-dlq.fifo", { label = "DLQ Depth" }]
          ]
        }
      }
    ]
  })
}
