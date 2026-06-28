# Vantro.ai — T+7 Post-Launch Retrospective
## Working Session Document | NOT FOR EXTERNAL DISTRIBUTION

---

## 1. MEETING HEADER

| Field | Value |
|---|---|
| Date | [DATE] |
| Time | [START_TIME] — [END_TIME] (target: 90 min) |
| Facilitator | [FACILITATOR_NAME] |
| Note-taker | [NOTE_TAKER_NAME] |
| Location / Call | [IN_PERSON / ZOOM / SLACK_HUDDLE] |
| Attendees | [NAME_1], [NAME_2], [NAME_3], [NAME_4] |
| Absent | [NAME] — [REASON] |

**Standing rule for this session:** No blame, no defense. Every finding maps to an action. If you can't write an action item, the finding doesn't go in the doc.

---

## 2. METRICS SCORECARD

> Delta = Actual − Target. Positive is good unless noted. Status: Green = within 5% of target or better; Yellow = 5–20% off; Red = >20% off or threshold crossed.

| KPI | Target | Actual | Delta | Status |
|---|---|---|---|---|
| Total signups (T+7) | [TARGET] | [ACTUAL] | [DELTA] | [Green / Yellow / Red] |
| Activation rate (% ran ≥1 agent job) | [TARGET]% | [ACTUAL]% | [DELTA]pp | [Green / Yellow / Red] |
| Day-1 retention | [TARGET]% | [ACTUAL]% | [DELTA]pp | [Green / Yellow / Red] |
| Day-7 retention | [TARGET]% | [ACTUAL]% | [DELTA]pp | [Green / Yellow / Red] |
| Avg agent jobs / active workspace (T+7) | [TARGET] | [ACTUAL] | [DELTA] | [Green / Yellow / Red] |
| Credit consumption rate (credits/workspace/day) | [TARGET] | [ACTUAL] | [DELTA] | [Green / Yellow / Red] |
| P95 API latency (ms) | ≤ [TARGET]ms | [ACTUAL]ms | [DELTA]ms | [Green / Yellow / Red] |
| Uptime % (T+7 window) | ≥ [TARGET]% | [ACTUAL]% | [DELTA]pp | [Green / Yellow / Red] |
| Support ticket volume (total, T+7) | ≤ [TARGET] | [ACTUAL] | [DELTA] | [Green / Yellow / Red] |
| CSAT / NPS score | [TARGET] | [ACTUAL] | [DELTA] | [Green / Yellow / Red] |
| Financial review queue max depth | ≤ [TARGET] | [ACTUAL] | [DELTA] | [Green / Yellow / Red] |
| Revenue — MRR or one-time credits sold | [TARGET] | [ACTUAL] | [DELTA] | [Green / Yellow / Red] |

**Scorecard summary:** [X] Green / [X] Yellow / [X] Red

**Headline read:** [One sentence — are we on track, behind, or ahead of plan?]

---

## 3. INCIDENT TIMELINE

> List every incident that required human escalation, customer communication, or code/config change during T+0 through T+7. If none: write "No incidents recorded."

| Time (UTC) | Severity | Description | TTR | Root Cause (1 line) | Action Item |
|---|---|---|---|---|---|
| [YYYY-MM-DD HH:MM] | [P0 / P1 / P2] | [WHAT HAPPENED] | [Xh Ym] | [ROOT_CAUSE] | [ACTION_ITEM_REF] |
| [YYYY-MM-DD HH:MM] | [P0 / P1 / P2] | [WHAT HAPPENED] | [Xh Ym] | [ROOT_CAUSE] | [ACTION_ITEM_REF] |
| [YYYY-MM-DD HH:MM] | [P0 / P1 / P2] | [WHAT HAPPENED] | [Xh Ym] | [ROOT_CAUSE] | [ACTION_ITEM_REF] |

