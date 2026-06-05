from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
TARGET = ROOT / "frontend/src/lib/providerQueueRetryFailover.ts"
BACKUP = ROOT / "backups" / f"provider_queue_vercel_safe_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
BACKUP.mkdir(parents=True, exist_ok=True)
shutil.copy2(TARGET, BACKUP / TARGET.name)

text = TARGET.read_text(encoding="utf-8")

text = text.replace('import fs from "fs";\nimport path from "path";\n', "")

start = text.index("const STORE_DIR")
end = text.index("function nextRetryAt")

replacement = r'''
const memoryStore: { jobs: Record<string, ProviderQueueJob[]> } =
  (globalThis as any).__providerQueueRetryFailoverStore ||
  ((globalThis as any).__providerQueueRetryFailoverStore = { jobs: {} });

function safeReadStore(): { jobs: Record<string, ProviderQueueJob[]> } {
  return memoryStore;
}

function safeWriteStore(store: { jobs: Record<string, ProviderQueueJob[]> }): void {
  memoryStore.jobs = store.jobs || {};
}

'''

text = text[:start] + replacement + text[end:]

TARGET.write_text(text, encoding="utf-8", newline="\n")

print("PROVIDER_QUEUE_FAILOVER_VERCEL_SAFE_PATCHED")
print(f"Backup: {BACKUP}")