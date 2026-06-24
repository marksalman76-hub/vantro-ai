# CloudWatch Log Group for ECS
resource "aws_cloudwatch_log_group" "ecs" {
  name              = "/ecs/${var.app_name}"
  retention_in_days = 7

  tags = {
    Name = "${var.app_name}-ecs-logs"
  }
}

# ECS Cluster
resource "aws_ecs_cluster" "main" {
  name = "${var.app_name}-cluster"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }

  tags = {
    Name = "${var.app_name}-cluster"
  }
}

# ECS Task Definition
resource "aws_ecs_task_definition" "main" {
  family                   = var.app_name
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.ecs_task_cpu
  memory                   = var.ecs_task_memory
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
  task_role_arn            = aws_iam_role.ecs_task_role.arn

  container_definitions = jsonencode([
    {
      name      = var.app_name
      image     = var.container_image
      essential = true
      portMappings = [
        {
          containerPort = var.container_port
          hostPort      = var.container_port
          protocol      = "tcp"
        }
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.ecs.name
          "awslogs-region"        = var.region
          "awslogs-stream-prefix" = "ecs"
        }
      }

      environment = [
        {
          name  = "ENVIRONMENT"
          value = var.environment
        },
        {
          name  = "DB_HOST"
          value = aws_db_instance.main.endpoint
        },
        {
          name  = "DB_PORT"
          value = "5432"
        },
        {
          name  = "DB_NAME"
          value = aws_db_instance.main.db_name
        },
        {
          name  = "DB_USER"
          value = aws_db_instance.main.username
        },
        {
          name  = "SQS_QUEUE_URL"
          value = aws_sqs_queue.media_jobs.url
        },
        {
          name  = "MEDIA_BUCKET"
          value = aws_s3_bucket.media.id
        },
        {
          name  = "DISABLE_INLINE_WORKER"
          value = "1"
        }
      ]

      secrets = [
        {
          name      = "DB_PASSWORD"
          valueFrom = "${aws_secretsmanager_secret.db_password.arn}:password::"
        },
        {
          name      = "API_KEYS"
          valueFrom = aws_secretsmanager_secret.api_keys.arn
        }
      ]
    }
  ])

  tags = {
    Name = "${var.app_name}-task-definition"
  }
}

# ECS Service
resource "aws_ecs_service" "main" {
  name            = "${var.app_name}-service"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.main.arn
  desired_count   = var.ecs_task_count
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = aws_subnet.private[*].id
    security_groups  = [aws_security_group.ecs_tasks.id]
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.main.arn
    container_name   = var.app_name
    container_port   = var.container_port
  }

  depends_on = [
    aws_lb_listener.https,
    aws_lb_listener.http_redirect,
    aws_iam_role_policy.ecs_task_execution_logs
  ]

  tags = {
    Name = "${var.app_name}-service"
  }
}

# ECS Auto-Scaling
resource "aws_appautoscaling_target" "ecs_target" {
  max_capacity       = var.ecs_max_capacity
  min_capacity       = var.ecs_min_capacity
  resource_id        = "service/${aws_ecs_cluster.main.name}/${aws_ecs_service.main.name}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"

  depends_on = [aws_ecs_service.main]
}

resource "aws_appautoscaling_policy" "ecs_policy_cpu" {
  name               = "${var.app_name}-cpu-autoscaling"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.ecs_target.resource_id
  scalable_dimension = aws_appautoscaling_target.ecs_target.scalable_dimension
  service_namespace  = aws_appautoscaling_target.ecs_target.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageCPUUtilization"
    }
    target_value       = 70.0
    scale_in_cooldown  = 300
    scale_out_cooldown = 60
  }
}

resource "aws_appautoscaling_policy" "ecs_policy_memory" {
  name               = "${var.app_name}-memory-autoscaling"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.ecs_target.resource_id
  scalable_dimension = aws_appautoscaling_target.ecs_target.scalable_dimension
  service_namespace  = aws_appautoscaling_target.ecs_target.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageMemoryUtilization"
    }
    target_value       = 80.0
    scale_in_cooldown  = 300
    scale_out_cooldown = 60
  }
}

# ── Agent Worker — dedicated ECS service for AI agent job processing ──────────

resource "aws_cloudwatch_log_group" "agent_worker" {
  name              = "/ecs/${var.app_name}-agent-worker"
  retention_in_days = 7

  tags = { Name = "${var.app_name}-agent-worker-logs" }
}

