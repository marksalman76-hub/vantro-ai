# Vantro.ai CloudWatch Monitoring Dashboards

Region: `us-east-1` | ECS Cluster: `vantro-cluster` | RDS: `vantro-db` | SQS: `vantro-agent-jobs` | ALB: `vantro-alb`

---

## 1. Deploy the Main Dashboard

```bash
aws cloudwatch put-dashboard \
  --region us-east-1 \
  --dashboard-name "Vantro-Operations" \
  --dashboard-body '{
  "widgets": [
    {
      "type": "metric",
      "x": 0,
      "y": 0,
      "width": 12,
      "height": 6,
      "properties": {
        "title": "Agent Job Completion Rate (last 1h)",
        "view": "timeSeries",
        "stacked": false,
        "metrics": [
          [
            {
              "expression": "completed / total * 100",
              "label": "Completion Rate %",
              "id": "completion_rate",
              "color": "#2ca02c"
            }
          ],
          [
            "Vantro/Jobs",
            "CompletedJobs",
            {
              "id": "completed",
              "visible": false,
              "stat": "Sum",
              "period": 3600
            }
          ],
          [
            "Vantro/Jobs",
            "TotalJobs",
            {
              "id": "total",
              "visible": false,
              "stat": "Sum",
              "period": 3600
            }
          ]
        ],
        "period": 3600,
        "region": "us-east-1",
        "yAxis": {
          "left": {
            "min": 0,
            "max": 100,
            "label": "Completion %"
          }
        },
        "annotations": {
          "horizontal": [
            {
              "label": "SLA floor",
              "value": 95,
              "color": "#d62728"
            }
          ]
        }
      }
    },
    {
      "type": "metric",
      "x": 12,
      "y": 0,
      "width": 12,
      "height": 6,
      "properties": {
        "title": "Job Status Breakdown (last 1h)",
        "view": "timeSeries",
        "stacked": true,
        "metrics": [
          ["Vantro/Jobs", "CompletedJobs",            { "stat": "Sum", "period": 300, "color": "#2ca02c", "label": "Completed" }],
          ["Vantro/Jobs", "FailedJobs",               { "stat": "Sum", "period": 300, "color": "#d62728", "label": "Failed" }],
          ["Vantro/Jobs", "PendingJobs",              { "stat": "Sum", "period": 300, "color": "#aec7e8", "label": "Pending" }],
          ["Vantro/Jobs", "ProcessingJobs",           { "stat": "Sum", "period": 300, "color": "#ffbb78", "label": "Processing" }],
          ["Vantro/Jobs", "PendingFinancialReview",   { "stat": "Sum", "period": 300, "color": "#ff7f0e", "label": "Pending Financial Review" }],
          ["Vantro/Jobs", "PendingApproval",          { "stat": "Sum", "period": 300, "color": "#9467bd", "label": "Pending Approval (HITL-3)" }]
        ],
        "period": 300,
        "region": "us-east-1"
      }
    },
    {
      "type": "log",
      "x": 0,
      "y": 6,
      "width": 24,
      "height": 6,
      "properties": {
        "title": "Average Job Execution Time per agent_id (last 1h)",
        "query": "SOURCE '/vantro/backend' | fields @timestamp, agent_id, execution_time_ms\n| filter ispresent(execution_time_ms) and ispresent(agent_id)\n| stats avg(execution_time_ms) as avg_ms,\n         p50(execution_time_ms) as p50_ms,\n         p95(execution_time_ms) as p95_ms,\n         count(*) as job_count\n  by agent_id\n| sort avg_ms desc",
        "region": "us-east-1",
        "view": "table"
      }
    },
    {
      "type": "metric",
      "x": 0,
      "y": 12,
      "width": 8,
      "height": 6,
      "properties": {
        "title": "Credit Deduction Rate (per hour)",
        "view": "timeSeries",
        "stacked": false,
        "metrics": [
          ["Vantro/Credits", "CreditsDeducted", { "stat": "Sum", "period": 3600, "color": "#1f77b4", "label": "Credits Used / hr" }]
        ],
        "period": 3600,
        "region": "us-east-1",
        "yAxis": {
          "left": { "label": "Credits", "min": 0 }
        }
      }
    },
    {
      "type": "metric",
      "x": 8,
      "y": 12,
      "width": 8,
      "height": 6,
      "properties": {
        "title": "HITL-3 Queue Depth (pending_approval)",
        "view": "timeSeries",
        "stacked": false,
        "metrics": [
          ["Vantro/Jobs", "PendingApproval", { "stat": "Maximum", "period": 60, "color": "#9467bd", "label": "Jobs awaiting owner approval" }]
        ],
        "period": 60,
        "region": "us-east-1",
        "annotations": {
          "horizontal": [
            {
              "label": "Alert threshold",
              "value": 10,
              "color": "#d62728"
            }
          ]
        }
      }
    },
    {
      "type": "metric",
      "x": 16,
      "y": 12,
      "width": 8,
      "height": 6,
      "properties": {
        "title": "Financial Scanner Triggers per Hour",
        "view": "timeSeries",
        "stacked": false,
        "metrics": [
          ["Vantro/FinancialScanner", "Triggers", { "stat": "Sum", "period": 3600, "color": "#d62728", "label": "Triggers / hr" }]
        ],
        "period": 3600,
        "region": "us-east-1",
        "annotations": {
          "horizontal": [
            {
              "label": "Investigate above",
              "value": 5,
              "color": "#ff7f0e"
            }
          ]
        }
      }
    },
    {
      "type": "log",
      "x": 0,
      "y": 18,
      "width": 12,
      "height": 6,
      "properties": {
        "title": "Active Workspaces (last 24h — at least 1 job)",
        "query": "SOURCE '/vantro/backend' | fields @timestamp, workspace_id\n| filter ispresent(workspace_id) and ispresent(agent_id)\n| stats count(*) as job_count by workspace_id\n| filter job_count >= 1\n| stats count_distinct(workspace_id) as active_workspaces",
        "region": "us-east-1",
        "view": "table"
      }
    },
    {
      "type": "log",
      "x": 12,
      "y": 18,
      "width": 12,
      "height": 6,
      "properties": {
        "title": "Error Rate by Endpoint — /api/agents/{id}/run (last 1h)",
        "query": "SOURCE '/vantro/alb-access-logs' | fields @timestamp, request_url, elb_status_code, target_status_code\n| filter request_url like /\\/api\\/agents\\/.+\\/run/ and (elb_status_code >= 500 or target_status_code >= 500)\n| stats count(*) as error_count by request_url\n| sort error_count desc\n| limit 20",
        "region": "us-east-1",
        "view": "table"
      }
    },
    {
      "type": "metric",
      "x": 0,
      "y": 24,
      "width": 8,
      "height": 6,
      "properties": {
        "title": "ECS — CPU Utilization (vantro-cluster)",
        "view": "timeSeries",
        "stacked": false,
        "metrics": [
          ["AWS/ECS", "CPUUtilization", "ClusterName", "vantro-cluster", { "stat": "Average", "period": 300, "label": "CPU avg %" }],
          ["AWS/ECS", "CPUUtilization", "ClusterName", "vantro-cluster", { "stat": "Maximum", "period": 300, "label": "CPU max %", "color": "#d62728" }]
        ],
        "period": 300,
        "region": "us-east-1",
        "yAxis": { "left": { "min": 0, "max": 100 } }
      }
    },
    {
      "type": "metric",
      "x": 8,
      "y": 24,
      "width": 8,
      "height": 6,
      "properties": {
        "title": "ECS — Memory Utilization (vantro-cluster)",
        "view": "timeSeries",
        "stacked": false,
        "metrics": [
          ["AWS/ECS", "MemoryUtilization", "ClusterName", "vantro-cluster", { "stat": "Average", "period": 300, "label": "Memory avg %" }],
          ["AWS/ECS", "MemoryUtilization", "ClusterName", "vantro-cluster", { "stat": "Maximum", "period": 300, "label": "Memory max %", "color": "#d62728" }]
        ],
        "period": 300,
        "region": "us-east-1",
        "yAxis": { "left": { "min": 0, "max": 100 } }
      }
    },
    {
      "type": "metric",
      "x": 16,
      "y": 24,
      "width": 8,
      "height": 6,
      "properties": {
        "title": "SQS — vantro-agent-jobs Queue Depth",
        "view": "timeSeries",
        "stacked": false,
        "metrics": [
          ["AWS/SQS", "ApproximateNumberOfMessagesVisible",   "QueueName", "vantro-agent-jobs", { "stat": "Maximum", "period": 60, "label": "Messages visible",     "color": "#1f77b4" }],
          ["AWS/SQS", "ApproximateNumberOfMessagesNotVisible","QueueName", "vantro-agent-jobs", { "stat": "Maximum", "period": 60, "label": "Messages in-flight",   "color": "#ff7f0e" }],
          ["AWS/SQS", "NumberOfMessagesSent",                 "QueueName", "vantro-agent-jobs", { "stat": "Sum",     "period": 300,"label": "Messages sent / 5min", "color": "#2ca02c" }]
        ],
        "period": 60,
        "region": "us-east-1"
      }
    },
    {
      "type": "metric",
      "x": 0,
      "y": 30,
      "width": 8,
      "height": 6,
      "properties": {
        "title": "RDS — vantro-db CPU & Connections",
        "view": "timeSeries",
        "stacked": false,
        "metrics": [
          ["AWS/RDS", "CPUUtilization",    "DBInstanceIdentifier", "vantro-db", { "stat": "Average", "period": 300, "label": "RDS CPU %",    "color": "#1f77b4" }],
          ["AWS/RDS", "DatabaseConnections","DBInstanceIdentifier", "vantro-db", { "stat": "Average", "period": 300, "label": "Connections",  "color": "#ff7f0e", "yAxis": "right" }]
        ],
        "period": 300,
        "region": "us-east-1"
      }
    },
    {
      "type": "metric",
      "x": 8,
      "y": 30,
      "width": 8,
      "height": 6,
      "properties": {
        "title": "ALB — Request Count & 5xx Errors",
        "view": "timeSeries",
        "stacked": false,
        "metrics": [
          ["AWS/ApplicationELB", "RequestCount",      "LoadBalancer", "app/vantro-alb/0000000000000000", { "stat": "Sum",     "period": 300, "label": "Requests",   "color": "#1f77b4" }],
          ["AWS/ApplicationELB", "HTTPCode_Target_5XX_Count", "LoadBalancer", "app/vantro-alb/0000000000000000", { "stat": "Sum", "period": 300, "label": "5xx Errors", "color": "#d62728" }]
        ],
        "period": 300,
        "region": "us-east-1"
      }
    },
    {
      "type": "metric",
      "x": 16,
      "y": 30,
      "width": 8,
      "height": 6,
      "properties": {
        "title": "ALB — Target Response Time (p50 / p95 / p99)",
        "view": "timeSeries",
        "stacked": false,
        "metrics": [
          ["AWS/ApplicationELB", "TargetResponseTime", "LoadBalancer", "app/vantro-alb/0000000000000000", { "stat": "p50", "period": 300, "label": "p50", "color": "#2ca02c" }],
          ["AWS/ApplicationELB", "TargetResponseTime", "LoadBalancer", "app/vantro-alb/0000000000000000", { "stat": "p95", "period": 300, "label": "p95", "color": "#ff7f0e" }],
          ["AWS/ApplicationELB", "TargetResponseTime", "LoadBalancer", "app/vantro-alb/0000000000000000", { "stat": "p99", "period": 300, "label": "p99", "color": "#d62728" }]
        ],
        "period": 300,
        "region": "us-east-1",
        "yAxis": { "left": { "label": "seconds", "min": 0 } }
      }
    },
    {
      "type": "metric",
      "x": 0,
      "y": 36,
      "width": 24,
      "height": 3,
      "properties": {
        "title": "Key Metrics — Single-Number View",
        "view": "singleValue",
        "metrics": [
          ["Vantro/Jobs",             "CompletedJobs",           { "stat": "Sum",     "period": 3600, "label": "Jobs Completed (1h)" }],
          ["Vantro/Jobs",             "FailedJobs",              { "stat": "Sum",     "period": 3600, "label": "Jobs Failed (1h)" }],
          ["Vantro/Jobs",             "PendingApproval",         { "stat": "Maximum", "period": 300,  "label": "HITL-3 Queue Depth" }],
          ["Vantro/Jobs",             "PendingFinancialReview",  { "stat": "Maximum", "period": 300,  "label": "Financial Review Queue" }],
          ["Vantro/FinancialScanner", "Triggers",                { "stat": "Sum",     "period": 3600, "label": "Financial Triggers (1h)" }],
          ["Vantro/Credits",          "CreditsDeducted",         { "stat": "Sum",     "period": 86400,"label": "Credits Used (24h)" }]
        ],
        "region": "us-east-1"
      }
    }
  ]
}'
```

