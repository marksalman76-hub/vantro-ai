# VANTRO AI - TECHNOLOGY STACK DECISIONS

## Frontend

**Framework:** Next.js 14
**Language:** TypeScript
**Styling:** Tailwind CSS
**State Management:** React Context + React Query
**Deployment:** Vercel
**Domain:** vantro.ai

Why Next.js?
- Full-stack React framework
- Built-in API routes
- Automatic code splitting
- Serverless deployment on Vercel
- Excellent DX (Developer Experience)

## Backend

**Framework:** FastAPI
**Language:** Python 3.11
**Async:** Native async/await support
**ORM:** SQLAlchemy
**Migrations:** Alembic
**Deployment:** Docker → ECR → ECS Fargate

Why FastAPI?
- Modern, fast Python framework
- Built-in API documentation (Swagger)
- Async support out of the box
- Type hints for validation
- Easy to test

## Database

**Engine:** PostgreSQL 18
**Hosting:** AWS RDS
**Backup:** Automated daily
**Replication:** Multi-AZ for HA
**Connection Pooling:** SQLAlchemy with psycopg2

Why PostgreSQL?
- Open source, reliable
- ACID compliance
- Excellent for relational data
- Good performance
- RDS provides managed service

## Infrastructure

**Cloud Provider:** AWS
**Region:** ap-southeast-2 (Sydney)
**VPC:** Custom VPC (10.0.0.0/16)
**Container Orchestration:** ECS Fargate
**Load Balancer:** AWS ALB
**DNS:** Route53 + Namecheap
**CDN:** Vercel Edge Network + CloudFront
**Container Registry:** AWS ECR

Why AWS?
- Reliable, scalable
- RDS managed database
- ECS Fargate (pay-per-use containers)
- CloudWatch monitoring
- Auto-scaling capabilities

## Authentication

**Method:** JWT (JSON Web Tokens)
**Token Duration:** 24 hours
**Hashing:** bcrypt with salt
**Storage:** localStorage (frontend)
**Transmission:** Authorization header

Why JWT?
- Stateless (scalable)
- Standard across industry
- Self-contained claims
- Works with distributed systems

## Payments

**Provider:** Stripe
**Implementation:** Webhooks for events
**Testing:** Stripe test mode
**Security:** Webhook signature verification

Why Stripe?
- Industry standard
- Secure, PCI compliant
- Webhook support
- Multiple payment methods
- Excellent documentation

## Monitoring & Logging

**Logs:** CloudWatch Logs
**Metrics:** CloudWatch Metrics
**Tracing:** CloudWatch X-Ray (optional)
**Alarms:** CloudWatch Alarms
**Dashboards:** CloudWatch Dashboards

Why CloudWatch?
- AWS-native integration
- Cost-effective
- Real-time monitoring
- Integrated with other AWS services

## CI/CD

**Repository:** GitHub
**CI/CD:** GitHub Actions (future)
**Process:**
  1. Push to GitHub
  2. Run tests
  3. Build Docker image
  4. Push to ECR
  5. Update ECS service
  6. Deploy new tasks

## Testing

**Backend:** pytest
**Frontend:** Jest + React Testing Library
**E2E:** Playwright
**Coverage Target:** 80% backend, 70% frontend

## Version Control

**Repository:** GitHub
**Repository:** https://github.com/marksalman76-hub/vantro-ai
**Branching:** main (production), develop (staging)
**Commit Convention:** Conventional Commits

## Development Tools

**Backend:**
- VSCode or PyCharm
- Python 3.11
- pip (package manager)
- Docker Desktop

**Frontend:**
- VSCode
- Node.js 20+
- npm
- Browser DevTools

## Decision Log

| # | Decision | Rationale | Status |
|----|----------|-----------|--------|
| 1 | Next.js + FastAPI | Modern, scalable, good DX | ✅ APPROVED |
| 2 | PostgreSQL on RDS | Reliable, managed, ACID | ✅ APPROVED |
| 3 | AWS ECS Fargate | Serverless containers, cost | ✅ APPROVED |
| 4 | JWT auth | Stateless, scalable | ✅ APPROVED |
| 5 | Stripe webhooks | Standard, secure | ✅ APPROVED |
| 6 | CloudWatch monitoring | AWS-native, integrated | ✅ APPROVED |

Last Updated: 2026-06-21 10:48:09
Status: APPROVED - Ready for implementation
