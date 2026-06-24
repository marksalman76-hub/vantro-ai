# DB Subnet Group
resource "aws_db_subnet_group" "main" {
  name       = "${var.app_name}-db-subnet-group"
  subnet_ids = aws_subnet.private[*].id

  tags = {
    Name = "${var.app_name}-db-subnet-group"
  }
}

# RDS PostgreSQL Instance
resource "aws_db_instance" "main" {
  identifier              = "${var.app_name}-db"
  engine                  = "postgres"
  engine_version          = "15"
  instance_class          = var.rds_instance_class
  allocated_storage       = var.rds_allocated_storage
  storage_type            = "gp3"
  storage_encrypted       = true

  # Database Configuration
  db_name  = "vantro_db"
  username = "postgres"
  password = aws_secretsmanager_secret_version.db_password.secret_string

  # Multi-AZ for High Availability
  multi_az = var.enable_multi_az

  # Backup Configuration
  backup_retention_period = var.rds_backup_retention_days
  backup_window           = "03:00-04:00"
  maintenance_window      = "mon:04:00-mon:05:00"
  copy_tags_to_snapshot   = true

  # Network Configuration
  db_subnet_group_name            = aws_db_subnet_group.main.name
  publicly_accessible             = false
  vpc_security_group_ids          = [aws_security_group.rds.id]
  parameter_group_name            = aws_db_parameter_group.main.name

  # Enhanced Monitoring
  enabled_cloudwatch_logs_exports = ["postgresql"]

  # Deletion Protection
  skip_final_snapshot       = false
  final_snapshot_identifier = "${var.app_name}-db-final-snapshot-${formatdate("YYYY-MM-DD-hhmm", timestamp())}"

  tags = {
    Name = "${var.app_name}-db"
  }

  depends_on = [
    aws_secretsmanager_secret_version.db_password
  ]
}

# DB Parameter Group
resource "aws_db_parameter_group" "main" {
  family      = "postgres15"
  name        = "${var.app_name}-db-params"
  description = "Parameter group for ${var.app_name}"

  parameter {
    name  = "log_connections"
    value = "1"
  }

  parameter {
    name  = "log_disconnections"
    value = "1"
  }

  parameter {
    name  = "log_duration"
    value = "1"
  }

  tags = {
    Name = "${var.app_name}-db-parameter-group"
  }
}

# RDS Read Replica — routes read-heavy GET traffic away from the primary
resource "aws_db_instance" "read_replica" {
  identifier             = "${var.app_name}-db-replica"
  replicate_source_db    = aws_db_instance.main.identifier
  instance_class         = var.rds_instance_class
  storage_type           = "gp3"
  storage_encrypted      = true
  publicly_accessible    = false
  vpc_security_group_ids = [aws_security_group.rds.id]
  parameter_group_name   = aws_db_parameter_group.main.name
  skip_final_snapshot    = true

  # Read replicas don't need independent backups — they inherit from primary
  backup_retention_period = 0

  tags = {
    Name = "${var.app_name}-db-replica"
    Role = "read-replica"
  }

  depends_on = [aws_db_instance.main]
}

output "rds_replica_endpoint" {
  description = "Read replica endpoint — use as DATABASE_REPLICA_URL in ECS task env"
  value       = aws_db_instance.read_replica.endpoint
  sensitive   = false
}

# CloudWatch Alarm for DB CPU Utilization
resource "aws_cloudwatch_metric_alarm" "rds_cpu" {
  alarm_name          = "${var.app_name}-rds-high-cpu"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/RDS"
  period              = "300"
  statistic           = "Average"
  threshold           = "80"
  alarm_description   = "Alert when RDS CPU exceeds 80%"
  treat_missing_data  = "notBreaching"

  dimensions = {
    DBInstanceIdentifier = aws_db_instance.main.id
  }
}

# CloudWatch Alarm for DB Storage
resource "aws_cloudwatch_metric_alarm" "rds_storage" {
  alarm_name          = "${var.app_name}-rds-low-storage"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "FreeStorageSpace"
  namespace           = "AWS/RDS"
  period              = "300"
  statistic           = "Average"
  threshold           = "2147483648"  # 2GB
  alarm_description   = "Alert when RDS storage is below 2GB"
  treat_missing_data  = "notBreaching"

  dimensions = {
    DBInstanceIdentifier = aws_db_instance.main.id
  }
}


