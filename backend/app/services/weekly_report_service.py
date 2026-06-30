"""
Weekly Report Generation Service

Generates client-safe weekly AI workforce reports per workspace.
Each agent section includes:
  - Successes: what was delivered and the impact
  - Failures: what went wrong and why (categorised)
  - Tactic change recommendations: when something isn't working, say so plainly
  - Red flags: things the owner must act on urgently
  - Scaling opportunities: when momentum is building, show where to push harder
  - Blockers, next actions
"""
import logging
import uuid
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy.orm import Session

from app.agents.agent_registry import (
    AGENT_CATALOGUE,
    AGENT_GOVERNANCE,
    agents_for_package,
)

logger = logging.getLogger(__name__)

VALID_RATINGS = {
    "useful", "not_useful", "too_detailed", "not_detailed_enough",
    "wrong_recommendation", "do_more_like_this",
}

# Thresholds
MOMENTUM_COMPLETED_THRESHOLD = 4     # ≥ N completed jobs = momentum building
MOMENTUM_RATE_THRESHOLD      = 0.85  # ≥ 85% success rate = excellent momentum
RED_FLAG_FAILURE_RATE        = 0.5   # ≥ 50% failure rate = red flag
RED_FLAG_MIN_JOBS            = 2     # only flag if there were at least N jobs
TACTIC_CHANGE_RATE           = 0.4   # < 40% success and ≥ 2 attempts = suggest change
SCALE_THRESHOLD_COMPLETED    = 3     # ≥ 3 completed jobs = worth scaling signal


def _tier_from_credits(total: int) -> str:
    if total >= 300:
        return "business"
    if total >= 200:
        return "growth"
    if total >= 60:
        return "starter"
    return "free"


def _quality_label(completion_rate: Optional[float], total_jobs: int) -> tuple[str, str]:
    if total_jobs == 0:
        return "no_activity", "No activity this week"
    if completion_rate is None:
        return "no_activity", "No activity this week"
    if completion_rate >= 0.9:
        return "excellent", "Excellent"
    if completion_rate >= 0.7:
        return "good", "Good"
    if completion_rate >= 0.5:
        return "fair", "Fair"
    return "needs_improvement", "Needs improvement"


def _categorise_failure(error_msg: str) -> str:
    """Map raw error text to a client-friendly failure category."""
    msg = (error_msg or "").lower()
    if any(k in msg for k in ("timeout", "timed out", "deadline")):
        return "Task timed out — the brief may be too broad or the request too complex"
    if any(k in msg for k in ("credit", "balance", "insufficient")):
        return "Insufficient credits to complete the task"
    if any(k in msg for k in ("auth", "token", "permission", "403", "401")):
        return "Access or permission issue prevented completion"
    if any(k in msg for k in ("rate limit", "429", "quota")):
        return "AI provider rate limit reached — will retry automatically next time"
    if any(k in msg for k in ("invalid", "parse", "format", "schema")):
        return "The task brief had a formatting issue the agent could not resolve"
    if any(k in msg for k in ("context", "too long", "length", "token")):
        return "The brief or input was too long — try splitting into smaller tasks"
    if any(k in msg for k in ("reject", "approval")):
        return "Task was rejected during the review step"
    return "Task did not complete — no specific error was recorded"


def _build_successes(completed: list, meta: dict) -> list[dict]:
    """Build client-readable success entries from completed jobs."""
    successes = []
    category = meta.get("category", "")
    name = meta.get("name", "Agent")

    for j in completed[:6]:
        # Build a context-aware label from the category
        if "Marketing" in category:
            label = "Marketing content or campaign task delivered"
        elif "Sales" in category:
            label = "Sales workflow or outreach task completed"
        elif "Research" in category:
            label = "Research and analysis task delivered"
        elif "Support" in category:
            label = "Customer support workflow completed"
        elif "Operations" in category:
            label = "Operational process task executed"
        elif "Media" in category or "Video" in category:
            label = "Media or creative asset produced"
        elif "Strategy" in category:
            label = "Strategic analysis or planning task delivered"
        elif "Finance" in category:
            label = "Financial analysis or reporting task completed"
        else:
            label = f"Task completed by {name}"

        successes.append({
            "job_id": j.id,
            "label": label,
            "credits_used": j.credits_used or 0,
        })
    return successes


