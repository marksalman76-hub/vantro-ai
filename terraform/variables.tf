variable "app_name" {
  description = "Application name"
  type        = string
  default     = "vantro"
}
variable "environment" {
  description = "Environment name"
  type        = string
  default     = "production"
  validation {
    condition     = contains(["development", "staging", "production"], var.environment)
    error_message = "Environment must be development, staging, or production."
  }
}
variable "region" {
  description = "AWS region"
  type        = string
  default     = "ap-southeast-2"
}
variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}
variable "private_subnet_cidrs" {
  description = "CIDR blocks for private subnets"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24"]
}
variable "public_subnet_cidrs" {
  description = "CIDR blocks for public subnets"
  type        = list(string)
  default     = ["10.0.10.0/24", "10.0.11.0/24"]
}
variable "rds_allocated_storage" {
  description = "RDS storage in GB"
  type        = number
  default     = 20
}
variable "rds_instance_class" {
  description = "RDS instance type"
  type        = string
  default     = "db.t3.small"
}
variable "rds_engine_version" {
  description = "PostgreSQL version"
  type        = string
  default     = "15"
}
variable "rds_backup_retention_days" {
  description = "RDS backup retention period (days)"
  type        = number
  default     = 7
}
variable "ecs_task_count" {
  description = "Initial number of ECS tasks"
  type        = number
  default     = 2
}
variable "ecs_task_cpu" {
  description = "ECS task CPU units (256, 512, 1024, 2048, 4096)"
  type        = number
  default     = 512
}
variable "ecs_task_memory" {
  description = "ECS task memory in MB (512-30720)"
  type        = number
  default     = 1024
}
variable "ecs_min_capacity" {
  description = "Minimum ECS task count for auto-scaling"
  type        = number
  default     = 2
}
variable "ecs_max_capacity" {
  description = "Maximum ECS task count for auto-scaling"
  type        = number
  default     = 4
}
variable "sqs_visibility_timeout" {
  description = "SQS message visibility timeout (seconds)"
  type        = number
  default     = 300
}
variable "sqs_message_retention" {
  description = "SQS message retention period (seconds)"
  type        = number
  default     = 1209600
}
variable "container_port" {
  description = "Container port for FastAPI app"
  type        = number
  default     = 8000
}
variable "container_image" {
  description = "Docker image URI for ECS task"
  type        = string
  default     = "python:3.11-slim"
}
variable "container_image_agent_worker" {
  description = "Docker image URI for the agent worker ECS service"
  type        = string
  default     = "python:3.11-slim"
}
variable "container_image_media_worker" {
  description = "Docker image URI for the media/SQS worker ECS service"
  type        = string
  default     = "python:3.11-slim"
}
variable "agent_worker_cpu" {
  description = "Agent worker task CPU units"
  type        = number
  default     = 512
}
variable "agent_worker_memory" {
  description = "Agent worker task memory (MB)"
  type        = number
  default     = 1024
}
variable "agent_worker_min_capacity" {
  description = "Min agent worker tasks"
  type        = number
  default     = 1
}
variable "agent_worker_max_capacity" {
  description = "Max agent worker tasks"
  type        = number
  default     = 4
}
variable "enable_multi_az" {
  description = "Enable Multi-AZ for RDS"
  type        = bool
  default     = true
}

# ── Secrets (pass via terraform.tfvars or TF_VAR_* environment variables) ──────
variable "jwt_secret" {
  description = "JWT signing secret (≥32 chars, random)"
  type        = string
  sensitive   = true
}
variable "stripe_api_key" {
  description = "Stripe publishable-facing API key reference — use stripe_secret_key for server-side operations"
  type        = string
  sensitive   = true
}

variable "stripe_secret_key" {
  description = "Stripe secret key (sk_live_...) — server-side only, never exposed to clients"
  type        = string
  sensitive   = true
}

variable "redis_node_type" {
  description = "ElastiCache Redis node type"
  type        = string
  default     = "cache.t3.micro"
}

variable "redis_num_cache_nodes" {
  description = "Number of ElastiCache Redis nodes (1 for single, 2+ for HA)"
  type        = number
  default     = 1
}
variable "stripe_webhook_secret" {
  description = "Stripe webhook signing secret (whsec_...)"
  type        = string
  sensitive   = true
}
variable "stripe_publishable_key" {
  description = "Stripe publishable key (pk_live_...)"
  type        = string
  sensitive   = true
}
variable "openai_api_key" {
  description = "OpenAI API key"
  type        = string
  sensitive   = true
}
variable "anthropic_api_key" {
  description = "Anthropic API key"
  type        = string
  sensitive   = true
}
variable "admin_email" {
  description = "Admin notification email address"
  type        = string
  default     = "mark.salman76@gmail.com"
}
variable "domain_name" {
  description = "Primary domain name for ACM certificate (e.g. vantro.ai)"
  type        = string
  default     = "vantro.ai"
}