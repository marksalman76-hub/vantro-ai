# Vantro Incident Notification Templates

**Usage:** Replace all `[BRACKETED]` variables before sending. Never include stack traces, internal service names, infrastructure details, or AI provider information in customer communications. All references to systems should use generic customer-facing language only.

**Channels:** Email (use Subject line), Status page (use Title), In-app banner (use Title — truncate to 120 chars if needed).

---

## P0 — Service Down

> Full service unavailable. Begin customer communication within 15 minutes of confirmed outage. Update every 30 minutes until resolved.

---

### P0 — Initial Notice

**Subject:** [URGENT] Vantro Platform Outage — We're On It | Incident [INCIDENT_ID]
**Title:** Platform Outage — Service Unavailable | [INCIDENT_ID]

---

We're writing to let you know that the Vantro platform is currently unavailable. We know how much your team depends on this to keep operations running, and we're treating this as our highest priority.

**What's happening:**
The Vantro platform is currently down. You may be unable to log in, run agent jobs, or access your workspace.

**When it started:** [START_TIME] [TIMEZONE]

**What's affected:** Full platform access, including [AFFECTED_FEATURES].

**What we're doing:**
Our team identified the issue at [DETECTION_TIME] and is working on it right now. Every available engineer is on this.

**What to expect:**
We'll send an update within 30 minutes — sooner if we have news. We'll post all updates at [STATUS_PAGE_URL].

We're sorry for the disruption. We'll keep you informed until this is fully resolved.

— The Vantro Team

---

### P0 — Progress Update

**Subject:** Update [UPDATE_NUMBER]: Vantro Platform Outage | Incident [INCIDENT_ID]
**Title:** Outage Update [UPDATE_NUMBER] — [CURRENT_STATUS_SUMMARY] | [INCIDENT_ID]

---

**Incident update — [UPDATE_TIME] [TIMEZONE]**

Here's where things stand on incident [INCIDENT_ID].

**Current status:** [CURRENT_STATUS — e.g., "Investigation is ongoing", "A fix has been identified and is being deployed", "Recovery is underway"]

**Progress since last update:**
[2–4 sentences describing what the team has done or learned since the previous update. Be specific about progress without revealing internal architecture. Example: "We have identified the root cause and are now deploying a fix. Early signs are positive."]

**Remaining work:**
[1–2 sentences on what still needs to happen before service is restored. Example: "We are completing final validation steps before declaring full recovery."]

**Estimated resolution:** [TIME_ESTIMATE or "We do not yet have a reliable estimate and will update you as soon as we do."]

**Affected features:** [AFFECTED_FEATURES]
**Outage duration so far:** [DURATION]

Next update: [NEXT_UPDATE_TIME] or sooner if the situation changes.

Status page: [STATUS_PAGE_URL]

— The Vantro Team

---

### P0 — Resolution

**Subject:** Resolved: Vantro Platform Outage | Incident [INCIDENT_ID]
**Title:** Resolved — Platform Fully Restored | [INCIDENT_ID]

---

The Vantro platform is fully restored. We want to give you a complete picture of what happened and what we're doing to prevent it from happening again.

**Incident summary**
- **Incident ID:** [INCIDENT_ID]
- **Start time:** [START_TIME] [TIMEZONE]
- **Resolved at:** [RESOLUTION_TIME] [TIMEZONE]
- **Total duration:** [TOTAL_DURATION]
- **Affected features:** [AFFECTED_FEATURES]

**What happened:**
[2–3 sentences describing the issue in plain, customer-facing terms. No internal system names, no stack details. Example: "A failure in a core platform component caused the service to become unreachable. The issue was triggered by an unexpected condition during a routine infrastructure update."]

**What we did to fix it:**
[2–3 sentences on the resolution action, generically described. Example: "We identified the affected component, rolled back the change that introduced the problem, and restored the service. We then ran a full health check before declaring recovery."]

**What we're doing to prevent recurrence:**
We are implementing additional monitoring and automated safeguards to detect and respond to this class of issue faster. We will also be reviewing our change management process to reduce the risk of similar disruptions.

**Credit to your account:**
As an acknowledgment of the impact this caused, we have applied **[CREDIT_AMOUNT] credits** to your workspace. These credits will be visible in your billing dashboard within 24 hours. If you have questions about the credit, contact [SUPPORT_EMAIL].

We understand that downtime affects your business directly, and we hold ourselves to a higher standard. Thank you for your patience while we worked through this.

— The Vantro Team

---

## P1 — Degraded Performance