def _build_failures(failed: list) -> list[dict]:
    """Build client-readable failure entries from failed/rejected jobs."""
    return [
        {
            "job_id": j.id,
            "category": _categorise_failure(j.error_message or ""),
            "raw_hint": (j.error_message or "No details recorded")[:120],
        }
        for j in failed[:5]
    ]


def _build_red_flags(
    agent_id: str,
    meta: dict,
    completed: list,
    failed: list,
    pending: list,
    remaining_credits: int,
    completion_rate: Optional[float],
) -> list[dict]:
    """Return urgent warnings the owner must act on."""
    flags = []
    name = meta.get("name", "Agent")
    total_attempted = len(completed) + len(failed)

    if remaining_credits < 5:
        flags.append({
            "severity": "critical",
            "flag": "Credit balance is critically low",
            "detail": f"Only {remaining_credits} credit(s) remaining. This agent will stop working if you run out.",
            "action": "Top up credits immediately from the Billing page.",
        })
    elif remaining_credits < 15:
        flags.append({
            "severity": "warning",
            "flag": "Credit balance is getting low",
            "detail": f"{remaining_credits} credits remaining. At current usage you may run out before next week's report.",
            "action": "Check your usage in Billing and consider topping up.",
        })

    if total_attempted >= RED_FLAG_MIN_JOBS and completion_rate is not None and completion_rate >= RED_FLAG_FAILURE_RATE and len(failed) > len(completed):
        flags.append({
            "severity": "critical",
            "flag": f"{name} is failing more often than it's succeeding",
            "detail": f"{len(failed)} of {total_attempted} tasks failed this week ({round((1 - completion_rate) * 100)}% failure rate). This is above the acceptable threshold.",
            "action": "Review the failure details below and consider changing your task briefs, or contact support if failures are technical.",
        })

    if len(pending) >= 3:
        flags.append({
            "severity": "warning",
            "flag": f"{len(pending)} tasks are stuck in approval or processing",
            "detail": "Tasks waiting too long for approval slow down your entire pipeline.",
            "action": "Review and approve or reject pending tasks in the Approvals section.",
        })

    if total_attempted == 0 and remaining_credits < 20:
        flags.append({
            "severity": "info",
            "flag": f"{name} was idle this week with a low credit balance",
            "detail": "No tasks were submitted and your credit balance is low, which could indicate the agent isn't being used.",
            "action": "Submit a task this week, or upgrade your plan to unlock more agents.",
        })

    return flags


# All financial figures in reports are SUGGESTIONS only.
# No agent can commit, allocate, or authorise any of these.
_SUGGESTION_DISCLAIMER = "This is a suggestion for your consideration — no action will be taken without your approval."


def _build_scaling_opportunities(
    agent_id: str,
    meta: dict,
    gov: dict,
    completed: list,
    failed: list,
    completion_rate: Optional[float],
    credits_used: int,
) -> list[dict]:
    """Return scaling opportunities when the agent is performing well."""
    opportunities = []
    name = meta.get("name", "Agent")
    category = meta.get("category", "")
    total_attempted = len(completed) + len(failed)

    if len(completed) < SCALE_THRESHOLD_COMPLETED or completion_rate is None:
        return []

    if completion_rate >= MOMENTUM_RATE_THRESHOLD and len(completed) >= MOMENTUM_COMPLETED_THRESHOLD:
        opportunities.append({
            "signal": "Strong momentum detected",
            "detail": f"{name} completed {len(completed)} tasks with a {round(completion_rate * 100)}% success rate this week. This agent is performing at its best.",
            "opportunity": _scale_action(category, name, len(completed), gov),
            "requires_approval": True,
            "disclaimer": _SUGGESTION_DISCLAIMER,
        })

    if credits_used >= 30 and completion_rate >= 0.7:
        opportunities.append({
            "signal": "High output volume — consider batching",
            "detail": f"You used {credits_used} credits on {name} this week. Batching related tasks together can make the agent more efficient.",
            "opportunity": "Group similar tasks into a single larger brief to reduce overhead and get more from each credit.",
            "requires_approval": False,
            "disclaimer": None,
        })

    if len(completed) >= 2 and completion_rate == 1.0:
        opportunities.append({
            "signal": "Perfect success rate — ready to expand scope",
            "detail": f"Every task submitted to {name} this week was completed successfully.",
            "opportunity": "Try more ambitious or complex tasks — the agent is ready for it. Consider increasing your weekly task volume.",
            "requires_approval": False,
            "disclaimer": None,
        })

    return opportunities[:3]


