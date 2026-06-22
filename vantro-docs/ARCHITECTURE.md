# VANTRO AI - SYSTEM ARCHITECTURE

## Overview
Vantro AI is a multi-tier SaaS platform:
- Frontend: Next.js on Vercel (https://vantro.ai)
- Backend: FastAPI on ECS Fargate
- Database: PostgreSQL on RDS
- API Gateway: AWS ALB
- Monitoring: CloudWatch

## VPC Structure
- VPC: 10.0.0.0/16 (ap-southeast-2)
- Public Subnets: 10.0.1.0/24, 10.0.2.0/24 (ALB)
- Private Subnets (ECS): 10.0.10.0/24, 10.0.11.0/24
- Private Subnets (RDS): 10.0.20.0/24, 10.0.21.0/24

## Security Groups
- ALB SG: Allow 80, 443 from 0.0.0.0/0
- ECS SG: Allow 8000 from ALB SG
- RDS SG: Allow 5432 from ECS SG

## Data Flow
User → Vercel (HTTPS) → ALB → ECS Tasks → RDS

## Deployment
- Frontend: Vercel (auto-deploy on git push)
- Backend: ECR → ECS (container orchestration)
- Database: RDS Multi-AZ with automated backups

## Monitoring
- CloudWatch Logs: /ecs/trance-formation-backend
- CloudWatch Metrics: CPU, memory, request count
- Alarms: High CPU, high memory, high error rate

## Scalability
- ECS: Auto-scaling (1-4 tasks)
- RDS: Read replicas (if needed)
- CDN: Vercel Edge Network

## Disaster Recovery
- RDS Multi-AZ failover: ~2 minutes
- Database backups: Daily, 30-day retention
- ECS task restart: Automatic on failure

Last Updated: 2026-06-21 10:47:01
