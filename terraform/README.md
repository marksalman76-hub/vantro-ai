# Vantro.AI Terraform Infrastructure as Code

Production-ready Terraform configuration for deploying Vantro.AI on AWS in the ap-southeast-2 region.

## Architecture Overview

This configuration deploys a complete, highly-available infrastructure on AWS:

- **VPC**: Multi-AZ networking with public/private subnets, NAT Gateways, and Internet Gateway
- **RDS**: PostgreSQL 15 with Multi-AZ failover, automated backups (7 days retention)
- **ECS**: Fargate containerized application with auto-scaling (2-4 tasks)
- **ALB**: Application Load Balancer for traffic distribution
- **S3**: Media storage and backup buckets with lifecycle policies
- **SQS**: FIFO queue for asynchronous media generation jobs
- **Secrets Manager**: Secure storage for database passwords and API keys
- **IAM**: Least-privilege roles and policies for all services
- **CloudWatch**: Monitoring, logging, and alarms for all components

## Prerequisites

1. **AWS Account** with appropriate permissions
2. **Terraform** >= 1.0 installed
3. **AWS CLI** configured with credentials (`aws configure`)
4. **Docker Image** published to ECR (or use provided default)

Verify setup:
```bash
terraform --version
aws --version
aws sts get-caller-identity
```

## Quick Start

### 1. Clone and Configure

```bash
cd terraform/
cp terraform.tfvars.example terraform.tfvars
```

Edit `terraform.tfvars` with your settings:
```hcl
app_name    = "vantro"
environment = "production"
region      = "ap-southeast-2"
```

### 2. Initialize Terraform

```bash
terraform init
```

### 3. Plan Deployment

```bash
terraform plan -out=tfplan
```

Review the plan carefully — this shows all resources that will be created.

### 4. Apply Configuration

```bash
terraform apply tfplan
```

This will:
- Create the VPC and networking infrastructure
- Provision RDS PostgreSQL database
- Set up S3 buckets with lifecycle policies
- Create SQS queue for async jobs
- Deploy ECS cluster and service with ALB
- Configure auto-scaling and CloudWatch alarms
- Generate random database password (stored in Secrets Manager)

### 5. Get Outputs

After deployment completes, retrieve important endpoints:

```bash
terraform output alb_dns_name
terraform output rds_endpoint
terraform output sqs_queue_url
terraform output media_bucket_name
```

## Configuration

### Variables

All configuration is in `variables.tf`. Key variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `app_name` | vantro | Application name |
| `environment` | production | Environment (development, staging, production) |
| `region` | ap-southeast-2 | AWS region |
| `rds_instance_class` | db.t3.small | RDS instance type |
| `rds_allocated_storage` | 20 | RDS storage (GB) |
| `ecs_task_count` | 2 | Initial ECS task count |
| `ecs_max_capacity` | 4 | Max tasks for auto-scaling |
| `enable_multi_az` | true | Enable Multi-AZ for RDS |

Override in `terraform.tfvars`:
```hcl
rds_instance_class = "db.t3.medium"
ecs_max_capacity   = 6
```

## Deployment Checklist

- [ ] AWS credentials configured
- [ ] Terraform installed and initialized
- [ ] `terraform.tfvars` customized
- [ ] `terraform plan` reviewed
- [ ] Docker image ready (or using default)
- [ ] Sufficient AWS quota for resources
- [ ] Backup/disaster recovery plan in place

## Post-Deployment

### 1. Update Database Password

The initial password is randomly generated. Update it:

```bash
aws secretsmanager get-secret-value \
  --secret-id vantro/db-password \
  --region ap-southeast-2
```

Or update in AWS Secrets Manager console.

### 2. Configure API Keys

Update placeholder API keys in Secrets Manager:

```bash
aws secretsmanager update-secret \
  --secret-id vantro/api-keys \
  --secret-string '{"JWT_SECRET":"...","STRIPE_API_KEY":"..."}' \
  --region ap-southeast-2
```

### 3. Test Application

```bash
ALB_DNS=$(terraform output -raw alb_dns_name)
curl http://$ALB_DNS/health
```

### 4. Configure SSL/TLS (Recommended)

Add HTTPS listener to ALB:
1. Create/import ACM certificate
2. Add HTTPS listener in `alb.tf`
3. Redirect HTTP → HTTPS
4. Re-apply Terraform

## Monitoring

CloudWatch dashboards and alarms are automatically created:

- **ECS**: CPU and memory utilization
- **RDS**: Storage, connections, replication lag
- **ALB**: Unhealthy hosts, response time
- **SQS**: Queue depth, message age

View alarms in AWS Console:
```
CloudWatch → Alarms
```

## Scaling

### ECS Auto-Scaling

Auto-scaling is configured for CPU (70%) and Memory (80%) targets. Adjust in `ecs.tf`:

```hcl
resource "aws_appautoscaling_policy" "ecs_policy_cpu" {
  # ...
  target_value = 70.0  # Adjust threshold
}
```

### RDS Scaling

To upgrade RDS instance type:

```hcl
rds_instance_class = "db.t3.medium"
terraform plan  # Review changes
terraform apply
```

## Backup & Disaster Recovery

- **RDS**: Automated backups (7 days retention)
- **S3**: Versioning enabled, lifecycle policies configured
- **Secrets**: Recovery window of 7 days for deletion

Restore from backup:
```bash
aws rds restore-db-instance-from-db-snapshot \
  --db-instance-identifier vantro-db-restored \
  --db-snapshot-identifier <snapshot-id>
```

## Cleanup

To destroy all resources:

```bash
terraform destroy
```

**WARNING**: This will delete:
- RDS database (final snapshot created)
- S3 buckets and objects
- ECS cluster and services
- VPC and all networking resources

Confirm you want to proceed when prompted.

## Troubleshooting

### State File Issues

If Terraform state becomes corrupted:

```bash
# Backup current state
cp terraform.tfstate terraform.tfstate.backup

# Refresh state
terraform refresh

# Re-plan and apply
terraform plan
terraform apply
```

### AWS Credential Issues

Ensure AWS CLI is configured:
```bash
aws sts get-caller-identity
```

Or use environment variables:
```bash
export AWS_ACCESS_KEY_ID=<your-key>
export AWS_SECRET_ACCESS_KEY=<your-secret>
export AWS_REGION=ap-southeast-2
```

### ECS Service Not Starting

Check task logs:
```bash
aws logs tail /ecs/vantro --follow
```

Check ECS service status:
```bash
aws ecs describe-services \
  --cluster vantro-cluster \
  --services vantro-service
```

## Files Structure

```
terraform/
├── main.tf              # Provider and backend config
├── variables.tf         # Input variables
├── vpc.tf              # VPC, subnets, gateways
├── rds.tf              # PostgreSQL database
├── s3.tf               # S3 buckets
├── sqs.tf              # SQS queue
├── ecs.tf              # ECS cluster and service
├── iam.tf              # IAM roles and policies
├── secrets.tf          # Secrets Manager
├── alb.tf              # Application Load Balancer
├── outputs.tf          # Outputs
├── terraform.tfvars.example  # Example variables
└── .gitignore          # Git ignore rules
```

## Support

For issues or questions:

1. Check Terraform documentation: https://registry.terraform.io/providers/hashicorp/aws
2. Review AWS documentation: https://docs.aws.amazon.com
3. Check CloudWatch logs for service errors
4. Enable Terraform debug logging:
   ```bash
   TF_LOG=DEBUG terraform plan
   ```

## License

Production infrastructure for Vantro.AI. Managed by Engineering team.