> **Note on ALB ARN suffix:** Replace `app/vantro-alb/0000000000000000` with the actual suffix from:
> ```bash
> aws elbv2 describe-load-balancers --names vantro-alb \
>   --query 'LoadBalancers[0].LoadBalancerArn' \
>   --output text --region us-east-1
> ```
> The suffix is the last two path segments of the ARN (e.g., `app/vantro-alb/a1b2c3d4e5f60000`).

---

## 2. Custom Metrics — What Must Be Emitted

The dashboard above references custom metrics that the backend must emit via `boto3` (or `cloudwatch.put_metric_data`). The financial-scanner metric (`Vantro/FinancialScanner/Triggers`) and `Vantro/Jobs/PendingFinancialReview` are stated as already emitted. The following must also be in place:

| Namespace | Metric Name | Unit | Emitted by |
|---|---|---|---|
| `Vantro/Jobs` | `CompletedJobs` | Count | `agent_worker._process_job()` on `completed` |
| `Vantro/Jobs` | `FailedJobs` | Count | `agent_worker._process_job()` on `failed` |
| `Vantro/Jobs` | `TotalJobs` | Count | `agent_worker._process_job()` on pickup |
| `Vantro/Jobs` | `PendingJobs` | Count | Periodic poller (every 60s) — `SELECT COUNT(*) WHERE status='pending'` |
| `Vantro/Jobs` | `ProcessingJobs` | Count | Periodic poller — `SELECT COUNT(*) WHERE status='processing'` |
| `Vantro/Jobs` | `PendingApproval` | Count | Periodic poller — `SELECT COUNT(*) WHERE status='pending_approval'` |
| `Vantro/Jobs` | `PendingFinancialReview` | Count | Already emitted — `Vantro/Jobs/PendingFinancialReview` |
| `Vantro/Credits` | `CreditsDeducted` | Count | `agent_worker._process_job()` after credit deduction — emit `credits_used` value |
| `Vantro/FinancialScanner` | `Triggers` | Count | Already emitted — `scan_for_financial_actions` in `agent_executor.py` |