> Partial impact — some features slow or unavailable. Send initial notice within 1 hour of confirmed impact. Update every 2 hours until resolved.

---

### P1 — Initial Notice

**Subject:** Vantro Platform — Degraded Performance | Incident [INCIDENT_ID]
**Title:** Degraded Performance — Some Features Affected | [INCIDENT_ID]

---

We want to let you know that the Vantro platform is currently experiencing degraded performance. The platform is operational, but some features are not working as expected.

**What's affected:**
[AFFECTED_FEATURES] — [brief description of the user-visible impact, e.g., "Agent jobs may take longer than usual to start or complete. Results may be delayed."]

**What's working normally:**
[UNAFFECTED_FEATURES — e.g., "Your workspace dashboard, settings, and billing are unaffected."]

**When it started:** [START_TIME] [TIMEZONE]

**What we're doing:**
Our team is actively investigating and working toward a fix. We'll keep you updated every 2 hours — or sooner if we have news.

Status page: [STATUS_PAGE_URL]

We apologize for the inconvenience. If you have a time-sensitive need, please contact [SUPPORT_EMAIL] and we'll do our best to help.

— The Vantro Team

---

### P1 — Progress Update

**Subject:** Update [UPDATE_NUMBER]: Degraded Performance | Incident [INCIDENT_ID]
**Title:** Degraded Performance Update [UPDATE_NUMBER] | [INCIDENT_ID]

---

**Incident update — [UPDATE_TIME] [TIMEZONE]**

This is a follow-up on incident [INCIDENT_ID] — degraded performance affecting [AFFECTED_FEATURES].

**Current status:** [CURRENT_STATUS — e.g., "We have identified the cause and are working on a fix", "A fix is being staged for deployment", "Performance is improving but not yet back to normal"]