def _scale_action(category: str, name: str, completed_count: int, gov: dict) -> str:
    """Return a category-specific scaling action."""
    if "Marketing" in category:
        return f"Double your content output — if {completed_count} tasks delivered results, try twice the volume next week to build pipeline momentum."
    if "Sales" in category:
        return f"Expand outreach targets — your sales agent is converting. Increase the prospect list size or add a second campaign track."
    if "Research" in category:
        return f"Use research outputs as fuel for other agents — feed findings into your Marketing or Strategy agents to multiply the impact."
    if "Support" in category:
        return f"Add proactive customer success workflows — your support agent is handling reactive work well; now use it for proactive outreach."
    if "Operations" in category:
        return f"Automate more workflows — identify the next manual process in your pipeline and hand it off to the operations agent."
    if "Media" in category or "Video" in category:
        return f"Build a content calendar — with consistent media output, plan 4 weeks ahead so the agent always has a queue of approved briefs."
    if "Strategy" in category:
        return f"Schedule monthly strategic reviews — use this agent to produce a formal monthly strategy brief for your team."
    return f"Increase task frequency for {name} — performance is strong and there's clear capacity to do more."


def _build_tactic_changes(
    agent_id: str,
    meta: dict,
    completed: list,
    failed: list,
    completion_rate: Optional[float],
) -> list[dict]:
    """Return recommendations to change tactics when something isn't working."""
    changes = []
    name = meta.get("name", "Agent")
    category = meta.get("category", "")
    total_attempted = len(completed) + len(failed)

    if total_attempted < 2 or completion_rate is None:
        return []

    if completion_rate < TACTIC_CHANGE_RATE:
        # Diagnose failure pattern from error messages
        error_msgs = [f.error_message or "" for f in failed]
        timeout_count  = sum(1 for m in error_msgs if "timeout" in m.lower() or "timed out" in m.lower())
        length_count   = sum(1 for m in error_msgs if "too long" in m.lower() or "length" in m.lower())
        format_count   = sum(1 for m in error_msgs if "format" in m.lower() or "parse" in m.lower() or "invalid" in m.lower())

        if timeout_count >= 1:
            changes.append({
                "tactic": "Split large tasks into smaller steps",
                "reason": f"{name} is timing out on complex requests. Break your brief into 2–3 focused sub-tasks instead of one large request.",
                "example": "Instead of 'Write a full marketing strategy', try 'Write an audience analysis' then 'Write a channel strategy' separately.",
            })
        elif length_count >= 1:
            changes.append({
                "tactic": "Shorten your task briefs",
                "reason": "Some tasks exceeded the agent's input capacity. Briefs over ~2,000 words may not process correctly.",
                "example": "Summarise your input data before passing it to the agent, or use the Research agent first to distil the key points.",
            })
        elif format_count >= 1:
            changes.append({
                "tactic": "Use plain language in your briefs",
                "reason": "Some tasks failed due to formatting issues in the brief. Avoid using special characters, tables, or code blocks in task instructions.",
                "example": "Write task briefs as clear plain-English instructions, not as structured documents or templates.",
            })
        else:
            changes.append({
                "tactic": "Rewrite your brief with more context",
                "reason": f"{name} struggled to complete tasks this week with a {round(completion_rate * 100)}% success rate. The most common fix is adding more background context.",
                "example": "Include: who your target audience is, what outcome you want, and any constraints (tone, length, format).",
            })

    if total_attempted >= 4 and completion_rate is not None and 0.5 <= completion_rate < 0.7 and not changes:
        # Fair performance — suggest a specific improvement
        if "Marketing" in category:
            changes.append({
                "tactic": "Provide a stronger brand brief",
                "reason": f"Your marketing agent is completing tasks but not at full effectiveness ({round(completion_rate * 100)}% success). Richer brand context typically lifts quality significantly.",
                "example": "Update your Brand Profile with your tone of voice, target audience personas, and three examples of content you love.",
            })
        elif "Sales" in category:
            changes.append({
                "tactic": "Add a detailed ICP (ideal customer profile) to your brief",
                "reason": f"Sales task quality improves significantly when the agent knows exactly who it's targeting.",
                "example": "Include company size, industry, job title, and key pain points of your ideal prospect in every sales task brief.",
            })
        elif "Research" in category:
            changes.append({
                "tactic": "Specify the output format you need",
                "reason": "Research agents perform better when given a clear output structure to follow.",
                "example": "End your brief with: 'Format the output as: 1. Summary (3 sentences), 2. Key findings (bullet list), 3. Recommended action.'",
            })

    return changes[:2]


