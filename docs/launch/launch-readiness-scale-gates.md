# Launch Readiness Scale Gates

Date added: 2026-06-30  
Status: Required before final public launch  

## Purpose

This file is the standing reminder requested by the owner after the AWS/Vercel/GitHub/Docker sync and initial ECS autoscaling work.

Vantro is now better prepared for scale, but it must not be called fully launch-ready for high-volume public traffic until these gates are completed and verified.

## Required Before Final Launch

1. Queue-depth autoscaling.
2. DB pool sizing.
3. RDS capacity increase.
4. Provider rate-limit contracts.
5. Load testing.

## Current Baseline

As of 2026-06-30:

- API ECS autoscaling target: min `2`, max `20`.
- Worker ECS autoscaling target: min `2`, max `50`.
- Worker CPU target tracking: `60%`.
- API CPU target tracking: `70%`.
- Worker job claiming is atomic, so multiple worker tasks should not duplicate the same job.

## Why This Gate Exists

Autoscaling task count is only one part of scale readiness.

True launch readiness also requires:

- SQS or durable queue depth to drive worker scaling, not CPU alone.
- Database connection pools sized for total API workers plus background workers.
- RDS instance/storage/IOPS capacity sized for burst traffic and concurrent job writes.
- Provider-side rate limits and commercial allowances confirmed for Higgsfield, Nano Banana, OpenAI, Anthropic, Stripe, and any other live provider.
- Load tests proving the platform can accept, queue, execute, retry, and observe realistic launch traffic.

## Launch Rule

Do not mark Vantro final-public-launch ready until these scale gates have been completed, tested, and documented.
