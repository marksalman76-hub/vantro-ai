# Dead Letter Queue must be declared first so main queue can reference it
resource "aws_sqs_queue" "media_jobs_dlq" {
  name                        = "${var.app_name}-media-jobs-dlq.fifo"
  fifo_queue                  = true
  content_based_deduplication = true
  message_retention_seconds   = 1209600 # 14 days

  tags = {
    Name = "${var.app_name}-media-jobs-dlq"
  }
}

# SQS Queue for Media Generation Jobs
resource "aws_sqs_queue" "media_jobs" {
  name                        = "${var.app_name}-media-jobs.fifo"
  fifo_queue                  = true
  content_based_deduplication = true
  visibility_timeout_seconds  = var.sqs_visibility_timeout
  message_retention_seconds   = var.sqs_message_retention

  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.media_jobs_dlq.arn
    maxReceiveCount     = 3
  })

  tags = {
    Name = "${var.app_name}-media-jobs"
  }
}

# SQS Queue Policy
resource "aws_sqs_queue_policy" "media_jobs" {
  queue_url = aws_sqs_queue.media_jobs.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
        Action = [
          "sqs:SendMessage",
          "sqs:ReceiveMessage",
          "sqs:DeleteMessage",
          "sqs:GetQueueAttributes"
        ]
        Resource = aws_sqs_queue.media_jobs.arn
      }
    ]
  })
}


# CloudWatch Alarm for Queue Depth
resource "aws_cloudwatch_metric_alarm" "sqs_queue_depth" {
  alarm_name          = "${var.app_name}-sqs-queue-depth"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "ApproximateNumberOfMessagesVisible"
  namespace           = "AWS/SQS"
  period              = "300"
  statistic           = "Average"
  threshold           = "100"
  alarm_description   = "Alert when SQS queue has more than 100 messages"
  treat_missing_data  = "notBreaching"

  dimensions = {
    QueueName = aws_sqs_queue.media_jobs.name
  }
}

# CloudWatch Alarm for Queue Age
resource "aws_cloudwatch_metric_alarm" "sqs_message_age" {
  alarm_name          = "${var.app_name}-sqs-message-age"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "ApproximateAgeOfOldestMessage"
  namespace           = "AWS/SQS"
  period              = "300"
  statistic           = "Maximum"
  threshold           = "3600"  # 1 hour
  alarm_description   = "Alert when oldest message is older than 1 hour"
  treat_missing_data  = "notBreaching"

  dimensions = {
    QueueName = aws_sqs_queue.media_jobs.name
  }
}