For `execution_time_ms` and structured `agent_id` / `workspace_id` fields, ensure the backend logs JSON lines to CloudWatch Logs group `/vantro/backend`. Example log structure:

```json
{
  "timestamp": "2026-06-27T12:00:00Z",
  "level": "INFO",
  "event": "job_completed",
  "job_id": "uuid",
  "agent_id": "research_analytics_agent",
  "workspace_id": "uuid",
  "execution_time_ms": 4230,
  "credits_used": 5,
  "status": "completed"
}
```

ALB access logs must be enabled and delivered to an S3 bucket, then forwarded to `/vantro/alb-access-logs` log group via a Lambda or Firehose subscription if you want the Logs Insights queries to work against them.

---

## 3. Average Job Execution Time per agent_id — Logs Insights Widget Detail

The widget at row `y=6` uses a Logs Insights query against `/vantro/backend`. This widget **cannot** use metric math because `agent_id` is a log field, not a metric dimension. The query:

```
SOURCE '/vantro/backend'
| fields @timestamp, agent_id, execution_time_ms
| filter ispresent(execution_time_ms) and ispresent(agent_id)
| stats avg(execution_time_ms) as avg_ms,
         p50(execution_time_ms) as p50_ms,
         p95(execution_time_ms) as p95_ms,
         count(*) as job_count
  by agent_id
| sort avg_ms desc
```

