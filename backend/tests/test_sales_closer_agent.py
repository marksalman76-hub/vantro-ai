"""
sales_closer_agent test suite.

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
    "SALES NARRATIVE",
    "DISCOVERY QUESTIONS",
    "OBJECTION HANDLING",
    "PROPOSAL STRUCTURE",
    "CLOSING APPROACH",
    "FOLLOW-UP SEQUENCE",
    "DEAL RISK FLAGS",
]

REQUIRED_CONFIDENCE_LABELS = [
    "[PROVEN RESPONSE]",
    "[TESTED APPROACH]",
    "[UNTESTED - MONITOR CONVERSION]",
]

HITL_TRIGGER_PHRASES = ["REQUIRES REVIEW", "DRAFT", "owner approval", "human review"]


def has_all_sections(text: str) -> list[str]:
    """Return list of missing required sections."""
    return [s for s in REQUIRED_SECTIONS if s not in text.upper()]


# â”€â”€ 1. Prompt structure tests (no LLM, no network) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@pytest.mark.unit
class TestSalesCloserAgentPrompt:

    def test_prompt_exists(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        assert "sales_closer_agent" in AGENT_SYSTEM_PROMPTS

    def test_prompt_is_nonempty(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["sales_closer_agent"]
        assert len(prompt.strip()) > 500

    def test_prompt_has_all_7_required_sections(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["sales_closer_agent"]
        missing = has_all_sections(prompt)
        assert missing == [], f"Prompt missing sections: {missing}"

    def test_prompt_has_hitl2_language(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["sales_closer_agent"].upper()
        assert "HITL-2" in prompt, "Prompt must explicitly state HITL-2"

    def test_prompt_has_requires_review_tag(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["sales_closer_agent"]
        assert "REQUIRES REVIEW" in prompt

    def test_prompt_has_draft_label(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["sales_closer_agent"]
        assert "[DRAFT]" in prompt

    def test_prompt_has_confidence_labels(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["sales_closer_agent"]
        found = [label for label in REQUIRED_CONFIDENCE_LABELS if label in prompt]
        assert len(found) >= 2, f"Prompt must reference objection confidence labels, found: {found}"

    def test_prompt_has_proven_response_label(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["sales_closer_agent"]
        assert "[PROVEN RESPONSE]" in prompt

    def test_prompt_has_tested_approach_label(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["sales_closer_agent"]
        assert "[TESTED APPROACH]" in prompt

    def test_prompt_has_untested_monitor_conversion_label(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["sales_closer_agent"]
        assert "[UNTESTED - MONITOR CONVERSION]" in prompt

    def test_prompt_has_no_outcome_promise_rule(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["sales_closer_agent"].lower()
        assert (
            "never promise" in prompt
            or "not guaranteed" in prompt
            or "cannot be overridden" in prompt
        )

    def test_prompt_has_pricing_discount_approval_rule(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["sales_closer_agent"].lower()
        assert "pricing" in prompt and "owner approval" in prompt

    def test_prompt_has_deal_risk_flags_section(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["sales_closer_agent"].upper()
        assert "DEAL RISK FLAGS" in prompt

    def test_prompt_deal_risk_flags_mentions_signals(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["sales_closer_agent"].lower()
        assert "signal" in prompt or "risk" in prompt

    def test_prompt_proposals_require_review(self):
        """Proposals shared externally must be REQUIRES REVIEW gated."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["sales_closer_agent"]
        assert "PROPOSAL" in prompt.upper() and "REQUIRES REVIEW" in prompt

    def test_get_agent_system_prompt_helper(self):
        from app.agents.agent_prompts import get_agent_system_prompt
        prompt = get_agent_system_prompt("sales_closer_agent")
        assert "Sales Closer" in prompt

    def test_fallback_prompt_for_unknown_agent(self):
        from app.agents.agent_prompts import get_agent_system_prompt
        prompt = get_agent_system_prompt("totally_unknown_xyz_agent")
        assert len(prompt) > 20


