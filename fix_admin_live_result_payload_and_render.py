from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
admin_page = ROOT / "frontend" / "src" / "app" / "admin" / "page.tsx"
api_route = ROOT / "frontend" / "src" / "app" / "api" / "admin-live-execution" / "route.ts"

backup = ROOT / "backups" / f"admin_live_result_payload_render_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
backup.mkdir(parents=True, exist_ok=True)
shutil.copy2(admin_page, backup / "page.tsx")
shutil.copy2(api_route, backup / "route.ts")

api = api_route.read_text(encoding="utf-8")

api = api.replace(
'''  const data = await response.json();

  return NextResponse.json({
    success: response.ok,
    backend_status: response.status,
    data,
  });''',
'''  const data = await response.json();

  const execution = data?.execution || {};
  const adapter = execution?.adapter_result || {};
  const normalised = adapter?.normalised_response || {};
  const safeOutput = normalised?.safe_output || {};

  const normalized_output =
    safeOutput?.text ||
    data?.output?.generated_output ||
    data?.output?.output ||
    data?.output?.content ||
    data?.generated_output ||
    data?.result ||
    data?.message ||
    "";

  return NextResponse.json({
    success: response.ok && data?.success === true,
    backend_status: response.status,
    normalized_output,
    provider_key: adapter?.provider_key || "openai",
    execution_status: execution?.execution_status || data?.execution_status || data?.status || "",
    live_external_call_executed: adapter?.live_external_call_executed === true,
    latency_ms: adapter?.latency_ms || null,
    customer_safe: adapter?.customer_safe === true,
    credential_values_exposed: adapter?.credential_values_exposed === true,
    data,
  });'''
)

api_route.write_text(api, encoding="utf-8")

s = admin_page.read_text(encoding="utf-8")

s = s.replace(
'''        const data = wrapper?.data || wrapper;
        const execution = data?.execution || {};
        const adapter = execution?.adapter_result || {};
        const normalised = adapter?.normalised_response || {};
        const safeOutput = normalised?.safe_output || {};''',
'''        const data = wrapper?.data || wrapper;
        const execution = data?.execution || {};
        const adapter = execution?.adapter_result || {};
        const normalised = adapter?.normalised_response || {};
        const safeOutput = normalised?.safe_output || {};'''
)

s = s.replace(
'''          provider: adapter?.provider_key || "openai",
          live_external_call_executed: adapter?.live_external_call_executed === true,
          latency_ms: adapter?.latency_ms || null,
          credential_values_exposed: adapter?.credential_values_exposed === true,
          customer_safe: adapter?.customer_safe === true,
          output:
            safeOutput?.text ||
            data?.output?.generated_output ||
            data?.output?.output ||
            data?.output?.content ||
            "",''',
'''          provider: wrapper?.provider_key || adapter?.provider_key || "openai",
          live_external_call_executed: wrapper?.live_external_call_executed === true || adapter?.live_external_call_executed === true,
          latency_ms: wrapper?.latency_ms || adapter?.latency_ms || null,
          credential_values_exposed: wrapper?.credential_values_exposed === true || adapter?.credential_values_exposed === true,
          customer_safe: wrapper?.customer_safe === true || adapter?.customer_safe === true,
          output:
            wrapper?.normalized_output ||
            safeOutput?.text ||
            data?.output?.generated_output ||
            data?.output?.output ||
            data?.output?.content ||
            data?.generated_output ||
            data?.result ||
            "",'''
)

s = s.replace(
'''                              <p>{cleanMessage}</p>
                              <div className="executionTimeline">''',
'''                              <div className="liveOutcomeBox">
                                <strong>Live Outcome</strong>
                                <pre>{cleanMessage}</pre>
                              </div>
                              <div className="executionMetaRow">
                                <span>Provider: {item?.provider || "openai"}</span>
                                <span>Live: {item?.live_external_call_executed ? "Yes" : "No"}</span>
                                <span>Latency: {item?.latency_ms ? `${item.latency_ms}ms` : "—"}</span>
                              </div>
                              <div className="executionTimeline">'''
)

if ".liveOutcomeBox" not in s:
    s = s.replace(
'''        .executionTimeline span {''',
'''        .liveOutcomeBox {
          margin-top: 14px;
          padding: 14px;
          border-radius: 16px;
          background: rgba(2, 6, 23, 0.72);
          border: 1px solid rgba(20, 184, 166, 0.25);
        }
        .liveOutcomeBox strong {
          display: block;
          color: #5eead4;
          font-size: 12px;
          text-transform: uppercase;
          letter-spacing: .08em;
          margin-bottom: 8px;
        }
        .liveOutcomeBox pre {
          margin: 0;
          white-space: pre-wrap;
          color: #e5e7eb;
          font-family: inherit;
          font-size: 14px;
          line-height: 1.55;
          max-height: 280px;
          overflow: auto;
        }
        .executionMetaRow {
          display: flex;
          flex-wrap: wrap;
          gap: 8px;
          margin-top: 12px;
        }
        .executionMetaRow span {
          padding: 6px 10px;
          border-radius: 999px;
          background: rgba(15, 23, 42, .86);
          border: 1px solid rgba(148, 163, 184, .22);
          color: #bfdbfe;
          font-size: 12px;
          font-weight: 800;
        }
        .executionTimeline span {'''
    )

admin_page.write_text(s, encoding="utf-8")

print("ADMIN_LIVE_RESULT_PAYLOAD_AND_RENDER_FIXED")
print(f"Backup: {backup}")
print(f"Updated: {admin_page}")
print(f"Updated: {api_route}")