resource "aws_ecs_task_definition" "agent_worker" {
  family                   = "${var.app_name}-agent-worker"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.agent_worker_cpu
  memory                   = var.agent_worker_memory
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
  task_role_arn            = aws_iam_role.ecs_task_role.arn

  container_definitions = jsonencode([
    {
      name      = "${var.app_name}-agent-worker"
      image     = var.container_image_agent_worker
      essential = true

      # No inbound ports — worker polls DB and calls LLM APIs outbound only
      portMappings = []

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.agent_worker.name
          "awslogs-region"        = var.region
          "awslogs-stream-prefix" = "agent-worker"
        }
      }

      environment = [
        { name = "ENVIRONMENT",        value = var.environment },
        { name = "DISABLE_INLINE_WORKER", value = "1" },
        { name = "DB_HOST",            value = aws_db_instance.main.endpoint },
        { name = "DB_PORT",            value = "5432" },
        { name = "DB_NAME",            value = aws_db_instance.main.db_name },
        { name = "DB_USER",            value = aws_db_instance.main.username },
        { name = "SQS_QUEUE_URL",      value = aws_sqs_queue.media_jobs.url },
        { name = "MEDIA_BUCKET",       value = aws_s3_bucket.media.id }
      ]

      secrets = [
        {
          name      = "DB_PASSWORD"
          valueFrom = "${aws_secretsmanager_secret.db_password.arn}:password::"
        },
        {
          name      = "API_KEYS"
          valueFrom = aws_secretsmanager_secret.api_keys.arn
        }
      ]

      healthCheck = {
        command     = ["CMD", "python3", "-c", "import sys; sys.exit(0)"]
        interval    = 60
        timeout     = 10
        retries     = 2
        startPeriod = 30
      }
    }
  ])

  tags = { Name = "${var.app_name}-agent-worker-task" }
}

resource "aws_ecs_service" "agent_worker" {
  name            = "${var.app_name}-agent-worker"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.agent_worker.arn
  desired_count   = var.agent_worker_min_capacity
  launch_type     = "FARGATE"

  # No load balancer — worker has no inbound HTTP
  network_configuration {
    subnets          = aws_subnet.private[*].id
    security_groups  = [aws_security_group.ecs_tasks.id]
    assign_public_ip = false
  }

  # Restart policy: ECS restarts the task automatically on crash
  deployment_minimum_healthy_percent = 0
  deployment_maximum_percent         = 200

  depends_on = [aws_iam_role_policy.ecs_task_execution_logs]

  tags = { Name = "${var.app_name}-agent-worker-service" }
}

# Auto-scaling for agent worker — scale on pending job queue depth
resource "aws_appautoscaling_target" "agent_worker" {
  max_capacity       = var.agent_worker_max_capacity
  min_capacity       = var.agent_worker_min_capacity
  resource_id        = "service/${aws_ecs_cluster.main.name}/${aws_ecs_service.agent_worker.name}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"

  depends_on = [aws_ecs_service.agent_worker]
}

resource "aws_appautoscaling_policy" "agent_worker_cpu" {
  name               = "${var.app_name}-agent-worker-cpu"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.agent_worker.resource_id
  scalable_dimension = aws_appautoscaling_target.agent_worker.scalable_dimension
  service_namespace  = aws_appautoscaling_target.agent_worker.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageCPUUtilization"
    }
    target_value       = 65.0
    scale_in_cooldown  = 600  # slow scale-in — avoid killing mid-job workers
    scale_out_cooldown = 60
  }
}

# CloudWatch alarm: alert when agent worker task count drops to 0
resource "aws_cloudwatch_metric_alarm" "agent_worker_down" {
  alarm_name          = "${var.app_name}-agent-worker-down"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "RunningTaskCount"
  namespace           = "ECS/ContainerInsights"
  period              = "60"
  statistic           = "Minimum"
  threshold           = "1"
  alarm_description   = "Agent worker has no running tasks — AI jobs will queue indefinitely"
  treat_missing_data  = "breaching"
  alarm_actions       = [aws_sns_topic.alerts.arn]

  dimensions = {
    ClusterName = aws_ecs_cluster.main.name
    ServiceName = aws_ecs_service.agent_worker.name
  }
}

# ── Media Worker — SQS consumer for video/HeyGen jobs ─────────────────────────

resource "aws_cloudwatch_log_group" "media_worker" {
  name              = "/ecs/${var.app_name}-media-worker"
  retention_in_days = 7

  tags = { Name = "${var.app_name}-media-worker-logs" }
}

