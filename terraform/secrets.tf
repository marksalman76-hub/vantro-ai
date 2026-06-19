# Database Password Secret
resource "aws_secretsmanager_secret" "db_password" {
  name                    = "${var.app_name}/db-password"
  recovery_window_in_days = 7

  tags = {
    Name = "${var.app_name}-db-password"
  }
}

# Generate random password for database
resource "random_password" "db_password" {
  length           = 32
  special          = true
  override_special = "!#$%&*()-_=+[]{}<>:?"
}

# Store database password in Secrets Manager
resource "aws_secretsmanager_secret_version" "db_password" {
  secret_id     = aws_secretsmanager_secret.db_password.id
  secret_string = random_password.db_password.result
}

# API Keys Secret
resource "aws_secretsmanager_secret" "api_keys" {
  name                    = "${var.app_name}/api-keys"
  recovery_window_in_days = 7

  tags = {
    Name = "${var.app_name}-api-keys"
  }
}

# Store API keys placeholder in Secrets Manager
resource "aws_secretsmanager_secret_version" "api_keys" {
  secret_id = aws_secretsmanager_secret.api_keys.id
  secret_string = jsonencode({
    JWT_SECRET         = "PLACEHOLDER_JWT_SECRET_CHANGE_IN_PRODUCTION"
    STRIPE_API_KEY     = "PLACEHOLDER_STRIPE_KEY_CHANGE_IN_PRODUCTION"
    OPENAI_API_KEY     = "PLACEHOLDER_OPENAI_KEY_CHANGE_IN_PRODUCTION"
    ANTHROPIC_API_KEY  = "PLACEHOLDER_ANTHROPIC_KEY_CHANGE_IN_PRODUCTION"
  })
}

# CloudWatch Alarm for Secret Rotation
resource "aws_cloudwatch_metric_alarm" "secrets_access" {
  alarm_name          = "${var.app_name}-secrets-rotation"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "UserErrorCount"
  namespace           = "AWS/SecretsManager"
  period              = "300"
  statistic           = "Sum"
  threshold           = "10"
  alarm_description   = "Alert on excessive secret access errors"
  treat_missing_data  = "notBreaching"
}