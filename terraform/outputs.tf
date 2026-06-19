# RDS Endpoint
output "rds_endpoint" {
  description = "RDS database endpoint"
  value       = aws_db_instance.main.endpoint
}
output "rds_database_name" {
  description = "RDS database name"
  value       = aws_db_instance.main.db_name
}
output "rds_username" {
  description = "RDS master username"
  value       = aws_db_instance.main.username
}
# S3 Buckets
output "media_bucket_name" {
  description = "S3 bucket for media storage"
  value       = aws_s3_bucket.media.id
}
output "media_bucket_arn" {
  description = "ARN of media storage bucket"
  value       = aws_s3_bucket.media.arn
}
output "backups_bucket_name" {
  description = "S3 bucket for backups"
  value       = aws_s3_bucket.backups.id
}
output "backups_bucket_arn" {
  description = "ARN of backups bucket"
  value       = aws_s3_bucket.backups.arn
}
# SQS Queue
output "sqs_queue_url" {
  description = "SQS queue URL for media jobs"
  value       = aws_sqs_queue.media_jobs.url
}
output "sqs_queue_arn" {
  description = "SQS queue ARN"
  value       = aws_sqs_queue.media_jobs.arn
}
output "sqs_queue_name" {
  description = "SQS queue name"
  value       = aws_sqs_queue.media_jobs.name
}
output "sqs_dlq_url" {
  description = "SQS dead letter queue URL"
  value       = aws_sqs_queue.media_jobs_dlq.url
}
# ALB
output "alb_dns_name" {
  description = "DNS name of the load balancer"
  value       = aws_lb.main.dns_name
}
output "alb_arn" {
  description = "ARN of the load balancer"
  value       = aws_lb.main.arn
}
output "alb_zone_id" {
  description = "Zone ID of the load balancer"
  value       = aws_lb.main.zone_id
}
# ECS Cluster (Service commented out in ecs.tf)
output "ecs_cluster_name" {
  description = "Name of the ECS cluster"
  value       = aws_ecs_cluster.main.name
}
output "ecs_cluster_arn" {
  description = "ARN of the ECS cluster"
  value       = aws_ecs_cluster.main.arn
}
# COMMENTED OUT - ECS Service (not deployed yet)
# output "ecs_service_name" {
#   description = "Name of the ECS service"
#   value       = aws_ecs_service.main.name
# }

# VPC
output "vpc_id" {
  description = "ID of the VPC"
  value       = aws_vpc.main.id
}
output "private_subnets" {
  description = "IDs of private subnets"
  value       = aws_subnet.private[*].id
}
output "public_subnets" {
  description = "IDs of public subnets"
  value       = aws_subnet.public[*].id
}
# Secrets Manager
output "db_password_secret_arn" {
  description = "ARN of the database password secret"
  value       = aws_secretsmanager_secret.db_password.arn
}
output "api_keys_secret_arn" {
  description = "ARN of the API keys secret"
  value       = aws_secretsmanager_secret.api_keys.arn
}
# CloudWatch Log Group
output "cloudwatch_log_group_name" {
  description = "Name of CloudWatch log group for ECS"
  value       = aws_cloudwatch_log_group.ecs.name
}
output "cloudwatch_log_group_arn" {
  description = "ARN of CloudWatch log group"
  value       = aws_cloudwatch_log_group.ecs.arn
}
# Connection String (for reference)
output "database_connection_string" {
  description = "PostgreSQL connection string (use environment variables for password)"
  value       = "postgresql://${aws_db_instance.main.username}@${aws_db_instance.main.endpoint}/${aws_db_instance.main.db_name}"
  sensitive   = true
}
# Application URL
output "application_url" {
  description = "URL to access the application"
  value       = "http://${aws_lb.main.dns_name}"
}