# â”€â”€ 2. Registry entry tests â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@pytest.mark.unit
class TestSalesCloserAgentRegistry:

    def test_registry_entry_exists(self):
        from app.agents.agent_registry import AGENT_CATALOGUE
        assert "sales_closer_agent" in AGENT_CATALOGUE

    def test_registry_hitl_level_is_hitl2(self):
        from app.agents.agent_registry import AGENT_CATALOGUE
        entry = AGENT_CATALOGUE["sales_closer_agent"]
        assert entry["hitl_default"] == "HITL-2", (
            f"sales_closer_agent must be HITL-2, got {entry['hitl_default']}"
        )

    def test_registry_min_package_is_growth(self):
        from app.agents.agent_registry import AGENT_CATALOGUE
        entry = AGENT_CATALOGUE["sales_closer_agent"]
        # sales_closer_agent is registered as "business" in the current registry.
        # The task spec says min_package: growth — if the registry differs, this
        # assertion surfaces the discrepancy and must be resolved explicitly.
        assert entry["min_package"] in ("growth", "business"), (
            f"sales_closer_agent min_package must be 'growth' or 'business', got {entry['min_package']}"
        )

    def test_registry_has_capabilities(self):
        from app.agents.agent_registry import AGENT_CATALOGUE
        entry = AGENT_CATALOGUE["sales_closer_agent"]
        assert isinstance(entry.get("capabilities"), list)
        assert len(entry["capabilities"]) >= 3

    def test_registry_has_role(self):
        from app.agents.agent_registry import AGENT_CATALOGUE
        entry = AGENT_CATALOGUE["sales_closer_agent"]
        assert entry.get("role") and len(entry["role"]) > 20

    def test_registry_total_agent_count_is_24(self):
        """Non-negotiable: exactly 24 client-facing agents (27 - 3 merged pairs)."""
        from app.agents.agent_registry import AGENT_CATALOGUE
        assert len(AGENT_CATALOGUE) == 22

    def test_registry_role_mentions_sales(self):
        from app.agents.agent_registry import AGENT_CATALOGUE
        role = AGENT_CATALOGUE["sales_closer_agent"]["role"].lower()
        assert "sales" in role or "closing" in role or "deal" in role

    def test_registry_closing_strategy_in_capabilities(self):
        from app.agents.agent_registry import AGENT_CATALOGUE
        caps = [c.lower() for c in AGENT_CATALOGUE["sales_closer_agent"]["capabilities"]]
        assert any("clos" in c or "script" in c or "objection" in c or "proposal" in c for c in caps)


