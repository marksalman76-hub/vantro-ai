from pathlib import Path

p = Path("frontend/src/app/admin/live-execution/page.tsx")
s = p.read_text(encoding="utf-8")

old = '''  if (first?.external_action_record_count !== undefined) {
    evidence.push(`External action records: ${first.external_action_record_count}`);
  }'''

new = '''  if (first?.external_action_record_count !== undefined) {
    evidence.push(`External action records: ${first.external_action_record_count}`);
  }

  const records = Array.isArray(first?.external_action_records) ? first.external_action_records : [];
  if (records.length) {
    evidence.push("");
    evidence.push("External Action Proof Records:");
    records.forEach((record: any, index: number) => {
      evidence.push(`Record ${index + 1}:`);
      evidence.push(`  - Action type: ${record?.action_type || record?.type || "not provided"}`);
      evidence.push(`  - Adapter: ${record?.adapter || record?.provider || "not provided"}`);
      evidence.push(`  - Status: ${record?.action_status || record?.status || "not provided"}`);
      evidence.push(`  - Target: ${record?.target_system || record?.integration || record?.destination || "not provided"}`);
      evidence.push(`  - Record ID: ${record?.record_id || record?.id || record?.external_id || "not provided"}`);
      evidence.push(`  - Created at: ${record?.created_at || record?.created_at_ms || record?.timestamp || "not provided"}`);
      evidence.push(`  - Summary: ${record?.summary || record?.result || record?.message || "not provided"}`);
    });
  } else if (first?.external_action_record_count > 0) {
    evidence.push("External action record details were not returned to the UI payload. Backend record-detail passthrough is required for full proof display.");
  }'''

if old not in s:
    raise SystemExit("Could not find external action record count block.")

s = s.replace(old, new)

p.write_text(s, encoding="utf-8")
print("ADMIN_AUTONOMOUS_PROOF_RECORDS_FIXED")