Alternatively, to emit this as a CloudWatch metric with dimension `AgentId`, add to `agent_worker._process_job()`:

```python
import boto3, time

cw = boto3.client("cloudwatch", region_name="us-east-1")

cw.put_metric_data(
    Namespace="Vantro/Jobs",
    MetricData=[
        {
            "MetricName": "ExecutionTimeMs",
            "Dimensions": [{"Name": "AgentId", "Value": agent_id}],
            "Value": execution_time_ms,
            "Unit": "Milliseconds",
        }
    ],
)
```

Once emitted, replace the log widget with a metric widget using `stat: p95` and group by `AgentId` dimension.

---

## 4. CloudWatch Logs Insights Queries — Ad-Hoc Investigation

Run these in the CloudWatch console → Logs Insights, log group `/vantro/backend` (adjust time range as needed).

### Query 1 — Jobs Stuck in Processing > 10 Minutes

```
fields @timestamp, job_id, agent_id, workspace_id, status
| filter status = "processing"
| filter @timestamp < (now() - 600000)
| sort @timestamp asc
```

> Also useful as a direct SQL check against RDS:
> ```sql
> SELECT id, agent_id, workspace_id, created_at, NOW() - created_at AS stuck_for
> FROM agent_jobs
> WHERE status = 'processing'
>   AND created_at < NOW() - INTERVAL '10 minutes'
> ORDER BY created_at ASC;
> ```

