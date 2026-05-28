from pathlib import Path
from datetime import datetime
import shutil

root = Path.cwd()
target = root / "frontend" / "src" / "app" / "admin" / "page.tsx"

backup_dir = root / "backups" / f"premium_admin_execution_renderer_before_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
backup_dir.mkdir(parents=True, exist_ok=True)
shutil.copy2(target, backup_dir / "page.tsx")

s = target.read_text(encoding="utf-8")

old = '''              <div className={runResult ? "output has" : "output"}>
                {!runResult ? (
                  "Agent output will appear here..."
                ) : (
                  <div className="adminResultCard">
                    <strong>{runResult?.status || "Execution result"}</strong>
                    <p>
                      {runResult?.message ||
                        `${runResult?.selected_agent_count || 0} selected agent run(s) processed.`}
                    </p>

                    {Array.isArray(runResult?.results) ? (
                      <div className="resultList">
                        {runResult.results.map((item: any, index: number) => (
                          <div className="resultRow" key={index}>
                            <span>{item?.agent_id || "agent"}</span>
                            <b>{item?.success ? "SUCCESS" : "REVIEW"}</b>
                            <small>{item?.message || item?.status || "Processed"}</small>
                          </div>
                        ))}
                      </div>
                    ) : null}
                  </div>
                )}
              </div>'''

new = '''              <div className={runResult ? "output has premiumExecutionOutput" : "output premiumExecutionOutput"}>
                {!runResult ? (
                  <div className="emptyExecutionState">
                    <strong>Ready to run</strong>
                    <span>Select agents, enter a task, then run a governed owner/admin execution.</span>
                  </div>
                ) : (
                  <div className="adminResultCard premium">
                    <div className="executionHeader">
                      <div>
                        <small>Governed execution</small>
                        <strong>{runResult?.status || "Execution processed"}</strong>
                        <p>{runResult?.selected_agent_count || 0} selected agent run(s) processed through the owner/admin path.</p>
                      </div>
                      <b className={runResult?.success ? "statusPill success" : "statusPill review"}>
                        {runResult?.success ? "COMPLETED" : "NEEDS REVIEW"}
                      </b>
                    </div>

                    {Array.isArray(runResult?.results) ? (
                      <div className="premiumResultGrid">
                        {runResult.results.map((item: any, index: number) => {
                          const cleanStatus = item?.success
                            ? "Completed"
                            : item?.status === "unsupported_execution_action"
                            ? "Prepared for review"
                            : "Needs review";

                          const cleanMessage = item?.success
                            ? "Agent pipeline completed successfully."
                            : item?.message === "Execution response received."
                            ? "The agent returned a governed result and is ready for operator review."
                            : item?.message || "Review the governed result before delivery.";

                          return (
                            <div className={item?.success ? "premiumResultCard success" : "premiumResultCard review"} key={index}>
                              <div className="resultTopline">
                                <span>{String(item?.agent_id || "agent").replaceAll("_", " ")}</span>
                                <b>{cleanStatus}</b>
                              </div>
                              <p>{cleanMessage}</p>
                              <div className="executionTimeline">
                                <span>Received</span>
                                <span>Governed</span>
                                <span>{item?.success ? "Completed" : "Review"}</span>
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    ) : null}
                  </div>
                )}
              </div>'''

if old not in s:
    raise SystemExit("Execution renderer block not found.")

s = s.replace(old, new, 1)

style_anchor = '''        .topRight{margin-left:auto;display:flex;align-items:center;gap:12px}.runtime{display:flex;gap:6px;align-item'''
css = '''        .premiumExecutionOutput{min-height:150px}
        .emptyExecutionState{display:grid;gap:6px;color:#94a3b8}
        .emptyExecutionState strong{color:#EEF2FF;font-size:16px}
        .adminResultCard.premium{display:grid;gap:16px}
        .executionHeader{display:flex;justify-content:space-between;gap:16px;align-items:flex-start;padding:16px;border:1px solid rgba(255,255,255,.08);background:rgba(11,18,38,.74);border-radius:18px}
        .executionHeader small{display:block;color:#8B9CB8;text-transform:uppercase;letter-spacing:.08em;font-size:10px;font-weight:900}
        .executionHeader strong{display:block;color:#EEF2FF;font-size:18px;margin-top:4px}
        .executionHeader p{margin:6px 0 0;color:#AAB7CF;font-size:13px;line-height:1.5}
        .statusPill{border-radius:999px;padding:7px 10px;font-size:10px;font-weight:950;letter-spacing:.06em;white-space:nowrap}
        .statusPill.success{background:rgba(20,184,166,.14);color:#5EEAD4;border:1px solid rgba(20,184,166,.28)}
        .statusPill.review{background:rgba(245,158,11,.14);color:#FCD34D;border:1px solid rgba(245,158,11,.28)}
        .premiumResultGrid{display:grid;gap:12px}
        .premiumResultCard{border-radius:16px;padding:14px;border:1px solid rgba(255,255,255,.08);background:rgba(15,23,42,.76)}
        .premiumResultCard.success{border-color:rgba(20,184,166,.22)}
        .premiumResultCard.review{border-color:rgba(245,158,11,.22)}
        .resultTopline{display:flex;justify-content:space-between;gap:12px;align-items:center}
        .resultTopline span{text-transform:capitalize;color:#EEF2FF;font-weight:900}
        .resultTopline b{font-size:10px;color:#C4B5FD;border:1px solid rgba(196,181,253,.2);border-radius:999px;padding:5px 8px}
        .premiumResultCard p{margin:9px 0 0;color:#AAB7CF;font-size:13px;line-height:1.45}
        .executionTimeline{display:flex;gap:7px;flex-wrap:wrap;margin-top:12px}
        .executionTimeline span{font-size:10px;font-weight:900;color:#8B9CB8;background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.07);border-radius:999px;padding:5px 8px}
'''

if style_anchor not in s:
    raise SystemExit("Style anchor not found.")

s = s.replace(style_anchor, css + style_anchor, 1)

target.write_text(s, encoding="utf-8")

print("PREMIUM_ADMIN_EXECUTION_RENDERER_INSTALLED")
print(f"Backup folder: {backup_dir}")
print(f"Updated: {target}")