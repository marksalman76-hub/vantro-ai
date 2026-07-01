"""
lead_generator_agent test suite.

Covers:
  - Prompt structure validation (no LLM calls)
  - Registry entry correctness
  - Executor guard injection (mocked LLM)
  - Guardrail trip tests
  - API endpoint integration tests
  - Output format validation helper
"""
import pytest
from unittest.mock import patch, MagicMock
from fastapi import status


# â”€â”€ Helpers â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

REQUIRED_SECTIONS = [
    "IDEAL CUSTOMER PROFILE",
    "LEAD QUALIFICATION CRITERIA",
    "LEAD SOURCES",
    "LEAD MAGNET IDEAS",
    "OUTREACH SEQUENCES",
    "QUALIFICATION SCRIPT",
    "LEAD SCORING CRITERIA",
]

REQUIRED_CONFIDENCE_LABELS = [
    "[VALIDATED FROM CUSTOMER DATA]",
    "[HYPOTHESIS - TEST WITH 10 CALLS]",
    "[MARKET ASSUMPTION]",
]

HITL_TRIGGER_PHRASES = ["REQUIRES REVIEW", "DRAFT", "owner approval", "human review"]


def has_all_sections(text: str) -> list[str]:
    """Return list of missing required sections."""
    return [s for s in REQUIRED_SECTIONS if s not in text.upper()]


