from pathlib import Path

checks = {
    "frontend/src/lib/providerQueueRetryFailover.ts": [
        "createProviderQueueJob",
        "persistProviderQueueJob",
        "getProviderQueueJobs",
        "getLatestProviderQueueJob",
        "attachProviderQueueRetryFailover",
        "provider-queue.json",
        "retry_scheduled",
        "failover_selected",
        "manual_review_required",
        "live_external_call_executed: false",
        "external_action_performed: false",
    ],
    "frontend/src/app/api/provider-queue-retry-failover/route.ts": [
        "provider_queue_retry_failover_enabled",
        "persistProviderQueueJob",
        "getProviderQueueJobs",
        "provider_failover_available",
    ],
    "frontend/src/app/api/delegated-workforce-execution/route.ts": [
        "attachProviderQueueRetryFailover",
        "providerQueueRetryFailover",
    ],
    "frontend/src/app/api/real-media-generation-providers/route.ts": [
        "provider_queue_retry_failover_enabled",
    ],
    "frontend/src/app/api/admin-real-media-generation-providers/route.ts": [
        "provider_queue_retry_failover_enabled",
    ],
}

missing = {}

for file, needles in checks.items():
    text = Path(file).read_text(encoding="utf-8")
    absent = [needle for needle in needles if needle not in text]
    if absent:
        missing[file] = absent

if missing:
    raise SystemExit(f"ROW9_PROVIDER_QUEUE_RETRY_FAILOVER_FAILED missing={missing}")

print("ROW9_PROVIDER_QUEUE_RETRY_FAILOVER_PASSED")