### Query 2 — Credit Deductions That Failed

```
fields @timestamp, job_id, agent_id, workspace_id, credits_used, error_message
| filter event = "credit_deduction_failed"
   or (event = "job_completed" and ispresent(credit_error))
| sort @timestamp desc
| limit 50
```

### Query 3 — Financial Scanner Trigger Details

```
fields @timestamp, job_id, agent_id, workspace_id, matched_phrase, raw_snippet
| filter event = "financial_scanner_triggered"
   or event = "financial_action_detected"
| stats count(*) as trigger_count by agent_id, matched_phrase
| sort trigger_count desc
```

### Query 4 — 5xx Errors Grouped by Path

```
SOURCE '/vantro/alb-access-logs'
| fields @timestamp, request_url, elb_status_code, target_status_code,
         target_processing_time, received_bytes
| filter elb_status_code >= 500 or target_status_code >= 500
| parse request_url "* *" as method, path
| stats count(*) as error_count,
         avg(target_processing_time) as avg_response_s
  by path
| sort error_count desc
| limit 30
```

If ALB logs are not in Logs Insights, run the equivalent against the backend structured logs:

```
SOURCE '/vantro/backend'
| fields @timestamp, method, path, status_code, response_time_ms
| filter status_code >= 500
| stats count(*) as error_count by path
| sort error_count desc
| limit 30
```

### Query 5 — Agent Execution Time p50 / p95 / p99 per agent_id

```
fields @timestamp, agent_id, execution_time_ms
| filter ispresent(execution_time_ms) and ispresent(agent_id)
| stats p50(execution_time_ms) as p50_ms,
         p95(execution_time_ms) as p95_ms,
         p99(execution_time_ms) as p99_ms,
         avg(execution_time_ms) as avg_ms,
         count(*) as sample_count
  by agent_id
| sort p95_ms desc
```