def _build_recommendations(
    agent_id: str,
    meta: dict,
    gov: dict,
    completed: list,
    failed: list,
    remaining_credits: int,
    tactic_changes: list,
    scaling_opportunities: list,
) -> list[str]:
    """High-level strategic recommendations (plain sentences for the overview)."""
    recs = []
    name = meta.get("name", "Agent")
    category = meta.get("category", "")

    if remaining_credits < 10:
        recs.append("Top up credits before this week to avoid interruption to your AI workforce")
    if failed and not tactic_changes:
        recs.append(f"Review the {len(failed)} failed task(s) below and resubmit with clearer briefs")
    if not completed and not failed:
        recs.append(f"Submit your first task to {name} this week — your plan includes this agent at no extra cost")
    if scaling_opportunities:
        recs.append(f"{name} is performing well — consider increasing your task volume to accelerate results")
    if tactic_changes:
        recs.append(f"Adjust your approach for {name}: {tactic_changes[0]['tactic'].lower()}")

    # Category-specific weekly nudge
    if completed and not recs:
        if "Marketing" in category:
            recs.append("Plan next week's content topics now so your marketing agent always has a brief ready")
        elif "Sales" in category:
            recs.append("Review pipeline status and identify the top 5 leads to prioritise this week")
        elif "Research" in category:
            recs.append("Share this week's research outputs with your strategy or marketing team for activation")
        elif "Support" in category:
            recs.append("Audit open support tickets and brief the agent on any recurring themes")
        elif "Operations" in category:
            recs.append("Identify the next manual process in your workflow and hand it off to this agent")
        elif "Media" in category:
            recs.append("Upload approved outputs to your asset library and plan next week's creative brief")
        else:
            recs.append("Book time to review outputs with your team and plan follow-up tasks")

    return recs[:3]