**What's changed since our last update:**
[2–3 sentences on progress. Be honest about where things stand. If there's nothing new to report, say so: "Our investigation is ongoing. We do not yet have a root cause confirmed, but we have ruled out [generic category] as the source."]

**What you can expect:**
[AFFECTED_FEATURES] [remain affected / are partially restored / should be fully restored by TIME_ESTIMATE].

Next update: [NEXT_UPDATE_TIME]
Status page: [STATUS_PAGE_URL]

— The Vantro Team

---

### P1 — Resolution

**Subject:** Resolved: Degraded Performance | Incident [INCIDENT_ID]
**Title:** Resolved — Performance Restored to Normal | [INCIDENT_ID]

---

The degraded performance affecting [AFFECTED_FEATURES] has been resolved. The Vantro platform is operating normally.

**Incident summary**
- **Incident ID:** [INCIDENT_ID]
- **Start time:** [START_TIME] [TIMEZONE]
- **Resolved at:** [RESOLUTION_TIME] [TIMEZONE]
- **Total duration:** [TOTAL_DURATION]
- **Affected features:** [AFFECTED_FEATURES]

**What happened:**
[2–3 sentences describing the issue in plain language. Example: "Increased load on a core processing component caused agent jobs to queue longer than expected, resulting in delays for some workspaces."]

**How we fixed it:**
[1–2 sentences on resolution. Example: "We scaled up the affected component and applied a configuration change to prevent the queue buildup from recurring under similar conditions."]

**What we're doing to prevent recurrence:**
We have added additional capacity headroom and improved our alerting so that this class of degradation is caught and addressed more quickly in the future.

[IF APPLICABLE:]
**Credit to your account:**
Given the duration and impact of this incident, we have applied **[CREDIT_AMOUNT] credits** to your workspace. They will appear in your billing dashboard within 24 hours.

Thank you for your patience.

— The Vantro Team

---

## P2 — Minor Issue

> Cosmetic or minor functional issue with limited user impact. Send initial notice within 4 hours of confirmation. Update daily until resolved.

---

### P2 — Initial Notice

**Subject:** Vantro Platform — Minor Issue Affecting [AFFECTED_FEATURES] | [INCIDENT_ID]
**Title:** Minor Issue — [ONE_LINE_SUMMARY] | [INCIDENT_ID]

---

We wanted to give you a heads-up about a minor issue currently affecting the Vantro platform.

**What's affected:**
[AFFECTED_FEATURES] — [brief description of user-visible impact, e.g., "Some workspace activity timestamps may display incorrectly in the dashboard. This is a display issue only and does not affect agent job execution or results."]

**What's working normally:**
All core platform features — including agent job execution, results, billing, and workspace management — are unaffected.

**When it started:** [START_TIME] [TIMEZONE]

**What we're doing:**
Our team is aware of the issue and is working on a fix. Given the limited impact, we expect to have this resolved within [ESTIMATED_RESOLUTION_WINDOW — e.g., "the next 24–48 hours"].

We'll follow up once it's resolved. If you have questions in the meantime, reach out at [SUPPORT_EMAIL].

— The Vantro Team

---

### P2 — Progress Update

**Subject:** Update: Minor Issue — [AFFECTED_FEATURES] | Incident [INCIDENT_ID]
**Title:** Minor Issue Update | [INCIDENT_ID]

---

**Daily update — [UPDATE_DATE]**

A quick status note on incident [INCIDENT_ID].

**Current status:** [CURRENT_STATUS — e.g., "A fix is in development and is on track for deployment by [DATE]", "The fix is being tested before release", "We are still investigating the root cause"]

**Reminder — what's affected:**
[AFFECTED_FEATURES] — [brief description]. All other platform features continue to work normally.

**Estimated resolution:** [DATE/TIME_ESTIMATE or "We'll update you as soon as we have a confirmed timeline."]

Next update: [NEXT_UPDATE_DATE] (unless resolved sooner)
Status page: [STATUS_PAGE_URL]

— The Vantro Team

---

### P2 — Resolution

**Subject:** Fixed: Minor Issue Resolved | Incident [INCIDENT_ID]
**Title:** Resolved — Minor Issue Fixed | [INCIDENT_ID]

---

The minor issue affecting [AFFECTED_FEATURES] has been resolved.

**Incident summary**
- **Incident ID:** [INCIDENT_ID]
- **Start time:** [START_TIME] [TIMEZONE]
- **Resolved at:** [RESOLUTION_TIME] [TIMEZONE]
- **Affected features:** [AFFECTED_FEATURES]

**What happened:**
[1–2 sentences in plain language. Example: "A recent update introduced a display inconsistency in the workspace dashboard that caused certain data to render incorrectly under specific conditions."]

**How we fixed it:**
[1–2 sentences. Example: "We deployed a targeted fix that corrects the rendering logic. All affected views now display accurately."]

No action is needed on your end. If you notice anything that doesn't look right, please let us know at [SUPPORT_EMAIL].

Thank you for your patience.

— The Vantro Team

---

## Variable Reference

| Variable | Description |
|---|---|
| `[INCIDENT_ID]` | Unique incident identifier, e.g., INC-2026-0042 |
| `[START_TIME]` | When the incident began (use 24h or 12h format consistently) |
| `[TIMEZONE]` | Customer's local timezone or UTC |
| `[DETECTION_TIME]` | When the team became aware of the issue |
| `[AFFECTED_FEATURES]` | Plain-language list of what's affected, e.g., "agent job execution and the results dashboard" |
| `[UNAFFECTED_FEATURES]` | What is working normally |
| `[UPDATE_NUMBER]` | Sequential update count starting at 1 |
| `[UPDATE_TIME]` / `[UPDATE_DATE]` | Timestamp or date of the update |
| `[CURRENT_STATUS]` | One-line status summary replacing the full explanation |
| `[RESOLUTION_TIME]` | Timestamp when the incident was resolved |
| `[TOTAL_DURATION]` | Human-readable duration, e.g., "2 hours 14 minutes" |
| `[NEXT_UPDATE_TIME]` / `[NEXT_UPDATE_DATE]` | Committed next communication time |
| `[TIME_ESTIMATE]` / `[ESTIMATED_RESOLUTION_WINDOW]` | Expected resolution time; use ranges if uncertain |
| `[CREDIT_AMOUNT]` | Number of credits awarded; omit block entirely if no credit is given |
| `[STATUS_PAGE_URL]` | Link to the public status page |
| `[SUPPORT_EMAIL]` | Customer support address |
| `[ONE_LINE_SUMMARY]` | Short P2 title summary for status page, e.g., "Dashboard Timestamp Display" |

---

## Editorial Rules

1. **Never mention AI providers, model names, or internal system names.** Use "our platform", "our systems", "the Vantro platform".
2. **Never include stack traces, error codes, or infrastructure terminology** (no database names, container platforms, hosting providers, framework names).
3. **Be honest about uncertainty.** If you don't have a resolution time, say so plainly rather than giving a range that will slip.
4. **One voice.** All templates should read as if written by the same person — calm, direct, and accountable.
5. **Credit is not automatic.** Apply the credit block only when a formal decision has been made. Remove it entirely from the template if no credit is being issued.
6. **P0 updates must go out on time.** A 30-minute update that says "no new information yet" is better than silence.