---

## 5. Recommended CloudWatch Alarms

Deploy alongside the dashboard:

```bash
# HITL-3 queue depth > 10 for 5 minutes
aws cloudwatch put-metric-alarm \
  --alarm-name "Vantro-HITL3-QueueHigh" \
  --alarm-description "HITL-3 pending_approval queue exceeded 10 jobs" \
  --namespace "Vantro/Jobs" \
  --metric-name "PendingApproval" \
  --statistic Maximum \
  --period 300 \
  --evaluation-periods 1 \
  --threshold 10 \
  --comparison-operator GreaterThanOrEqualToThreshold \
  --alarm-actions arn:aws:sns:us-east-1:ACCOUNT_ID:vantro-alerts \
  --region us-east-1

# Financial scanner spike: > 5 triggers in 1 hour
aws cloudwatch put-metric-alarm \
  --alarm-name "Vantro-FinancialScanner-Spike" \
  --alarm-description "Financial scanner triggered more than 5 times in 1 hour" \
  --namespace "Vantro/FinancialScanner" \
  --metric-name "Triggers" \
  --statistic Sum \
  --period 3600 \
  --evaluation-periods 1 \
  --threshold 5 \
  --comparison-operator GreaterThanOrEqualToThreshold \
  --alarm-actions arn:aws:sns:us-east-1:ACCOUNT_ID:vantro-alerts \
  --region us-east-1

# Job failure rate: > 5 failures in 5 minutes
aws cloudwatch put-metric-alarm \
  --alarm-name "Vantro-JobFailures-High" \
  --alarm-description "More than 5 job failures in 5 minutes" \
  --namespace "Vantro/Jobs" \
  --metric-name "FailedJobs" \
  --statistic Sum \
  --period 300 \
  --evaluation-periods 1 \
  --threshold 5 \
  --comparison-operator GreaterThanOrEqualToThreshold \
  --alarm-actions arn:aws:sns:us-east-1:ACCOUNT_ID:vantro-alerts \
  --region us-east-1

# RDS CPU > 80% for 5 minutes
aws cloudwatch put-metric-alarm \
  --alarm-name "Vantro-RDS-CPUHigh" \
  --alarm-description "vantro-db CPU utilization above 80%" \
  --namespace "AWS/RDS" \
  --metric-name "CPUUtilization" \
  --dimensions Name=DBInstanceIdentifier,Value=vantro-db \
  --statistic Average \
  --period 300 \
  --evaluation-periods 2 \
  --threshold 80 \
  --comparison-operator GreaterThanOrEqualToThreshold \
  --alarm-actions arn:aws:sns:us-east-1:ACCOUNT_ID:vantro-alerts \
  --region us-east-1

# SQS visible messages > 100 (worker not keeping up)
aws cloudwatch put-metric-alarm \
  --alarm-name "Vantro-SQS-Backlog" \
  --alarm-description "Agent job queue backlog exceeds 100 messages" \
  --namespace "AWS/SQS" \
  --metric-name "ApproximateNumberOfMessagesVisible" \
  --dimensions Name=QueueName,Value=vantro-agent-jobs \
  --statistic Maximum \
  --period 300 \
  --evaluation-periods 2 \
  --threshold 100 \
  --comparison-operator GreaterThanOrEqualToThreshold \
  --alarm-actions arn:aws:sns:us-east-1:ACCOUNT_ID:vantro-alerts \
  --region us-east-1
```

Replace `ACCOUNT_ID` with your AWS account ID and ensure the SNS topic `vantro-alerts` exists with email/PagerDuty subscriptions.

---

## 6. Dashboard Access URL

After `put-dashboard` succeeds:

```
https://us-east-1.console.aws.amazon.com/cloudwatch/home?region=us-east-1#dashboards:name=Vantro-Operations
```