def generate_workspace_report(workspace_id: str, db: Session, period_days: int = 7) -> "WeeklyReport":
    """Generate and persist a weekly report for the given workspace."""
    from app.models.agent_system import AgentJob
    from app.models.workspace import Workspace, CreditsAccount
    from app.models.reports import WeeklyReport

    now = datetime.utcnow()
    period_end = now
    period_start = now - timedelta(days=period_days)

    ws = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not ws:
        raise ValueError(f"Workspace {workspace_id} not found")

    cred = db.query(CreditsAccount).filter(CreditsAccount.workspace_id == workspace_id).first()
    total_credits   = cred.total_credits if cred else 0
    used_credits    = cred.used_credits  if cred else 0
    remaining_credits = total_credits - used_credits
    tier = _tier_from_credits(total_credits)

    # All jobs this period
    jobs = (
        db.query(AgentJob)
        .filter(AgentJob.workspace_id == workspace_id)
        .filter(AgentJob.created_at >= period_start)
        .filter(AgentJob.created_at <= period_end)
        .all()
    )

    purchased_agent_ids = agents_for_package(tier)

    sections = []
    workspace_red_flags = []

    for agent_id in purchased_agent_ids:
        meta = AGENT_CATALOGUE.get(agent_id, {})
        gov  = AGENT_GOVERNANCE.get(agent_id, {})
        agent_jobs = [j for j in jobs if j.agent_id == agent_id]

        completed = [j for j in agent_jobs if j.status == "completed"]
        failed    = [j for j in agent_jobs if j.status in ("failed", "rejected")]
        pending   = [j for j in agent_jobs if j.status in ("pending", "running", "pending_approval")]
        cancelled = [j for j in agent_jobs if j.status == "cancelled"]
        total_done = len(completed) + len(failed)

        credits_used      = sum(j.credits_used or 0 for j in completed)
        completion_rate   = (len(completed) / total_done) if total_done > 0 else None
        quality_score, quality_label = _quality_label(completion_rate, len(agent_jobs))

        # Rich intelligence fields
        successes            = _build_successes(completed, meta)
        failures             = _build_failures(failed)
        red_flags            = _build_red_flags(agent_id, meta, completed, failed, pending, remaining_credits, completion_rate)
        scaling_opportunities= _build_scaling_opportunities(agent_id, meta, gov, completed, failed, completion_rate, credits_used)
        tactic_changes       = _build_tactic_changes(agent_id, meta, completed, failed, completion_rate)
        recommendations      = _build_recommendations(agent_id, meta, gov, completed, failed, remaining_credits, tactic_changes, scaling_opportunities)

        # Collect critical flags for the executive summary
        workspace_red_flags.extend([f for f in red_flags if f["severity"] == "critical"])

        # Legacy blockers field (kept for backwards compat)
        blockers = []
        if remaining_credits < 10:
            blockers.append("Low credit balance may limit upcoming work")
        for rf in red_flags:
            if rf["flag"] not in blockers:
                blockers.append(rf["flag"])

        section = {
            "agent_id":              agent_id,
            "agent_name":            meta.get("name", agent_id),
            "category":              meta.get("category", ""),
            "status":                "active" if agent_jobs else "idle",
            "period_start":          period_start.isoformat(),
            "period_end":            period_end.isoformat(),
            "jobs_completed":        len(completed),
            "jobs_failed":           len(failed),
            "jobs_pending":          len(pending),
            "jobs_cancelled":        len(cancelled),
            "total_jobs":            len(agent_jobs),
            "credits_used":          credits_used,
            "quality_score":         quality_score,
            "quality_label":         quality_label,
            "completion_rate_pct":   round(completion_rate * 100) if completion_rate is not None else None,
            "successes":             successes,
            "failures":              failures,
            "red_flags":             red_flags,
            "scaling_opportunities": scaling_opportunities,
            "tactic_changes":        tactic_changes,
            "recommendations":       recommendations,
            "blockers":              blockers,
        }
        sections.append(section)

    # Executive summary
    all_completed   = len([j for j in jobs if j.status == "completed"])
    all_failed      = len([j for j in jobs if j.status in ("failed", "rejected")])
    all_credits     = sum(j.credits_used or 0 for j in jobs if j.status == "completed")
    active_agents   = len([s for s in sections if s["status"] == "active"])
    scaling_count   = sum(1 for s in sections if s.get("scaling_opportunities"))
    tactic_count    = sum(1 for s in sections if s.get("tactic_changes"))

    exec_parts = [
        f"Your AI workforce completed {all_completed} task{'s' if all_completed != 1 else ''} "
        f"this week across {active_agents} active agent{'s' if active_agents != 1 else ''}, "
        f"using {all_credits} credit{'s' if all_credits != 1 else ''}."
    ]
    if all_failed:
        exec_parts.append(f"{all_failed} task{'s' if all_failed != 1 else ''} encountered issues and need your attention.")
    if workspace_red_flags:
        exec_parts.append(f"There {'are' if len(workspace_red_flags) > 1 else 'is'} {len(workspace_red_flags)} critical issue{'s' if len(workspace_red_flags) > 1 else ''} requiring your immediate action.")
    if scaling_count:
        exec_parts.append(f"{scaling_count} agent{'s are' if scaling_count > 1 else ' is'} building strong momentum — see scaling opportunities below.")
    if tactic_count and not all_failed:
        exec_parts.append(f"Review tactic change recommendations for {tactic_count} agent{'s' if tactic_count > 1 else ''} to improve results next week.")
    if remaining_credits < 10:
        exec_parts.append("Your credit balance is low — top up before next week to keep your AI agents running.")

    executive_summary = " ".join(exec_parts)

    report = WeeklyReport(
        id=str(uuid.uuid4()),
        workspace_id=workspace_id,
        reporting_period_start=period_start,
        reporting_period_end=period_end,
        sections=sections,
        team_sections=[],
        executive_summary=executive_summary,
        status="generated",
        email_recipients=[],
        delivery_status="pending",
        created_at=now,
        updated_at=now,
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    logger.info("Weekly report generated for workspace=%s report=%s sections=%d", workspace_id, report.id, len(sections))
    return report


def send_report_email(report: "WeeklyReport", recipients: list, db: Session) -> bool:
    """Email a weekly report to the given recipients. Returns True on success."""
    from app.services.email_service import _send as _send_email

    if not recipients:
        return False

    sections = report.sections or []
    summary  = report.executive_summary or "Your weekly AI workforce report."

    # Plain text
    lines = [
        "Your weekly AI Agent workforce report",
        "=" * 45,
        "",
        summary,
        "",
    ]
    for s in sections:
        if s.get("total_jobs", 0) == 0:
            continue
        lines.append(f"── {s.get('agent_name', s.get('agent_id'))} ──")
        lines.append(f"Quality: {s.get('quality_label', '—')}  |  Completed: {s.get('jobs_completed', 0)}  |  Failed: {s.get('jobs_failed', 0)}  |  Credits: {s.get('credits_used', 0)}")

        if s.get("successes"):
            lines.append(f"What was delivered ({len(s['successes'])} task{'s' if len(s['successes']) != 1 else ''}):")
            for sv in s["successes"][:3]:
                lines.append(f"  ✓ {sv['label']}")

        if s.get("failures"):
            lines.append("What went wrong:")
            for fv in s["failures"][:3]:
                lines.append(f"  ✗ {fv['category']}")

        if s.get("red_flags"):
            lines.append("RED FLAGS (action required):")
            for rf in s["red_flags"]:
                lines.append(f"  ⚠ {rf['flag']}: {rf['action']}")

        if s.get("scaling_opportunities"):
            lines.append("Scaling opportunities:")
            for so in s["scaling_opportunities"][:2]:
                lines.append(f"  ↑ {so['signal']}: {so['opportunity']}")

        if s.get("tactic_changes"):
            lines.append("Recommended tactic changes:")
            for tc in s["tactic_changes"][:2]:
                lines.append(f"  → {tc['tactic']}: {tc['reason']}")

        if s.get("recommendations"):
            lines.append("This week's recommendations:")
            for r in s["recommendations"]:
                lines.append(f"  • {r}")

        lines.append("")

    lines += ["View your full report and act on these insights in your portal.", "", "Vantro AI — your AI workforce, working for you."]
    plain = "\n".join(lines)

    # HTML email
    quality_colors = {
        "excellent": "#10b981", "good": "#6366f1",
        "fair": "#f59e0b", "needs_improvement": "#ef4444", "no_activity": "#6b7280",
    }

    agent_blocks_html = ""
    for s in sections:
        if s.get("total_jobs", 0) == 0:
            continue
        qc = quality_colors.get(s.get("quality_score", ""), "#6b7280")
        name = s.get("agent_name", s.get("agent_id"))

        # Successes block
        succ_html = ""
        if s.get("successes"):
            items = "".join(f'<li style="color:#d1fae5;font-size:12px;margin-bottom:3px;">✓ {sv["label"]} ({sv["credits_used"]}cr)</li>' for sv in s["successes"][:4])
            succ_html = f'<div style="margin-bottom:12px;"><p style="color:#10b981;font-size:11px;font-weight:700;margin:0 0 6px;text-transform:uppercase;letter-spacing:0.05em">What was delivered</p><ul style="margin:0;padding-left:16px">{items}</ul></div>'

        # Failures block
        fail_html = ""
        if s.get("failures"):
            items = "".join(f'<li style="color:#fca5a5;font-size:12px;margin-bottom:3px;">✗ {fv["category"]}</li>' for fv in s["failures"][:3])
            fail_html = f'<div style="margin-bottom:12px;"><p style="color:#ef4444;font-size:11px;font-weight:700;margin:0 0 6px;text-transform:uppercase;letter-spacing:0.05em">What went wrong</p><ul style="margin:0;padding-left:16px">{items}</ul></div>'

        # Red flags block
        rf_html = ""
        if s.get("red_flags"):
            items = "".join(f'<li style="color:#fef3c7;font-size:12px;margin-bottom:6px;"><strong>{rf["flag"]}</strong><br><span style="color:#d1d5db;">{rf["action"]}</span></li>' for rf in s["red_flags"])
            rf_html = f'<div style="margin-bottom:12px;background:#431407;border:1px solid #dc2626;border-radius:8px;padding:10px 14px;"><p style="color:#fca5a5;font-size:11px;font-weight:700;margin:0 0 6px;text-transform:uppercase;letter-spacing:0.05em">⚠ Red flags — action required</p><ul style="margin:0;padding-left:16px">{items}</ul></div>'

        # Scaling block
        scale_html = ""
        if s.get("scaling_opportunities"):
            items = "".join(f'<li style="color:#c4b5fd;font-size:12px;margin-bottom:6px;"><strong style="color:#a78bfa">{so["signal"]}</strong><br>{so["opportunity"]}</li>' for so in s["scaling_opportunities"][:2])
            scale_html = f'<div style="margin-bottom:12px;background:#1e1b4b;border:1px solid #6d28d9;border-radius:8px;padding:10px 14px;"><p style="color:#a78bfa;font-size:11px;font-weight:700;margin:0 0 6px;text-transform:uppercase;letter-spacing:0.05em">↑ Scaling opportunities</p><ul style="margin:0;padding-left:16px">{items}</ul></div>'

        # Tactic changes block
        tactic_html = ""
        if s.get("tactic_changes"):
            items = "".join(f'<li style="color:#fef9c3;font-size:12px;margin-bottom:6px;"><strong style="color:#fbbf24">{tc["tactic"]}</strong><br>{tc["reason"]}</li>' for tc in s["tactic_changes"][:2])
            tactic_html = f'<div style="margin-bottom:12px;background:#1c1a00;border:1px solid #b45309;border-radius:8px;padding:10px 14px;"><p style="color:#fbbf24;font-size:11px;font-weight:700;margin:0 0 6px;text-transform:uppercase;letter-spacing:0.05em">→ Recommended tactic changes</p><ul style="margin:0;padding-left:16px">{items}</ul></div>'

        # Recommendations
        rec_html = ""
        if s.get("recommendations"):
            items = "".join(f'<li style="color:#d1d5db;font-size:12px;margin-bottom:3px;">{r}</li>' for r in s["recommendations"])
            rec_html = f'<div><p style="color:#f9fafb;font-size:11px;font-weight:700;margin:0 0 6px;text-transform:uppercase;letter-spacing:0.05em">This week</p><ul style="margin:0;padding-left:16px">{items}</ul></div>'

        agent_blocks_html += f"""
        <div style="margin-bottom:28px;padding:20px;background:#1f2937;border-radius:12px;border-left:4px solid {qc};">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;">
            <h3 style="color:#f9fafb;margin:0;font-size:15px;">{name}</h3>
            <span style="color:{qc};font-size:11px;font-weight:700;">{s.get('quality_label','—')}</span>
          </div>
          <div style="display:flex;gap:16px;margin-bottom:16px;padding-bottom:12px;border-bottom:1px solid #374151;">
            <span style="color:#9ca3af;font-size:12px;">✓ {s.get('jobs_completed',0)} done</span>
            <span style="color:#9ca3af;font-size:12px;">✗ {s.get('jobs_failed',0)} failed</span>
            <span style="color:#9ca3af;font-size:12px;">{s.get('credits_used',0)} credits</span>
            {'<span style="color:' + qc + ';font-size:12px;">' + str(s.get('completion_rate_pct','')) + '% success</span>' if s.get('completion_rate_pct') is not None else ''}
          </div>
          {rf_html}{succ_html}{fail_html}{scale_html}{tactic_html}{rec_html}
        </div>"""

    html = f"""
    <html><body style="font-family:-apple-system,sans-serif;background:#111827;color:#f9fafb;max-width:640px;margin:0 auto;padding:40px 20px;">
      <div style="margin-bottom:32px;display:flex;justify-content:space-between;align-items:center;">
        <span style="font-size:20px;font-weight:800;">Vantro<span style="color:#8b5cf6;">.ai</span></span>
        <span style="color:#6b7280;font-size:12px;">Weekly AI Workforce Report</span>
      </div>
      <div style="background:#1f2937;border-radius:16px;padding:24px;margin-bottom:32px;border:1px solid #374151;">
        <h2 style="color:#f9fafb;margin:0 0 12px;font-size:20px;">This week's summary</h2>
        <p style="color:#9ca3af;margin:0;line-height:1.6;">{summary}</p>
      </div>
      {agent_blocks_html}
      <div style="margin-top:32px;padding:20px;background:#1f2937;border-radius:12px;text-align:center;border:1px solid #4c1d95;">
        <p style="color:#c4b5fd;margin:0 0 16px;font-size:14px;">Take action on these insights in your portal</p>
        <a href="https://vantro.ai/dashboard/reports" style="background:linear-gradient(135deg,#7c3aed,#4f46e5);color:#fff;padding:14px 32px;border-radius:10px;text-decoration:none;font-weight:700;font-size:14px;">View full report →</a>
      </div>
      <p style="color:#4b5563;font-size:11px;margin-top:32px;text-align:center;">
        {report.reporting_period_start.strftime('%d %b') if report.reporting_period_start else 'This week'} – {report.reporting_period_end.strftime('%d %b %Y') if report.reporting_period_end else 'today'} · Manage report settings in your portal
      </p>
    </body></html>"""

    sent = 0
    for recipient in recipients:
        try:
            _send_email(recipient, "Your weekly AI workforce report — Vantro", plain, html)
            sent += 1
        except Exception as exc:
            logger.warning("Failed to email report %s to %s: %s", report.id, recipient, exc)

    if sent > 0:
        report.email_sent_at     = datetime.utcnow()
        report.delivery_status   = "sent"
        report.email_recipients  = recipients
        report.status            = "sent"
        db.commit()
        return True
    else:
        report.delivery_status  = "failed"
        report.delivery_error   = "Email delivery failed for all recipients"
        db.commit()
        return False


def get_or_create_report_settings(workspace_id: str, db: Session) -> "WorkspaceReportSettings":
    from app.models.reports import WorkspaceReportSettings
    settings = db.query(WorkspaceReportSettings).filter(
        WorkspaceReportSettings.workspace_id == workspace_id
    ).first()
    if not settings:
        settings = WorkspaceReportSettings(
            id=str(uuid.uuid4()),
            workspace_id=workspace_id,
            created_at=datetime.utcnow(),
        )
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return settings
