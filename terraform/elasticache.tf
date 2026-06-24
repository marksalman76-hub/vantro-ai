# ElastiCache Redis — token revocation blocklist, rate limiting, response caching
# Deployed into private subnets; accessible only from ECS task security group.

resource "aws_security_group" "redis" {
  name        = "${var.app_name}-redis-sg"
  description = "Redis — allow access from ECS tasks only"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port       = 6379
    to_port         = 6379
    protocol        = "tcp"
    security_groups = [aws_security_group.ecs_tasks.id]
    description     = "Redis from ECS tasks"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = { Name = "${var.app_name}-redis-sg" }
}

resource "aws_elasticache_subnet_group" "main" {
  name       = "${var.app_name}-redis-subnet-group"
  subnet_ids = aws_subnet.private[*].id

  tags = { Name = "${var.app_name}-redis-subnet-group" }
}

resource "aws_elasticache_replication_group" "main" {
  replication_group_id       = "${var.app_name}-redis"
  description                = "Vantro Redis — token revocation, rate limiting, session cache"
  node_type                  = var.redis_node_type
  num_cache_clusters         = var.redis_num_cache_nodes
  automatic_failover_enabled = false
  parameter_group_name       = "default.redis7"
  engine_version             = "7.0"
  port                       = 6379
  subnet_group_name          = aws_elasticache_subnet_group.main.name
  security_group_ids         = [aws_security_group.redis.id]
  at_rest_encryption_enabled = true
  transit_encryption_enabled = true
  multi_az_enabled           = false
  apply_immediately          = false
  maintenance_window         = "sun:05:00-sun:06:00"
  snapshot_retention_limit   = 1
  snapshot_window            = "04:00-05:00"

  tags = {
    Name        = "${var.app_name}-redis"
    Environment = var.environment
  }
}

# CloudWatch alarm: Redis CPU spike
resource "aws_cloudwatch_metric_alarm" "redis_cpu" {
  alarm_name          = "${var.app_name}-redis-high-cpu"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/ElastiCache"
  period              = "300"
  statistic           = "Average"
  threshold           = "75"
  alarm_description   = "ElastiCache Redis CPU >75%"
  treat_missing_data  = "notBreaching"
  alarm_actions       = [aws_sns_topic.alerts.arn]

  dimensions = {
    ReplicationGroupId = aws_elasticache_replication_group.main.id
  }
}

output "redis_endpoint" {
  description = "ElastiCache Redis primary endpoint — set as REDIS_URL in ECS task secrets"
  value       = "rediss://${aws_elasticache_replication_group.main.primary_endpoint_address}:6379"
  sensitive   = true
}