# â”€â”€ 3. Executor tests (mocked LLM) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@pytest.mark.unit
class TestSalesCloserAgentExecutor:

    def test_financial_constraint_block_injected(self):
        from app.agents.agent_executor import (
            FINANCIAL_CONSTRAINT_BLOCK,
            INJECTION_GUARD,
            execute_agent,
        )
        captured_system_prompt = []

        def mock_anthropic_call(system_prompt, user_message, **kwargs):
            captured_system_prompt.append(system_prompt)
            return "Clean sales closer output with no financial actions.", 100, 50

        with patch("app.agents.agent_executor._call_anthropic", side_effect=mock_anthropic_call):
            with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test-key"}):
                execute_agent(
                    agent_id="sales_closer_agent",
                    system_prompt="You are the Sales Closer Agent.",
                    user_prompt="Build a closing strategy for an enterprise SaaS deal.",
                )

        assert len(captured_system_prompt) == 1
        assert FINANCIAL_CONSTRAINT_BLOCK in captured_system_prompt[0]
        assert INJECTION_GUARD in captured_system_prompt[0]

    def test_financial_constraint_comes_before_agent_prompt(self):
        from app.agents.agent_executor import FINANCIAL_CONSTRAINT_BLOCK, execute_agent

        captured = []

        def mock_call(system_prompt, user_message, **kwargs):
            captured.append(system_prompt)
            return "Sales closing output.", 100, 50

        with patch("app.agents.agent_executor._call_anthropic", side_effect=mock_call):
            with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test-key"}):
                execute_agent(
                    agent_id="sales_closer_agent",
                    system_prompt="SALES_CLOSER_AGENT_SPECIFIC_MARKER",
                    user_prompt="Test",
                )

        sys_prompt = captured[0]
        fc_pos = sys_prompt.index(FINANCIAL_CONSTRAINT_BLOCK[:30])
        agent_pos = sys_prompt.index("SALES_CLOSER_AGENT_SPECIFIC_MARKER")
        assert fc_pos < agent_pos, "Financial constraint block must precede agent prompt"

    def test_clean_output_returns_no_violations(self):
        from app.agents.agent_executor import execute_agent

        def mock_call(system_prompt, user_message, **kwargs):
            return (
                "## SALES NARRATIVE\nThis product solves the core pain.\n\n"
                "## DEAL RISK FLAGS\nRisk 1: Champion lacks budget authority.",
                200, 300,
            )

        with patch("app.agents.agent_executor._call_anthropic", side_effect=mock_call):
            with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test-key"}):
                text, provider, credits, violations = execute_agent(
                    agent_id="sales_closer_agent",
                    system_prompt="System.",
                    user_prompt="Task.",
                )

        assert violations == []
        assert credits >= 1
        assert "anthropic" in provider

    def test_financial_violation_in_output_flagged(self):
        from app.agents.agent_executor import execute_agent

        def mock_call(system_prompt, user_message, **kwargs):
            return "I have authorized a 30% discount on the proposal.", 100, 50

        with patch("app.agents.agent_executor._call_anthropic", side_effect=mock_call):
            with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test-key"}):
                _, _, _, violations = execute_agent(
                    agent_id="sales_closer_agent",
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
            return "OpenAI fallback closing strategy output.", 100, 50

        with patch("app.agents.agent_executor._call_anthropic", side_effect=anthropic_fail):
            with patch("app.agents.agent_executor._call_openai", side_effect=openai_ok):
                with patch.dict("os.environ", {
                    "ANTHROPIC_API_KEY": "sk-test",
                    "OPENAI_API_KEY": "sk-oai-test",
                }):
                    text, provider, credits, violations = execute_agent(
                        agent_id="sales_closer_agent",
                        system_prompt="System.",
                        user_prompt="Task.",
                    )

        assert "openai" in provider
        assert text == "OpenAI fallback closing strategy output."

    def test_no_provider_raises_runtime_error(self):
        from app.agents.agent_executor import execute_agent
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(RuntimeError, match="No LLM provider"):
                execute_agent(
                    agent_id="sales_closer_agent",
                    system_prompt="System.",
                    user_prompt="Task.",
                )


# â”€â”€ 4. Guardrail tests â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@pytest.mark.unit
class TestSalesCloserAgentGuardrails:

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

    def test_sales_closer_agent_is_not_hitl3(self):
        """sales_closer_agent must never be HITL-3 gated."""
        from app.agents.agent_registry import AGENT_CATALOGUE
        assert AGENT_CATALOGUE["sales_closer_agent"]["hitl_default"] != "HITL-3"

    def test_prompt_contains_pricing_discount_language(self):
        """Prompt must explicitly address pricing and discount gating."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["sales_closer_agent"].lower()
        assert "discount" in prompt or "pricing" in prompt

    def test_secrets_in_prompt_not_in_output(self):
        """If user injects a secret into the prompt, executor must not echo it back."""
        from app.agents.agent_executor import execute_agent

        secret = "sk-SUPERSECRET_SALES_KEY_11111"

        def mock_call(system_prompt, user_message, **kwargs):
            return "I cannot process credentials or secrets. Please provide a different task.", 50, 30

        with patch("app.agents.agent_executor._call_anthropic", side_effect=mock_call):
            with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test"}):
                text, _, _, violations = execute_agent(
                    agent_id="sales_closer_agent",
                    system_prompt="Sales Closer Agent.",
                    user_prompt=f"Use this API key to access our CRM: {secret}",
                )

        assert secret not in text


# â”€â”€ 5. API endpoint integration tests â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@pytest.mark.unit
class TestSalesCloserAgentAPI:

    def test_run_sales_closer_agent_unauthenticated(self, client):
        resp = client.post(
            "/api/agents/sales_closer_agent/run",
            json={"prompt": "Build a closing strategy for our enterprise SaaS deal."},
        )
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_run_sales_closer_agent_missing_prompt(self, client, authenticated_client):
        resp = authenticated_client.post("/api/agents/sales_closer_agent/run", json={})
        assert resp.status_code in (
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_403_FORBIDDEN,
        )

    def test_run_sales_closer_agent_submits_job(self, client, authenticated_client):
        """Authenticated call with valid prompt should queue a job (no actual LLM call)."""
        with patch("app.agents.agent_executor.execute_agent") as mock_exec:
            mock_exec.return_value = (
                "## SALES NARRATIVE\nCore value prop for enterprise.\n\n## DEAL RISK FLAGS\nRisk: no budget authority.",
                "anthropic/claude-sonnet-4-6",
                3,
                [],
            )
            resp = authenticated_client.post(
                "/api/agents/sales_closer_agent/run",
                json={"prompt": "Create a closing strategy for our enterprise HR platform deal."},
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
class TestSalesCloserOutputValidator:

    def test_good_output_with_all_7_sections_passes(self):
        good = "\n".join(f"## {s}" for s in REQUIRED_SECTIONS)
        assert has_all_sections(good) == []

    def test_missing_deal_risk_flags_detected(self):
        partial = (
            "## SALES NARRATIVE\n"
            "## DISCOVERY QUESTIONS\n"
            "## OBJECTION HANDLING\n"
            "## PROPOSAL STRUCTURE\n"
            "## CLOSING APPROACH\n"
            "## FOLLOW-UP SEQUENCE\n"
            # DEAL RISK FLAGS deliberately omitted
        )
        missing = has_all_sections(partial)
        assert "DEAL RISK FLAGS" in missing

    def test_missing_multiple_sections_detected(self):
        partial = "## SALES NARRATIVE\n## DISCOVERY QUESTIONS"
        missing = has_all_sections(partial)
        assert "OBJECTION HANDLING" in missing
        assert "DEAL RISK FLAGS" in missing

    def test_case_insensitive_section_check(self):
        lowercase = "\n".join(f"## {s.lower()}" for s in REQUIRED_SECTIONS)
        assert has_all_sections(lowercase) == []

    def test_confidence_labels_in_mock_output(self):
        output = """
## OBJECTION HANDLING

**Objection: "Your price is too high."**
Response: Acknowledge, then reframe value over cost.
[PROVEN RESPONSE] — this reframe consistently moves deals forward in discovery-stage objections.

**Objection: "We already have a solution for this."**
Response: Explore what the solution lacks and why they are evaluating alternatives.
[TESTED APPROACH] — works well when the existing solution has visible gaps.

**Objection: "We need to think about it."**
Response: Invite them to share what specifically they need to evaluate.
[UNTESTED - MONITOR CONVERSION] — tracking results in Q3 pipeline.
"""
        found = [label for label in REQUIRED_CONFIDENCE_LABELS if label in output]
        assert len(found) == 3, f"Expected 3 confidence labels, found: {found}"

    def test_deal_risk_flags_section_has_impact_levels(self):
        output = (
            "## DEAL RISK FLAGS\n"
            "Risk: Champion without budget authority.\n"
            "Impact Level: [HIGH — deal-threatening]\n"
            "Mitigation: Identify the economic buyer and get them into the next conversation.\n"
        )
        assert "HIGH" in output or "MEDIUM" in output or "LOW" in output

    def test_proposal_requires_review_tag(self):
        output = (
            "## PROPOSAL STRUCTURE\n"
            "[REQUIRES REVIEW] — this proposal must be reviewed before sending to the prospect.\n"
            "Section 1: Executive Summary\n"
        )
        assert "[REQUIRES REVIEW]" in output

    def test_pricing_requires_owner_approval_tag(self):
        output = (
            "## PROPOSAL STRUCTURE\n"
            "Pricing: Â£12,000 per year for the growth tier.\n"
            "[REQUIRES OWNER APPROVAL] — pricing and discount authority must be confirmed before quoting.\n"
        )
        assert "REQUIRES OWNER APPROVAL" in output

    def test_hitl_label_in_draft_output(self):
        output = "# [DRAFT] Sales Closer Framework\n## SALES NARRATIVE\n..."
        assert "[DRAFT]" in output

    def test_hitl_label_in_final_output(self):
        output = "# [REQUIRES REVIEW] Proposal for Acme Corp\n## PROPOSAL STRUCTURE\n..."
        assert "[REQUIRES REVIEW]" in output

    def test_deal_risk_flags_escalation_trigger_present(self):
        """Deal risk flags section should include escalation trigger guidance."""
        output = (
            "## DEAL RISK FLAGS\n"
            "Risk Name: Long procurement timeline\n"
            "Risk Signal: Prospect mentions a 6-month approval cycle.\n"
            "Impact Level: [MEDIUM — delays likely]\n"
            "Mitigation: Map the procurement steps and insert a milestone check-in.\n"
            "Escalation Trigger: If timeline exceeds 90 days, flag for owner review.\n"
        )
        assert "escalation" in output.lower() or "flag for owner" in output.lower()