**Severity definitions:**
- P0 — Full outage or data integrity risk; all hands
- P1 — Partial degradation affecting >10% of workspaces or a billing/financial workflow
- P2 — Single-workspace issue or cosmetic; resolved within normal support SLA

**Total P0s:** [X] | **Total P1s:** [X] | **Total P2s:** [X] | **Mean TTR:** [X]h [X]m

---

## 4. WHAT WENT WELL

> For each prompt, write at least one specific, concrete observation. Vague answers ("things went fine") are not accepted.

### 4a. System Reliability
**Prompt: What held up better than expected?**

- [OBSERVATION — e.g., "ECS Fargate autoscaling handled the T+0 spike without manual intervention; no task restarts"]
- [OBSERVATION]
- [OBSERVATION]

### 4b. Customer Response
**Prompt: What feedback surprised us positively?**

- [OBSERVATION — e.g., "Three workspaces ran >50 agent jobs on Day 1 with zero support contacts"]
- [OBSERVATION]
- [OBSERVATION]

### 4c. Team Execution
**Prompt: What process worked well under pressure?**

- [OBSERVATION — e.g., "On-call rotation held; all P1 pages acknowledged within 8 minutes"]
- [OBSERVATION]
- [OBSERVATION]

### 4d. Product
**Prompt: What feature got more usage than expected?**

- [OBSERVATION — e.g., "Financial review queue visibility — customers appreciated seeing items flagged rather than silently rejected"]
- [OBSERVATION]
- [OBSERVATION]

---

## 5. WHAT DIDN'T GO WELL

> Same rule: specific and concrete. "Communication could be better" is not a finding. "Customers couldn't find the credit top-up button until Day 3" is.

### 5a. System Issues
**Prompt: What broke or degraded that we didn't anticipate?**

- [FINDING — e.g., "PostgreSQL connection pool exhausted at 08:00 UTC Day 2 under 40 concurrent workspace jobs; p95 latency spiked to 4.2s for 11 minutes"]
- [FINDING]
- [FINDING]

### 5b. Customer Experience
**Prompt: Where did customers get stuck or confused?**

- [FINDING — e.g., "7 of 12 Day-1 support tickets were 'how do I connect my Shopify store' — onboarding copy does not surface integrations setup early enough"]
- [FINDING]
- [FINDING]

### 5c. Team Process
**Prompt: What slowed us down internally?**

- [FINDING — e.g., "No agreed runbook for financial review queue overflow; two team members made conflicting decisions on Day 3"]
- [FINDING]
- [FINDING]

### 5d. Product Gaps
**Prompt: What were customers asking for that we don't have?**

- [FINDING — e.g., "Bulk agent job scheduling — requested by [X] workspaces in the first 72h"]
- [FINDING]
- [FINDING]

---

## 6. ACTION ITEMS

> Every finding in sections 3, 4, and 5 must map to at least one row here or be explicitly closed as "accepted risk."

### Group A — T+14 Urgent (must be resolved before T+14 expansion gate)

| Priority | Item | Owner | Deadline | Success Criteria |
|---|---|---|---|---|
| [P0 / P1 / P2] | [ACTION_ITEM] | [OWNER] | [DATE] | [MEASURABLE_OUTCOME] |
| [P0 / P1 / P2] | [ACTION_ITEM] | [OWNER] | [DATE] | [MEASURABLE_OUTCOME] |
| [P0 / P1 / P2] | [ACTION_ITEM] | [OWNER] | [DATE] | [MEASURABLE_OUTCOME] |
| [P0 / P1 / P2] | [ACTION_ITEM] | [OWNER] | [DATE] | [MEASURABLE_OUTCOME] |
| [P0 / P1 / P2] | [ACTION_ITEM] | [OWNER] | [DATE] | [MEASURABLE_OUTCOME] |

### Group B — T+30+ Roadmap (important but not blocking T+14 go-live)

