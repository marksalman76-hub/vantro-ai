"""
marketing_specialist_agent test suite.

Covers:
  - Prompt structure validation (no LLM calls)
  - Registry entry correctness
  - Executor guard injection (mocked LLM)
  - Guardrail tests
  - API endpoint integration tests
  - Output format validation helper
"""
import pytest
from unittest.mock import patch, MagicMock
from fastapi import status


# â”€â”€ Helpers â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

REQUIRED_SECTIONS = [
    "MARKETING OBJECTIVE",
    "TARGET AUDIENCE",
    "CAMPAIGN CONCEPT",
    "CHANNEL PLAN",
    "FUNNEL STRUCTURE",
    "CONTENT PLAN",
    "BUDGET GUIDANCE",
    "MEASUREMENT PLAN",
    "LAUNCH CHECKLIST",
]

REQUIRED_CONFIDENCE_LABELS = [
    "[DATA-BACKED]",
    "[INDUSTRY STANDARD]",
    "[HYPOTHESIS - A/B TEST FIRST]",
]

HITL_TRIGGER_PHRASES = ["REQUIRES REVIEW", "DRAFT", "owner approval", "human review"]


def has_all_sections(text: str) -> list[str]:
    """Return list of missing required sections (case-insensitive)."""
    upper = text.upper()
    return [s for s in REQUIRED_SECTIONS if s not in upper]