resource "aws_ecs_task_definition" "media_worker" {
  family                   = "${var.app_name}-media-worker"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.agent_worker_cpu
  memory                   = var.agent_worker_memory
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
  task_role_arn            = aws_iam_role.ecs_task_role.arn

  container_definitions = jsonencode([
    {
      name      = "${var.app_name}-media-worker"
      image     = var.container_image_media_worker
      essential = true
      portMappings = []

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.media_worker.name
          "awslogs-region"        = var.region
          "awslogs-stream-prefix" = "media-worker"
        }
      }

      environment = [
        { name = "ENVIRONMENT",  value = var.environment },
        { name = "DB_HOST",      value = aws_db_instance.main.endpoint },
        { name = "DB_PORT",      value = "5432" },
        { name = "DB_NAME",      value = aws_db_instance.main.db_name },
        { name = "DB_USER",      value = aws_db_instance.main.username },
        { name = "SQS_QUEUE_URL", value = aws_sqs_queue.media_jobs.url },
        { name = "MEDIA_BUCKET", value = aws_s3_bucket.media.id }
      ]

      secrets = [
        {
          name      = "DB_PASSWORD"
          valueFrom = "${aws_secretsmanager_secret.db_password.arn}:password::"
        },
        {
          name      = "API_KEYS"
          valueFrom = aws_secretsmanager_secret.api_keys.arn
        }
      ]

      healthCheck = {
        command     = ["CMD", "python3", "-c", "import sys; sys.exit(0)"]
        interval    = 60
        timeout     = 10
        retries     = 2
        startPeriod = 30
      }
    }
  ])

  tags = { Name = "${var.app_name}-media-worker-task" }
}

resource "aws_ecs_service" "media_worker" {
  name            = "${var.app_name}-media-worker"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.media_worker.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = aws_subnet.private[*].id
    security_groups  = [aws_security_group.ecs_tasks.id]
    assign_public_ip = false
  }

  deployment_minimum_healthy_percent = 0
  deployment_maximum_percent         = 200

  depends_on = [aws_iam_role_policy.ecs_task_execution_logs]

  tags = { Name = "${var.app_name}-media-worker-service" }
}

# Scale media worker on SQS queue depth
resource "aws_appautoscaling_target" "media_worker" {
  max_capacity       = 4
  min_capacity       = 1
  resource_id        = "service/${aws_ecs_cluster.main.name}/${aws_ecs_service.media_worker.name}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"

  depends_on = [aws_ecs_service.media_worker]
}

resource "aws_appautoscaling_policy" "media_worker_sqs" {
  name               = "${var.app_name}-media-worker-sqs"
  policy_type        = "StepScaling"
  resource_id        = aws_appautoscaling_target.media_worker.resource_id
  scalable_dimension = aws_appautoscaling_target.media_worker.scalable_dimension
  service_namespace  = aws_appautoscaling_target.media_worker.service_namespace

  step_scaling_policy_configuration {
    adjustment_type         = "ChangeInCapacity"
    cooldown                = 120
    metric_aggregation_type = "Maximum"

    step_adjustment {
      metric_interval_lower_bound = 0
      metric_interval_upper_bound = 10
      scaling_adjustment          = 1
    }
    step_adjustment {
      metric_interval_lower_bound = 10
      scaling_adjustment          = 2
    }
  }
}

resource "aws_cloudwatch_metric_alarm" "sqs_scale_out" {
  alarm_name          = "${var.app_name}-sqs-queue-depth"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "ApproximateNumberOfMessagesVisible"
  namespace           = "AWS/SQS"
  period              = "60"
  statistic           = "Maximum"
  threshold           = "5"
  alarm_description   = "Scale out media worker when SQS queue depth > 5"
  alarm_actions       = [aws_appautoscaling_policy.media_worker_sqs.arn]

  dimensions = {
    QueueName = aws_sqs_queue.media_jobs.name
  }
}

# ── CloudWatch Alarm for ECS Service CPU ──────────────────────────────────────
resource "aws_cloudwatch_metric_alarm" "ecs_cpu" {
  alarm_name          = "${var.app_name}-ecs-high-cpu"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/ECS"
  period              = "300"
  statistic           = "Average"
  threshold           = "90"
  alarm_description   = "Alert when ECS service CPU exceeds 90%"
  treat_missing_data  = "notBreaching"

  dimensions = {
    ClusterName = aws_ecs_cluster.main.name
    ServiceName = aws_ecs_service.main.name
  }
}