| Priority | Item | Owner | Deadline | Success Criteria |
|---|---|---|---|---|
| [P1 / P2] | [ACTION_ITEM] | [OWNER] | [DATE] | [MEASURABLE_OUTCOME] |
| [P1 / P2] | [ACTION_ITEM] | [OWNER] | [DATE] | [MEASURABLE_OUTCOME] |
| [P1 / P2] | [ACTION_ITEM] | [OWNER] | [DATE] | [MEASURABLE_OUTCOME] |
| [P1 / P2] | [ACTION_ITEM] | [OWNER] | [DATE] | [MEASURABLE_OUTCOME] |

**Accepted risks (not actioned):**

| Finding | Rationale | Revisit Date |
|---|---|---|
| [FINDING] | [WHY ACCEPTED AS-IS] | [DATE] |

---

## 7. GO/NO-GO DECISION RECORD — T+14 EXPANSION

> Each gate is binary. "Conditional" is allowed only if the condition is specific, measurable, and owned. Handwavy conditions are No-Go.

| Gate | Threshold | T+7 Actual | Status | Notes |
|---|---|---|---|---|
| Uptime over T+7 window | ≥ [UPTIME_THRESHOLD]% | [ACTUAL]% | [Go / No-Go / Conditional] | [NOTE] |
| P95 API latency | ≤ [LATENCY_THRESHOLD]ms | [ACTUAL]ms | [Go / No-Go / Conditional] | [NOTE] |
| Open P0 incidents | 0 | [ACTUAL] | [Go / No-Go / Conditional] | [NOTE] |
| Financial review queue max depth | ≤ [QUEUE_THRESHOLD] items | [ACTUAL] | [Go / No-Go / Conditional] | [NOTE] |
| Activation rate | ≥ [ACTIVATION_THRESHOLD]% | [ACTUAL]% | [Go / No-Go / Conditional] | [NOTE] |
| Support ticket backlog (open) | ≤ [TICKET_THRESHOLD] | [ACTUAL] | [Go / No-Go / Conditional] | [NOTE] |

### Final Decision

> Circle one. If Conditional, the condition must be written in the box below before sign-off is valid.

**[ GO ] &nbsp;&nbsp; [ NO-GO ] &nbsp;&nbsp; [ CONDITIONAL ]**

**Decision rationale:**
[One paragraph. State which gates drove the decision. If Conditional, state exactly what must be true before T+14 go-live is authorized, who owns verification, and by what date.]

**Conditional go-live trigger (if applicable):**
- Condition: [SPECIFIC_MEASURABLE_CONDITION]
- Owner: [NAME]
- Verification deadline: [DATE / TIME]
- Verified by: [NAME]

---

## 8. STAKEHOLDER SIGN-OFF

> Sign-off confirms: (a) you were present or reviewed the document, (b) you agree with the recorded decision, (c) you accept ownership of your assigned action items.

| Name | Role | Decision | Date | Signature / Initials |
|---|---|---|---|---|
| [NAME] | Founder / Owner | [Go / No-Go / Conditional] | [DATE] | [INITIALS] |
| [NAME] | Engineering Lead | [Go / No-Go / Conditional] | [DATE] | [INITIALS] |
| [NAME] | Product Lead | [Go / No-Go / Conditional] | [DATE] | [INITIALS] |
| [NAME] | Support Lead | [Go / No-Go / Conditional] | [DATE] | [INITIALS] |

**Dissenting opinions (if any):**
[NAME] — [DISSENT_TEXT]

---

## DOCUMENT CONTROL

| Field | Value |
|---|---|
| Version | 1.0 |
| Created | [DATE] |
| Last updated | [DATE] |
| Owner | [NAME] |
| Next review | T+14 retro (scheduled: [DATE]) |
| Storage location | [INTERNAL_LINK_OR_PATH] |

---

*This document is an internal working record. Distribution outside the core team requires explicit approval from the Founder/Owner.*