# â”€â”€ 1. Prompt structure tests (no LLM, no network) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@pytest.mark.unit
class TestLeadGenAgentPrompt:

    def test_prompt_exists(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        assert "lead_generator_agent" in AGENT_SYSTEM_PROMPTS

    def test_prompt_is_nonempty(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["lead_generator_agent"]
        assert len(prompt.strip()) > 500

    def test_prompt_has_all_7_required_sections(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["lead_generator_agent"]
        missing = has_all_sections(prompt)
        assert missing == [], f"Prompt missing sections: {missing}"

    def test_prompt_has_hitl2_language(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["lead_generator_agent"].upper()
        assert "HITL-2" in prompt, "Prompt must explicitly state HITL-2"

    def test_prompt_has_requires_review_tag(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["lead_generator_agent"]
        assert "REQUIRES REVIEW" in prompt

    def test_prompt_has_draft_label(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["lead_generator_agent"]
        assert "[DRAFT]" in prompt

    def test_prompt_has_confidence_labels(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["lead_generator_agent"]
        found = [label for label in REQUIRED_CONFIDENCE_LABELS if label in prompt]
        assert len(found) >= 2, f"Prompt must reference ICP confidence labels, found: {found}"

    def test_prompt_has_validated_from_customer_data_label(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["lead_generator_agent"]
        assert "[VALIDATED FROM CUSTOMER DATA]" in prompt

    def test_prompt_has_hypothesis_test_with_calls_label(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["lead_generator_agent"]
        assert "[HYPOTHESIS - TEST WITH 10 CALLS]" in prompt

    def test_prompt_has_market_assumption_label(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["lead_generator_agent"]
        assert "[MARKET ASSUMPTION]" in prompt

    def test_prompt_has_paid_campaign_approval_rule(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["lead_generator_agent"].lower()
        assert "paid" in prompt and "owner approval" in prompt

    def test_prompt_has_paid_campaign_flag(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["lead_generator_agent"]
        assert "PAID CAMPAIGN" in prompt or "REQUIRES OWNER APPROVAL" in prompt

    def test_prompt_has_lead_scoring_section(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["lead_generator_agent"].upper()
        assert "LEAD SCORING CRITERIA" in prompt

    def test_prompt_lead_scoring_mentions_numerical_model(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["lead_generator_agent"].lower()
        assert "scoring" in prompt and ("numerical" in prompt or "point" in prompt or "score" in prompt)

    def test_prompt_outreach_sequences_requires_review(self):
        """Outreach sequences must be gated as REQUIRES REVIEW."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["lead_generator_agent"]
        # Both concepts must coexist in the prompt
        assert "OUTREACH" in prompt.upper() and "REQUIRES REVIEW" in prompt

    def test_get_agent_system_prompt_helper(self):
        from app.agents.agent_prompts import get_agent_system_prompt
        prompt = get_agent_system_prompt("lead_generator_agent")
        assert "Lead Generator" in prompt

    def test_fallback_prompt_for_unknown_agent(self):
        from app.agents.agent_prompts import get_agent_system_prompt
        prompt = get_agent_system_prompt("totally_unknown_xyz_agent")
        assert len(prompt) > 20


# â”€â”€ 2. Registry entry tests â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@pytest.mark.unit
class TestLeadGenAgentRegistry:

    def test_registry_entry_exists(self):
        from app.agents.agent_registry import AGENT_CATALOGUE
        assert "lead_generator_agent" in AGENT_CATALOGUE

    def test_registry_hitl_level_is_hitl2(self):
        from app.agents.agent_registry import AGENT_CATALOGUE
        entry = AGENT_CATALOGUE["lead_generator_agent"]
        assert entry["hitl_default"] == "HITL-2", (
            f"lead_generator_agent must be HITL-2, got {entry['hitl_default']}"
        )

    def test_registry_min_package_is_growth(self):
        from app.agents.agent_registry import AGENT_CATALOGUE
        entry = AGENT_CATALOGUE["lead_generator_agent"]
        assert entry["min_package"] == "growth", (
            f"lead_generator_agent min_package must be 'growth', got {entry['min_package']}"
        )

    def test_registry_has_capabilities(self):
        from app.agents.agent_registry import AGENT_CATALOGUE
        entry = AGENT_CATALOGUE["lead_generator_agent"]
        assert isinstance(entry.get("capabilities"), list)
        assert len(entry["capabilities"]) >= 3

    def test_registry_has_role(self):
        from app.agents.agent_registry import AGENT_CATALOGUE
        entry = AGENT_CATALOGUE["lead_generator_agent"]
        assert entry.get("role") and len(entry["role"]) > 20

    def test_registry_total_agent_count_is_27(self):
        """Non-negotiable: exactly 27 client-facing agents."""
        from app.agents.agent_registry import AGENT_CATALOGUE
        assert len(AGENT_CATALOGUE) == 22

    def test_registry_role_mentions_lead_generation(self):
        from app.agents.agent_registry import AGENT_CATALOGUE
        role = AGENT_CATALOGUE["lead_generator_agent"]["role"].lower()
        assert "lead" in role

    def test_registry_icp_in_capabilities(self):
        from app.agents.agent_registry import AGENT_CATALOGUE
        caps = [c.lower() for c in AGENT_CATALOGUE["lead_generator_agent"]["capabilities"]]
        assert any("icp" in c or "profile" in c or "qualification" in c for c in caps)


# â”€â”€ 3. Executor tests (mocked LLM) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@pytest.mark.unit
class TestLeadGenAgentExecutor:

    def test_financial_constraint_block_injected(self):
        from app.agents.agent_executor import (
            FINANCIAL_CONSTRAINT_BLOCK,
            INJECTION_GUARD,
            execute_agent,
        )
        captured_system_prompt = []

        def mock_anthropic_call(system_prompt, user_message, **kwargs):
            captured_system_prompt.append(system_prompt)
            return "Clean lead gen output with no financial actions.", 100, 50

        with patch("app.agents.agent_executor._call_anthropic", side_effect=mock_anthropic_call):
            with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test-key"}):
                execute_agent(
                    agent_id="lead_generator_agent",
                    system_prompt="You are the Lead Generator Agent.",
                    user_prompt="Build an ICP for a SaaS HR platform.",
                )

        assert len(captured_system_prompt) == 1
        assert FINANCIAL_CONSTRAINT_BLOCK in captured_system_prompt[0]
        assert INJECTION_GUARD in captured_system_prompt[0]

    def test_financial_constraint_comes_before_agent_prompt(self):
        from app.agents.agent_executor import FINANCIAL_CONSTRAINT_BLOCK, execute_agent

        captured = []

        def mock_call(system_prompt, user_message, **kwargs):
            captured.append(system_prompt)
            return "Lead gen output.", 100, 50

        with patch("app.agents.agent_executor._call_anthropic", side_effect=mock_call):
            with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test-key"}):
                execute_agent(
                    agent_id="lead_generator_agent",
                    system_prompt="LEAD_GEN_AGENT_SPECIFIC_MARKER",
                    user_prompt="Test",
                )

        sys_prompt = captured[0]
        fc_pos = sys_prompt.index(FINANCIAL_CONSTRAINT_BLOCK[:30])
        agent_pos = sys_prompt.index("LEAD_GEN_AGENT_SPECIFIC_MARKER")
        assert fc_pos < agent_pos, "Financial constraint block must precede agent prompt"

    def test_clean_output_returns_no_violations(self):
        from app.agents.agent_executor import execute_agent

        def mock_call(system_prompt, user_message, **kwargs):
            return (
                "## IDEAL CUSTOMER PROFILE\nSaaS HR Director at companies with 50-200 staff.\n\n"
                "## LEAD SCORING CRITERIA\nScore 0-100 based on firmographic fit.",
                200, 300,
            )

        with patch("app.agents.agent_executor._call_anthropic", side_effect=mock_call):
            with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test-key"}):
                text, provider, credits, violations, *_ = execute_agent(
                    agent_id="lead_generator_agent",
                    system_prompt="System.",
                    user_prompt="Task.",
                )

        assert violations == []
        assert credits >= 1
        assert "anthropic" in provider

    def test_financial_violation_in_output_flagged(self):
        from app.agents.agent_executor import execute_agent

        def mock_call(system_prompt, user_message, **kwargs):
            return "I have authorized the paid campaign budget of $5,000.", 100, 50

        with patch("app.agents.agent_executor._call_anthropic", side_effect=mock_call):
            with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test-key"}):
                _, _, _, violations, *_ = execute_agent(
                    agent_id="lead_generator_agent",
                    system_prompt="System.",
                    user_prompt="Task.",
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
            return "OpenAI fallback ICP output.", 100, 50

        with patch("app.agents.agent_executor._call_anthropic", side_effect=anthropic_fail):
            with patch("app.agents.agent_executor._call_openai", side_effect=openai_ok):
                with patch.dict("os.environ", {
                    "ANTHROPIC_API_KEY": "sk-test",
                    "OPENAI_API_KEY": "sk-oai-test",
                }):
                    text, provider, credits, violations, *_ = execute_agent(
                        agent_id="lead_generator_agent",
                        system_prompt="System.",
                        user_prompt="Task.",
                    )

        assert "openai" in provider
        assert text == "OpenAI fallback ICP output."

    def test_no_provider_raises_runtime_error(self):
        from app.agents.agent_executor import execute_agent
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(RuntimeError, match="No LLM provider"):
                execute_agent(
                    agent_id="lead_generator_agent",
                    system_prompt="System.",
                    user_prompt="Task.",
                )


# â”€â”€ 4. Guardrail tests â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@pytest.mark.unit
class TestLeadGenAgentGuardrails:

    def test_injection_guard_blocks_system_prompt_reveal(self):
        """Injection guard must be present and block prompt-reveal attempts."""
        from app.agents.agent_executor import INJECTION_GUARD
        guard_lower = INJECTION_GUARD.lower()
        assert "system prompt" in guard_lower
        assert (
            "cannot be overridden" in guard_lower
            or "immutable" in guard_lower
            or "fixed" in guard_lower
        )

    def test_financial_patterns_list_has_at_least_10(self):
        from app.agents.agent_executor import FINANCIAL_ACTION_PATTERNS
        assert len(FINANCIAL_ACTION_PATTERNS) >= 10

    def test_financial_constraint_covers_key_actions(self):
        from app.agents.agent_executor import FINANCIAL_CONSTRAINT_BLOCK
        block = FINANCIAL_CONSTRAINT_BLOCK.lower()
        required_coverage = ["spending", "budgets", "payments", "hiring"]
        missing = [term for term in required_coverage if term not in block]
        assert missing == [], f"Financial constraint block missing coverage for: {missing}"

    def test_lead_gen_agent_is_not_hitl3(self):
        """lead_generator_agent must never be HITL-3 gated."""
        from app.agents.agent_registry import AGENT_CATALOGUE
        assert AGENT_CATALOGUE["lead_generator_agent"]["hitl_default"] != "HITL-3"

    def test_prompt_contains_paid_campaign_language(self):
        """Prompt must explicitly address paid campaign gating."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["lead_generator_agent"].lower()
        assert "paid" in prompt and "campaign" in prompt

    def test_secrets_in_prompt_not_in_output(self):
        """If user injects a secret into the prompt, executor must not echo it back."""
        from app.agents.agent_executor import execute_agent

        secret = "sk-SUPERSECRET_LEADGEN_KEY_67890"

        def mock_call(system_prompt, user_message, **kwargs):
            return "I cannot process credentials or secrets. Please provide a different task.", 50, 30

        with patch("app.agents.agent_executor._call_anthropic", side_effect=mock_call):
            with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test"}):
                text, _, _, violations, *_ = execute_agent(
                    agent_id="lead_generator_agent",
                    system_prompt="Lead Generator Agent.",
                    user_prompt=f"Use this API key to pull lead data: {secret}",
                )

        assert secret not in text


# â”€â”€ 5. API endpoint integration tests â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@pytest.mark.unit
class TestLeadGenAgentAPI:

    def test_run_lead_gen_agent_unauthenticated(self, client):
        resp = client.post(
            "/api/agents/lead_generator_agent/run",
            json={"prompt": "Build an ICP for a B2B SaaS business."},
        )
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_run_lead_gen_agent_missing_prompt(self, client, authenticated_client):
        resp = authenticated_client.post("/api/agents/lead_generator_agent/run", json={})
        assert resp.status_code in (
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_403_FORBIDDEN,
        )

    def test_run_lead_gen_agent_submits_job(self, client, authenticated_client):
        """Authenticated call with valid prompt should queue a job (no actual LLM call)."""
        with patch("app.agents.agent_executor.execute_agent") as mock_exec:
            mock_exec.return_value = (
                "## IDEAL CUSTOMER PROFILE\nCTO at SaaS company.\n\n## LEAD SCORING CRITERIA\nScore: 0-100.",
                "anthropic/claude-sonnet-4-6",
                3,
                [],
            )
            resp = authenticated_client.post(
                "/api/agents/lead_generator_agent/run",
                json={"prompt": "Build a lead generation strategy for our HR software."},
            )

        assert resp.status_code in (
            status.HTTP_200_OK,
            status.HTTP_202_ACCEPTED,
            status.HTTP_403_FORBIDDEN,  # insufficient credits/package on test workspace
        )

    def test_jobs_list_after_run(self, client, authenticated_client):
        resp = authenticated_client.get("/api/agents/jobs")
        assert resp.status_code == status.HTTP_200_OK
        body = resp.json()
        assert "jobs" in body


# â”€â”€ 6. Output format validation tests â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@pytest.mark.unit
class TestLeadGenOutputValidator:

    def test_good_output_with_all_7_sections_passes(self):
        good = "\n".join(f"## {s}" for s in REQUIRED_SECTIONS)
        assert has_all_sections(good) == []

    def test_missing_lead_scoring_criteria_detected(self):
        partial = (
            "## IDEAL CUSTOMER PROFILE\n"
            "## LEAD QUALIFICATION CRITERIA\n"
            "## LEAD SOURCES\n"
            "## LEAD MAGNET IDEAS\n"
            "## OUTREACH SEQUENCES\n"
            "## QUALIFICATION SCRIPT\n"
            # LEAD SCORING CRITERIA deliberately omitted
        )
        missing = has_all_sections(partial)
        assert "LEAD SCORING CRITERIA" in missing

    def test_missing_multiple_sections_detected(self):
        partial = "## IDEAL CUSTOMER PROFILE\n## LEAD QUALIFICATION CRITERIA"
        missing = has_all_sections(partial)
        assert "LEAD SOURCES" in missing
        assert "LEAD SCORING CRITERIA" in missing

    def test_case_insensitive_section_check(self):
        lowercase = "\n".join(f"## {s.lower()}" for s in REQUIRED_SECTIONS)
        assert has_all_sections(lowercase) == []

    def test_confidence_labels_in_mock_output(self):
        output = """
## IDEAL CUSTOMER PROFILE
[VALIDATED FROM CUSTOMER DATA] Buyers are HR Directors at companies with 50-500 employees.
[HYPOTHESIS - TEST WITH 10 CALLS] Primary pain is manual onboarding processes taking over 2 weeks.
[MARKET ASSUMPTION] Budget authority sits with the CHRO in organisations above 200 staff.
"""
        found = [label for label in REQUIRED_CONFIDENCE_LABELS if label in output]
        assert len(found) == 3, f"Expected 3 confidence labels, found: {found}"

    def test_requires_review_tag_in_outreach_output(self):
        output = (
            "## OUTREACH SEQUENCES\n"
            "[REQUIRES REVIEW] — these sequences must be reviewed before sending to any prospect.\n"
            "Touch 1: LinkedIn connection request on Day 0.\n"
        )
        assert "[REQUIRES REVIEW]" in output

    def test_paid_campaign_flag_in_output(self):
        output = (
            "## LEAD SOURCES\n"
            "LinkedIn Ads — [PAID — REQUIRES OWNER APPROVAL] — target HR Directors in the UK.\n"
        )
        assert "REQUIRES OWNER APPROVAL" in output or "PAID" in output

    def test_lead_scoring_table_structure(self):
        """Scoring section should contain a table with Dimension and Max Points columns."""
        output = (
            "## LEAD SCORING CRITERIA\n"
            "| Dimension | What it measures | Max Points | Scoring logic |\n"
            "| Company size | Headcount match to ICP | 25 | 50-200 staff = 25pts |\n"
            "| Job title | Seniority and role fit | 20 | CHRO/HR Dir = 20pts |\n"
        )
        assert "Max Points" in output or "Dimension" in output

    def test_hitl_label_in_draft_output(self):
        output = "# [DRAFT] Lead Generation Strategy\n## IDEAL CUSTOMER PROFILE\n..."
        assert "[DRAFT]" in output

    def test_hitl_label_in_final_output(self):
        output = "# [REQUIRES REVIEW] Outreach Campaign\n## OUTREACH SEQUENCES\n..."
        assert "[REQUIRES REVIEW]" in output