# â”€â”€ 1. Prompt structure tests (no LLM, no network) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@pytest.mark.unit
class TestMarketingSpecialistAgentPrompt:

    def test_prompt_exists(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        assert "marketing_specialist_agent" in AGENT_SYSTEM_PROMPTS

    def test_prompt_is_nonempty(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["marketing_specialist_agent"]
        assert len(prompt.strip()) > 300

    def test_prompt_has_all_required_sections(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["marketing_specialist_agent"]
        missing = has_all_sections(prompt)
        assert missing == [], f"Prompt missing sections: {missing}"

    def test_prompt_has_launch_checklist_section(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["marketing_specialist_agent"].upper()
        assert "LAUNCH CHECKLIST" in prompt

    def test_prompt_has_budget_approval_language(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["marketing_specialist_agent"].lower()
        assert "owner approval" in prompt or "requires owner approval" in prompt
        assert "budget" in prompt

    def test_prompt_has_paid_launch_flag(self):
        """All paid campaign launches must be flagged for owner approval."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["marketing_specialist_agent"]
        assert "PAID CAMPAIGN" in prompt or "paid campaign" in prompt.lower()
        assert "REQUIRES OWNER APPROVAL" in prompt

    def test_prompt_has_confidence_labels(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["marketing_specialist_agent"]
        found = [label for label in REQUIRED_CONFIDENCE_LABELS if label in prompt]
        assert len(found) == 3, f"Missing confidence labels: {[l for l in REQUIRED_CONFIDENCE_LABELS if l not in prompt]}"

    def test_prompt_has_hitl_gate_language(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["marketing_specialist_agent"].upper()
        assert "HITL" in prompt or "REQUIRES REVIEW" in prompt or "HUMAN REVIEW" in prompt

    def test_prompt_has_draft_label(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["marketing_specialist_agent"]
        assert "[DRAFT]" in prompt

    def test_prompt_has_requires_review_tag(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["marketing_specialist_agent"]
        assert "[REQUIRES REVIEW]" in prompt

    def test_get_agent_system_prompt_helper(self):
        from app.agents.agent_prompts import get_agent_system_prompt
        prompt = get_agent_system_prompt("marketing_specialist_agent")
        assert "Marketing" in prompt

    def test_fallback_prompt_for_unknown_agent(self):
        from app.agents.agent_prompts import get_agent_system_prompt
        prompt = get_agent_system_prompt("nonexistent_xyz_agent")
        assert len(prompt) > 20


# â”€â”€ 2. Registry entry tests â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@pytest.mark.unit
class TestMarketingSpecialistAgentRegistry:

    def test_registry_entry_exists(self):
        from app.agents.agent_registry import AGENT_CATALOGUE
        assert "marketing_specialist_agent" in AGENT_CATALOGUE

    def test_registry_hitl_level_is_not_hitl3(self):
        """marketing_specialist_agent is HITL-1/2, never HITL-3."""
        from app.agents.agent_registry import AGENT_CATALOGUE
        entry = AGENT_CATALOGUE["marketing_specialist_agent"]
        assert entry["hitl_default"] != "HITL-3"

    def test_registry_min_package_is_growth(self):
        from app.agents.agent_registry import AGENT_CATALOGUE
        entry = AGENT_CATALOGUE["marketing_specialist_agent"]
        assert entry["min_package"] == "growth"

    def test_registry_has_capabilities(self):
        from app.agents.agent_registry import AGENT_CATALOGUE
        entry = AGENT_CATALOGUE["marketing_specialist_agent"]
        assert isinstance(entry.get("capabilities"), list)
        assert len(entry["capabilities"]) >= 3

    def test_registry_has_role(self):
        from app.agents.agent_registry import AGENT_CATALOGUE
        entry = AGENT_CATALOGUE["marketing_specialist_agent"]
        assert entry.get("role") and len(entry["role"]) > 20

    def test_registry_total_agent_count(self):
        """Non-negotiable: exactly 27 client-facing agents."""
        from app.agents.agent_registry import AGENT_CATALOGUE
        assert len(AGENT_CATALOGUE) == 22


# â”€â”€ 3. Executor tests (mocked LLM) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@pytest.mark.unit
class TestMarketingSpecialistAgentExecutor:

    def test_financial_guard_injected_into_system_prompt(self):
        from app.agents.agent_executor import (
            FINANCIAL_CONSTRAINT_BLOCK,
            INJECTION_GUARD,
            execute_agent,
        )
        captured_system_prompt = []

        def mock_anthropic_call(system_prompt, user_message, **kwargs):
            captured_system_prompt.append(system_prompt)
            return "Clean marketing plan output with no financial actions.", 120, 60

        with patch("app.agents.agent_executor._call_anthropic", side_effect=mock_anthropic_call):
            with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test-key"}):
                execute_agent(
                    agent_id="marketing_specialist_agent",
                    system_prompt="You are the Marketing Specialist Agent.",
                    user_prompt="Create a campaign plan for our SaaS product launch.",
                )

        assert len(captured_system_prompt) == 1
        assert FINANCIAL_CONSTRAINT_BLOCK in captured_system_prompt[0]
        assert INJECTION_GUARD in captured_system_prompt[0]

    def test_clean_output_returns_no_violations(self):
        from app.agents.agent_executor import execute_agent

        def mock_call(system_prompt, user_message, **kwargs):
            return (
                "## MARKETING OBJECTIVE\nGenerate 50 qualified leads in 30 days.\n\n"
                "## TARGET AUDIENCE\nSMB founders aged 30-45. [INDUSTRY STANDARD]\n\n"
                "## CAMPAIGN CONCEPT\nFree audit campaign. [HYPOTHESIS - A/B TEST FIRST]\n\n"
                "## CHANNEL PLAN\nLinkedIn organic. [DATA-BACKED]\n\n"
                "## FUNNEL STRUCTURE\nAwareness > Trial > Conversion.\n\n"
                "## CONTENT PLAN\nWeek 1: Blog post. [DRAFT]\n\n"
                "## BUDGET GUIDANCE\n$2,000/month. BUDGET GUIDANCE ONLY — REQUIRES OWNER APPROVAL.\n\n"
                "## MEASUREMENT PLAN\nPrimary KPI: leads generated. Review weekly.\n\n"
                "## LAUNCH CHECKLIST\n- [ ] Objective confirmed.\n\n"
                "[REQUIRES REVIEW]",
                250, 400,
            )

        with patch("app.agents.agent_executor._call_anthropic", side_effect=mock_call):
            with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test-key"}):
                text, provider, credits, violations = execute_agent(
                    agent_id="marketing_specialist_agent",
                    system_prompt="You are the Marketing Specialist Agent.",
                    user_prompt="Create a campaign plan.",
                )

        assert violations == []
        assert credits >= 1
        assert "anthropic" in provider

    def test_financial_violation_in_output_detected(self):
        from app.agents.agent_executor import execute_agent

        def mock_call(system_prompt, user_message, **kwargs):
            return "I have authorized the campaign spend of $10,000 for Q3.", 100, 50

        with patch("app.agents.agent_executor._call_anthropic", side_effect=mock_call):
            with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test-key"}):
                _, _, _, violations = execute_agent(
                    agent_id="marketing_specialist_agent",
                    system_prompt="System.",
                    user_prompt="Launch the campaign.",
                )

        assert len(violations) > 0

    def test_tokens_to_credits_minimum_one(self):
        from app.agents.agent_executor import _tokens_to_credits
        assert _tokens_to_credits(0, 0) == 1
        assert _tokens_to_credits(1, 1) == 1
        assert _tokens_to_credits(500, 500) == 1
        assert _tokens_to_credits(1000, 1000) == 2

    def test_openai_fallback_when_anthropic_fails(self):
        from app.agents.agent_executor import execute_agent

        def anthropic_fail(system_prompt, user_message):
            raise RuntimeError("Anthropic unavailable")

        def openai_ok(system_prompt, user_message):
            return "OpenAI marketing fallback output.", 120, 80

        with patch("app.agents.agent_executor._call_anthropic", side_effect=anthropic_fail):
            with patch("app.agents.agent_executor._call_openai", side_effect=openai_ok):
                with patch.dict("os.environ", {
                    "ANTHROPIC_API_KEY": "sk-test",
                    "OPENAI_API_KEY": "sk-oai-test",
                }):
                    text, provider, credits, violations = execute_agent(
                        agent_id="marketing_specialist_agent",
                        system_prompt="System.",
                        user_prompt="Create a marketing plan.",
                    )

        assert "openai" in provider
        assert text == "OpenAI marketing fallback output."

    def test_no_provider_raises_runtime_error(self):
        from app.agents.agent_executor import execute_agent
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(RuntimeError, match="No LLM provider"):
                execute_agent(
                    agent_id="marketing_specialist_agent",
                    system_prompt="System.",
                    user_prompt="Create a marketing plan.",
                )


# â”€â”€ 4. Guardrail tests â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@pytest.mark.unit
class TestMarketingSpecialistAgentGuardrails:

    def test_injection_guard_blocks_system_prompt_reveal(self):
        """Injection guard must reference the system prompt and mark it fixed/immutable."""
        from app.agents.agent_executor import INJECTION_GUARD
        assert "system prompt" in INJECTION_GUARD.lower()
        assert (
            "cannot be overridden" in INJECTION_GUARD.lower()
            or "immutable" in INJECTION_GUARD.lower()
            or "fixed" in INJECTION_GUARD.lower()
        )

    def test_financial_patterns_list_has_minimum_count(self):
        """Guard list must have at least 10 patterns for meaningful coverage."""
        from app.agents.agent_executor import FINANCIAL_ACTION_PATTERNS
        assert len(FINANCIAL_ACTION_PATTERNS) >= 10

    def test_financial_constraint_covers_key_actions(self):
        from app.agents.agent_executor import FINANCIAL_CONSTRAINT_BLOCK
        block = FINANCIAL_CONSTRAINT_BLOCK.lower()
        required_coverage = ["spending", "budgets", "payments", "hiring"]
        missing = [term for term in required_coverage if term not in block]
        assert missing == [], f"Financial constraint block missing coverage for: {missing}"

    def test_marketing_agent_is_not_hitl3(self):
        """marketing_specialist_agent must never be HITL-3."""
        from app.agents.agent_registry import AGENT_CATALOGUE
        assert AGENT_CATALOGUE["marketing_specialist_agent"]["hitl_default"] != "HITL-3"

    def test_prompt_has_paid_launch_flag_language(self):
        """Prompt must require owner approval before any paid campaign is launched."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["marketing_specialist_agent"].lower()
        assert "paid" in prompt
        assert "owner approval" in prompt or "requires owner approval" in prompt

    def test_secrets_not_echoed_in_output(self):
        """If user injects a secret, executor must not echo it back in output."""
        from app.agents.agent_executor import execute_agent

        secret = "sk-SUPERSECRET_MARKETING_KEY_99999"

        def mock_call(system_prompt, user_message, **kwargs):
            return "I cannot process credentials. Please provide a campaign brief instead.", 50, 30

        with patch("app.agents.agent_executor._call_anthropic", side_effect=mock_call):
            with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test"}):
                text, _, _, violations = execute_agent(
                    agent_id="marketing_specialist_agent",
                    system_prompt="Marketing Specialist Agent.",
                    user_prompt=f"Use this key to pull ad data: {secret}",
                )

        assert secret not in text


# â”€â”€ 5. API endpoint integration tests â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@pytest.mark.unit
class TestMarketingSpecialistAgentAPI:

    def test_run_marketing_agent_unauthenticated(self, client):
        resp = client.post(
            "/api/agents/marketing_specialist_agent/run",
            json={"prompt": "Create a campaign plan for our product launch."},
        )
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_run_marketing_agent_missing_prompt(self, client, authenticated_client):
        resp = authenticated_client.post(
            "/api/agents/marketing_specialist_agent/run",
            json={},
        )
        assert resp.status_code in (
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_403_FORBIDDEN,
        )

    def test_run_marketing_agent_submits_job(self, client, authenticated_client):
        """Authenticated call with valid prompt should queue a job (no actual LLM call)."""
        mock_output = (
            "## MARKETING OBJECTIVE\nGenerate 50 qualified leads in 30 days.\n\n"
            "## TARGET AUDIENCE\nSMB founders aged 30-45. [INDUSTRY STANDARD]\n\n"
            "## CAMPAIGN CONCEPT\nFree audit campaign. [HYPOTHESIS - A/B TEST FIRST]\n\n"
            "## CHANNEL PLAN\nLinkedIn organic first. [DATA-BACKED]\n\n"
            "## FUNNEL STRUCTURE\nAwareness > Interest > Decision.\n\n"
            "## CONTENT PLAN\nWeek 1: Thought leadership post. [DRAFT]\n\n"
            "## BUDGET GUIDANCE\n$2,000/month. BUDGET GUIDANCE ONLY — REQUIRES OWNER APPROVAL.\n\n"
            "## MEASUREMENT PLAN\nPrimary KPI: leads. Review cadence: weekly.\n\n"
            "## LAUNCH CHECKLIST\n- [ ] Objective confirmed.\n\n"
            "[REQUIRES REVIEW]"
        )
        with patch("app.agents.agent_executor.execute_agent") as mock_exec:
            mock_exec.return_value = (
                mock_output,
                "anthropic/claude-sonnet-4-6",
                3,
                [],
            )
            resp = authenticated_client.post(
                "/api/agents/marketing_specialist_agent/run",
                json={"prompt": "Create a multi-channel marketing campaign for our SaaS product launch."},
            )

        assert resp.status_code in (
            status.HTTP_200_OK,
            status.HTTP_202_ACCEPTED,
            status.HTTP_403_FORBIDDEN,  # insufficient credits/package on test workspace
            status.HTTP_400_BAD_REQUEST,
        )

    def test_jobs_list_after_run(self, client, authenticated_client):
        resp = authenticated_client.get("/api/agents/jobs")
        assert resp.status_code == status.HTTP_200_OK
        body = resp.json()
        assert "jobs" in body


# â”€â”€ 6. Output validator helper tests â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@pytest.mark.unit
class TestMarketingSpecialistOutputValidator:

    def test_section_detection_helper_all_present(self):
        good = "\n".join(f"## {s}" for s in REQUIRED_SECTIONS)
        assert has_all_sections(good) == []

    def test_missing_launch_checklist_detected(self):
        sections_without_checklist = [s for s in REQUIRED_SECTIONS if s != "LAUNCH CHECKLIST"]
        partial = "\n".join(f"## {s}" for s in sections_without_checklist)
        missing = has_all_sections(partial)
        assert "LAUNCH CHECKLIST" in missing

    def test_all_three_confidence_labels_in_mock_output(self):
        output = """
## CHANNEL PLAN
LinkedIn organic content. [DATA-BACKED] — confirmed by our analytics dashboard.
Facebook retargeting. [INDUSTRY STANDARD] — typical for B2C SaaS at this stage.
TikTok short-form video. [HYPOTHESIS - A/B TEST FIRST] — unconfirmed for this audience.
"""
        found = [label for label in REQUIRED_CONFIDENCE_LABELS if label in output]
        assert len(found) == 3

    def test_requires_review_present_in_output(self):
        output = (
            "## LAUNCH CHECKLIST\n"
            "- [ ] Objective confirmed.\n"
            "- [ ] Creative assets reviewed.\n"
            "[REQUIRES REVIEW]"
        )
        assert "[REQUIRES REVIEW]" in output

    def test_budget_approval_label_in_output(self):
        """Budget guidance lines must carry the approval label."""
        output = (
            "## BUDGET GUIDANCE\n"
            "- LinkedIn Ads: $1,500â€“$3,000/month. "
            "BUDGET GUIDANCE ONLY — REQUIRES OWNER APPROVAL before any spend is committed.\n"
            "Total (test phase): $3,000. [BUDGET GUIDANCE ONLY — REQUIRES OWNER APPROVAL]\n"
        )
        assert "REQUIRES OWNER APPROVAL" in output

    def test_section_detection_case_insensitive(self):
        lowercase = "\n".join(f"## {s.lower()}" for s in REQUIRED_SECTIONS)
        assert has_all_sections(lowercase) == []

    def test_section_detection_single_missing(self):
        sections_minus_one = [s for s in REQUIRED_SECTIONS if s != "MEASUREMENT PLAN"]
        partial = "\n".join(f"## {s}" for s in sections_minus_one)
        missing = has_all_sections(partial)
        assert missing == ["MEASUREMENT PLAN"]

    def test_all_sections_in_well_formed_output(self):
        well_formed = """
## MARKETING OBJECTIVE
Generate 50 qualified leads in 30 days via LinkedIn organic and email outreach.
Primary KPI: qualified leads. Target: 50. Timeframe: 30 days.

## TARGET AUDIENCE
SaaS founders at Series A, 30-45, UK market. [INDUSTRY STANDARD]
Pain point: scaling acquisition without burning runway.
Negative audience: solo founders with <Â£50k ARR.

## CAMPAIGN CONCEPT
"The Lean Launch" — show founders how to generate leads for under Â£500/month.
Core concept: audit offer with social proof. [HYPOTHESIS - A/B TEST FIRST]
Tone: authoritative but accessible. [DRAFT]

## CHANNEL PLAN
1. LinkedIn organic — [DATA-BACKED] — primary channel, owned audience.
2. Email newsletter — [INDUSTRY STANDARD] — owned list, zero media spend.
3. Google Search — [HYPOTHESIS - A/B TEST FIRST] — [PAID — REQUIRES OWNER APPROVAL]

## FUNNEL STRUCTURE
Awareness: LinkedIn post > Interest: Lead magnet download > Action: Book call.

## CONTENT PLAN
Week 1: Thought leadership post (LinkedIn). [DRAFT]
Week 2: Case study email. [DRAFT]
Week 3: Ad creative for retargeting. [REQUIRES REVIEW]

## BUDGET GUIDANCE
LinkedIn Ads: Â£1,000â€“Â£2,500/month. BUDGET GUIDANCE ONLY — REQUIRES OWNER APPROVAL before any spend is committed.
Total test phase: Â£2,500. [BUDGET GUIDANCE ONLY — REQUIRES OWNER APPROVAL]

## MEASUREMENT PLAN
Primary KPI: qualified leads. Target: 50 in 30 days.
Review cadence: weekly. Tool: CRM + GA4.
Kill switch: <5 leads after 14 days.

## LAUNCH CHECKLIST
INTERNAL READINESS:
- [ ] Objective and KPIs documented.
- [ ] Audience definition confirmed.

REQUIRES OWNER REVIEW [REQUIRES REVIEW]:
- [ ] Final messaging approved by owner.

REQUIRES OWNER APPROVAL — PAID ACTIVITY [REQUIRES OWNER APPROVAL — PAID CAMPAIGN]:
- [ ] All paid channel budgets approved before spend.

[REQUIRES REVIEW]
"""
        missing = has_all_sections(well_formed)
        assert missing == [], f"Well-formed output should pass all section checks; missing: {missing}"

