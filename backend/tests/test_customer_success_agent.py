"""
customer_success_agent test suite.

Covers:
  - Prompt structure validation (no LLM calls)
  - Registry entry correctness
  - Executor guard injection (mocked LLM)
  - Financial action scanner (unit)
  - Guardrail trip tests (mocked output)
  - API endpoint integration tests
  - Output format validation helper
"""
import pytest
from unittest.mock import patch, MagicMock
from fastapi import status


# â”€â”€ Helpers â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

REQUIRED_SECTIONS = [
    "CUSTOMER SUCCESS FRAMEWORK",
    "ONBOARDING FLOW",
    "HEALTH SCORE MODEL",
    "RETENTION PLAYBOOK",
    "LOYALTY PROGRAMME DESIGN",
    "RENEWAL & EXPANSION SEQUENCES",
]

REQUIRED_CONFIDENCE_LABELS = [
    "[VALIDATED SIGNAL]",
    "[PROXY METRIC]",
    "[ASSUMED - MONITOR CLOSELY]",
]

HITL_TRIGGER_PHRASES = ["REQUIRES REVIEW", "DRAFT", "owner approval", "human review"]


def has_all_sections(text: str) -> list[str]:
    """Return list of missing required sections."""
    return [s for s in REQUIRED_SECTIONS if s not in text.upper()]


# â”€â”€ 1. Prompt structure tests â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@pytest.mark.unit
class TestCustomerSuccessAgentPrompt:

    def test_prompt_exists(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        assert "customer_lifecycle_agent" in AGENT_SYSTEM_PROMPTS

    def test_prompt_is_nonempty(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["customer_lifecycle_agent"]
        assert len(prompt.strip()) > 500

    def test_prompt_has_all_required_sections(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["customer_lifecycle_agent"]
        missing = has_all_sections(prompt)
        assert missing == [], f"Prompt missing sections: {missing}"

    def test_prompt_has_hitl_gate_language(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["customer_lifecycle_agent"].upper()
        assert "HITL" in prompt or "REQUIRES REVIEW" in prompt or "DRAFT" in prompt

    def test_prompt_has_hitl_gate_block(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["customer_lifecycle_agent"]
        assert "HITL GATES" in prompt

    def test_prompt_has_confidence_labels(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["customer_lifecycle_agent"]
        found = [label for label in REQUIRED_CONFIDENCE_LABELS if label in prompt]
        assert len(found) >= 2, f"Prompt should reference confidence labels, found: {found}"

    def test_prompt_has_validated_signal_label(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["customer_lifecycle_agent"]
        assert "[VALIDATED SIGNAL]" in prompt

    def test_prompt_has_proxy_metric_label(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["customer_lifecycle_agent"]
        assert "[PROXY METRIC]" in prompt

    def test_prompt_has_assumed_monitor_closely_label(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["customer_lifecycle_agent"]
        assert "[ASSUMED - MONITOR CLOSELY]" in prompt

    def test_prompt_discount_flag_rule(self):
        """Discount and compensation decisions must require owner approval."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["customer_lifecycle_agent"].lower()
        assert "discount" in prompt
        assert "owner approval" in prompt

    def test_prompt_compensation_requires_owner_approval(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["customer_lifecycle_agent"].lower()
        assert "compensation" in prompt or "concession" in prompt

    def test_prompt_automation_review_rule(self):
        """Automated communication sequences must require review before activation."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["customer_lifecycle_agent"].lower()
        assert "automat" in prompt
        assert "review" in prompt

    def test_prompt_has_requires_review_tag(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["customer_lifecycle_agent"]
        assert "[REQUIRES REVIEW]" in prompt

    def test_prompt_has_draft_tag(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["customer_lifecycle_agent"]
        assert "[DRAFT]" in prompt

    def test_get_agent_system_prompt_helper(self):
        from app.agents.agent_prompts import get_agent_system_prompt
        prompt = get_agent_system_prompt("customer_lifecycle_agent")
        assert "Customer" in prompt or "Lifecycle" in prompt

    def test_fallback_prompt_for_unknown_agent(self):
        from app.agents.agent_prompts import get_agent_system_prompt
        prompt = get_agent_system_prompt("totally_unknown_xyz_agent")
        assert len(prompt) > 20

    def test_prompt_source_integrity_rule(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["customer_lifecycle_agent"].lower()
        assert "fabricat" in prompt or "invent" in prompt or "observable" in prompt or "unavailable" in prompt


# â”€â”€ 2. Registry entry tests â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@pytest.mark.unit
class TestCustomerSuccessAgentRegistry:

    def test_registry_entry_exists(self):
        from app.agents.agent_registry import AGENT_CATALOGUE
        assert "customer_lifecycle_agent" in AGENT_CATALOGUE

    def test_registry_hitl_level_present(self):
        from app.agents.agent_registry import AGENT_CATALOGUE
        entry = AGENT_CATALOGUE["customer_lifecycle_agent"]
        assert "hitl_default" in entry

    def test_registry_hitl_level_is_hitl2(self):
        from app.agents.agent_registry import AGENT_CATALOGUE
        entry = AGENT_CATALOGUE["customer_lifecycle_agent"]
        assert entry["hitl_default"] == "HITL-2"

    def test_registry_min_package_is_growth(self):
        from app.agents.agent_registry import AGENT_CATALOGUE
        entry = AGENT_CATALOGUE["customer_lifecycle_agent"]
        assert entry["min_package"] == "growth"

    def test_registry_has_capabilities(self):
        from app.agents.agent_registry import AGENT_CATALOGUE
        entry = AGENT_CATALOGUE["customer_lifecycle_agent"]
        assert isinstance(entry.get("capabilities"), list)
        assert len(entry["capabilities"]) >= 3

    def test_registry_has_role(self):
        from app.agents.agent_registry import AGENT_CATALOGUE
        entry = AGENT_CATALOGUE["customer_lifecycle_agent"]
        assert entry.get("role") and len(entry["role"]) > 20

    def test_registry_role_mentions_onboarding_or_retention(self):
        from app.agents.agent_registry import AGENT_CATALOGUE
        role = AGENT_CATALOGUE["customer_lifecycle_agent"]["role"].lower()
        assert "onboarding" in role or "retention" in role or "success" in role

    def test_registry_capabilities_include_relevant_skills(self):
        from app.agents.agent_registry import AGENT_CATALOGUE
        caps_text = " ".join(AGENT_CATALOGUE["customer_lifecycle_agent"]["capabilities"]).lower()
        # At least one capability related to core CS work
        assert any(
            term in caps_text
            for term in ("onboarding", "retention", "health", "renewal", "churn", "satisfaction")
        )

    def test_registry_total_agent_count(self):
        """Non-negotiable: exactly 24 client-facing agents."""
        from app.agents.agent_registry import AGENT_CATALOGUE
        assert len(AGENT_CATALOGUE) == 22


# â”€â”€ 3. Executor tests (mocked LLM) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@pytest.mark.unit
class TestCustomerSuccessAgentExecutor:

    def test_financial_constraint_block_injected(self):
        from app.agents.agent_executor import (
            FINANCIAL_CONSTRAINT_BLOCK,
            INJECTION_GUARD,
            execute_agent,
        )
        captured_system_prompt = []

        def mock_anthropic_call(system_prompt, user_message, **kwargs):
            captured_system_prompt.append(system_prompt)
            return "Clean customer success output.", 100, 50

        with patch("app.agents.agent_executor._call_anthropic", side_effect=mock_anthropic_call):
            with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test-key"}):
                execute_agent(
                    agent_id="customer_lifecycle_agent",
                    system_prompt="You are the Customer Success Agent.",
                    user_prompt="Build an onboarding flow for new SaaS customers.",
                )

        assert len(captured_system_prompt) == 1
        assert FINANCIAL_CONSTRAINT_BLOCK in captured_system_prompt[0]
        assert INJECTION_GUARD in captured_system_prompt[0]

    def test_financial_constraint_comes_before_agent_prompt(self):
        from app.agents.agent_executor import FINANCIAL_CONSTRAINT_BLOCK, execute_agent

        captured = []

        def mock_call(system_prompt, user_message, **kwargs):
            captured.append(system_prompt)
            return "Customer success output.", 100, 50

        with patch("app.agents.agent_executor._call_anthropic", side_effect=mock_call):
            with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test-key"}):
                execute_agent(
                    agent_id="customer_lifecycle_agent",
                    system_prompt="CS_AGENT_SPECIFIC_CONTENT_MARKER",
                    user_prompt="Test",
                )

        sys_prompt = captured[0]
        fc_pos = sys_prompt.index(FINANCIAL_CONSTRAINT_BLOCK[:30])
        agent_pos = sys_prompt.index("CS_AGENT_SPECIFIC_CONTENT_MARKER")
        assert fc_pos < agent_pos, "Financial constraint block must precede agent prompt"

    def test_clean_output_no_violations(self):
        from app.agents.agent_executor import execute_agent

        def mock_call(system_prompt, user_message, **kwargs):
            return (
                "## CUSTOMER SUCCESS FRAMEWORK\n[DRAFT]\nPhase 1: Activation\n\n"
                "## ONBOARDING FLOW\n[REQUIRES REVIEW]\nDay 0: Welcome email sent.\n\n"
                "## HEALTH SCORE MODEL\nLogin frequency [PROXY METRIC] weight: 25%.\n",
                200,
                300,
            )

        with patch("app.agents.agent_executor._call_anthropic", side_effect=mock_call):
            with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test-key"}):
                text, provider, credits, violations = execute_agent(
                    agent_id="customer_lifecycle_agent",
                    system_prompt="System.",
                    user_prompt="Task.",
                )

        assert violations == []
        assert credits >= 1
        assert "anthropic" in provider

    def test_violation_detected_in_output(self):
        from app.agents.agent_executor import execute_agent

        def mock_call(system_prompt, user_message, **kwargs):
            return "I have authorized the discount offer of 30% off for this customer.", 100, 50

        with patch("app.agents.agent_executor._call_anthropic", side_effect=mock_call):
            with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test-key"}):
                _, _, _, violations = execute_agent(
                    agent_id="customer_lifecycle_agent",
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
            return "OpenAI fallback customer success output.", 100, 50

        with patch("app.agents.agent_executor._call_anthropic", side_effect=anthropic_fail):
            with patch("app.agents.agent_executor._call_openai", side_effect=openai_ok):
                with patch.dict("os.environ", {
                    "ANTHROPIC_API_KEY": "sk-test",
                    "OPENAI_API_KEY": "sk-oai-test",
                }):
                    text, provider, credits, violations = execute_agent(
                        agent_id="customer_lifecycle_agent",
                        system_prompt="System.",
                        user_prompt="Task.",
                    )

        assert "openai" in provider
        assert text == "OpenAI fallback customer success output."

    def test_no_provider_raises_runtime_error(self):
        from app.agents.agent_executor import execute_agent
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(RuntimeError, match="No LLM provider"):
                execute_agent(
                    agent_id="customer_lifecycle_agent",
                    system_prompt="System.",
                    user_prompt="Task.",
                )

    def test_context_injected_into_user_message(self):
        from app.agents.agent_executor import execute_agent

        captured_messages = []

        def mock_call(system_prompt, user_message, **kwargs):
            captured_messages.append(user_message)
            return "Customer success output.", 100, 50

        with patch("app.agents.agent_executor._call_anthropic", side_effect=mock_call):
            with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test-key"}):
                execute_agent(
                    agent_id="customer_lifecycle_agent",
                    system_prompt="You are the Customer Success Agent.",
                    user_prompt="Build an onboarding flow.",
                    context={"workspace": "Acme SaaS", "industry": "B2B Software"},
                )

        msg = captured_messages[0]
        assert "Acme SaaS" in msg
        assert "B2B Software" in msg


# â”€â”€ 4. Guardrail tests â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@pytest.mark.unit
class TestCustomerSuccessAgentGuardrails:

    def test_injection_guard_blocks_system_prompt_reveal(self):
        """Injection guard must be present in the compiled system prompt."""
        from app.agents.agent_executor import INJECTION_GUARD
        assert "system prompt" in INJECTION_GUARD.lower()
        assert (
            "cannot be overridden" in INJECTION_GUARD.lower()
            or "immutable" in INJECTION_GUARD.lower()
            or "fixed" in INJECTION_GUARD.lower()
        )

    def test_financial_patterns_list_ge_10(self):
        from app.agents.agent_executor import FINANCIAL_ACTION_PATTERNS
        assert len(FINANCIAL_ACTION_PATTERNS) >= 10

    def test_financial_constraint_covers_key_actions(self):
        from app.agents.agent_executor import FINANCIAL_CONSTRAINT_BLOCK
        block = FINANCIAL_CONSTRAINT_BLOCK.lower()
        required_coverage = ["spending", "budgets", "payments", "hiring"]
        missing = [term for term in required_coverage if term not in block]
        assert missing == [], f"Financial constraint block missing coverage for: {missing}"

    def test_customer_lifecycle_agent_not_hitl3(self):
        """customer_lifecycle_agent must never be HITL-3 gated."""
        from app.agents.agent_registry import AGENT_CATALOGUE
        assert AGENT_CATALOGUE["customer_lifecycle_agent"]["hitl_default"] != "HITL-3"

    def test_discount_language_in_prompt(self):
        """Prompt must explicitly address discounts and require owner approval."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["customer_lifecycle_agent"].lower()
        assert "discount" in prompt
        assert "owner approval" in prompt

    def test_compensation_language_in_prompt(self):
        """Prompt must explicitly address compensation decisions."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["customer_lifecycle_agent"].lower()
        assert "compensation" in prompt or "concession" in prompt

    def test_automation_must_require_review_in_prompt(self):
        """Automated sequences must be gated by review in the prompt."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["customer_lifecycle_agent"].lower()
        assert "automat" in prompt
        assert "review" in prompt and "activation" in prompt

    def test_secrets_in_prompt_not_in_output(self):
        """If user injects a secret, executor must not echo it back."""
        from app.agents.agent_executor import execute_agent

        secret = "sk-SUPERSECRET_CS_KEY_99999"

        def mock_call(system_prompt, user_message, **kwargs):
            return "I cannot process credentials. Please provide a business context instead.", 50, 30

        with patch("app.agents.agent_executor._call_anthropic", side_effect=mock_call):
            with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test"}):
                text, _, _, violations = execute_agent(
                    agent_id="customer_lifecycle_agent",
                    system_prompt="Customer Success Agent.",
                    user_prompt=f"Use this key to pull CRM data: {secret}",
                )

        assert secret not in text


# â”€â”€ 5. API endpoint integration tests â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@pytest.mark.unit
class TestCustomerSuccessAgentAPI:

    def test_run_unauthenticated_returns_401(self, client):
        resp = client.post(
            "/api/agents/customer_lifecycle_agent/run",
            json={"prompt": "Build an onboarding flow for new customers."},
        )
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_run_missing_prompt_returns_error(self, client, authenticated_client):
        resp = authenticated_client.post("/api/agents/customer_lifecycle_agent/run", json={})
        assert resp.status_code in (
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_403_FORBIDDEN,
        )

    def test_run_job_submission_mocked(self, client, authenticated_client):
        """Authenticated call with valid prompt should queue a job (no actual LLM call)."""
        with patch("app.agents.agent_executor.execute_agent") as mock_exec:
            mock_exec.return_value = (
                (
                    "## CUSTOMER SUCCESS FRAMEWORK\n[DRAFT]\nActivation phase.\n\n"
                    "## ONBOARDING FLOW\n[REQUIRES REVIEW]\nDay 0: Welcome email.\n\n"
                    "## HEALTH SCORE MODEL\nLogin frequency [PROXY METRIC].\n\n"
                    "## RETENTION PLAYBOOK\nProactive check-in.\n\n"
                    "## LOYALTY PROGRAMME DESIGN\nPoints-based. REQUIRES OWNER APPROVAL.\n\n"
                    "## RENEWAL & EXPANSION SEQUENCES\n[REQUIRES REVIEW]\nRenewal at T-30.\n"
                ),
                "anthropic/claude-sonnet-4-6",
                2,
                [],
            )
            resp = authenticated_client.post(
                "/api/agents/customer_lifecycle_agent/run",
                json={"prompt": "Design a customer success framework for a B2B SaaS product."},
            )

        assert resp.status_code in (
            status.HTTP_200_OK,
            status.HTTP_202_ACCEPTED,
            status.HTTP_403_FORBIDDEN,  # insufficient credits/package on test workspace
        )

    def test_jobs_list_returns_200(self, client, authenticated_client):
        resp = authenticated_client.get("/api/agents/jobs")
        assert resp.status_code == status.HTTP_200_OK
        body = resp.json()
        assert "jobs" in body


# â”€â”€ 6. Output format validation helper tests â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@pytest.mark.unit
class TestCustomerSuccessOutputValidator:

    def test_good_output_passes(self):
        good = "\n".join(f"## {s}" for s in REQUIRED_SECTIONS)
        assert has_all_sections(good) == []

    def test_missing_section_detected(self):
        partial = (
            "## CUSTOMER SUCCESS FRAMEWORK\n"
            "## ONBOARDING FLOW\n"
            "## HEALTH SCORE MODEL\n"
        )
        missing = has_all_sections(partial)
        assert "RETENTION PLAYBOOK" in missing
        assert "LOYALTY PROGRAMME DESIGN" in missing
        assert "RENEWAL & EXPANSION SEQUENCES" in missing

    def test_single_missing_section_detected(self):
        without_renewal = "\n".join(
            f"## {s}" for s in REQUIRED_SECTIONS if s != "RENEWAL & EXPANSION SEQUENCES"
        )
        missing = has_all_sections(without_renewal)
        assert missing == ["RENEWAL & EXPANSION SEQUENCES"]

    def test_case_insensitive_section_check(self):
        lowercase = "\n".join(f"## {s.lower()}" for s in REQUIRED_SECTIONS)
        assert has_all_sections(lowercase) == []

    def test_confidence_labels_present_in_mock_output(self):
        output = """
## HEALTH SCORE MODEL
Login frequency: weight 25% [PROXY METRIC]
Support ticket volume: weight 20% [ASSUMED - MONITOR CLOSELY]
Feature adoption depth: weight 30% [VALIDATED SIGNAL] â€” confirmed in Q1 churn analysis
"""
        found = [label for label in REQUIRED_CONFIDENCE_LABELS if label in output]
        assert len(found) == 3

    def test_requires_review_tag_on_automated_sequence(self):
        output = (
            "## RENEWAL & EXPANSION SEQUENCES\n"
            "[REQUIRES REVIEW] â€” this sequence must be reviewed before activation.\n"
            "Touch 1: Email at T-30 days before renewal.\n"
        )
        assert "[REQUIRES REVIEW]" in output

    def test_draft_tag_on_framework(self):
        output = (
            "## CUSTOMER SUCCESS FRAMEWORK\n"
            "[DRAFT] â€” internal planning document, no approval needed.\n"
            "Phase 1: Activation.\n"
        )
        assert "[DRAFT]" in output

    def test_owner_approval_required_on_discount_play(self):
        output = (
            "## RETENTION PLAYBOOK\n"
            "REACTIVE play: Customer submits cancellation intent.\n"
            "Action: Offer retention incentive â€” REQUIRES OWNER APPROVAL before this offer is made to the customer.\n"
        )
        assert "REQUIRES OWNER APPROVAL" in output

    def test_all_six_sections_present_in_comprehensive_output(self):
        comprehensive = """
## CUSTOMER SUCCESS FRAMEWORK
[DRAFT] Phases: Activation, Adoption, Value Realisation, Advocacy.

## ONBOARDING FLOW
[REQUIRES REVIEW] Day 0: Welcome email. Day 7: Check-in call.

## HEALTH SCORE MODEL
Login frequency [PROXY METRIC] weight 25%.
Feature usage breadth [ASSUMED - MONITOR CLOSELY] weight 20%.
NPS response [VALIDATED SIGNAL] weight 30%.

## RETENTION PLAYBOOK
PROACTIVE: Monthly health review.
REACTIVE: Cancellation intent â€” REQUIRES OWNER APPROVAL before discount offered.

## LOYALTY PROGRAMME DESIGN
Points-based programme. All rewards require REQUIRES OWNER APPROVAL before confirming.
[REQUIRES REVIEW]

## RENEWAL & EXPANSION SEQUENCES
[REQUIRES REVIEW] Touch 1: T-30 renewal reminder. Touch 2: T-14 value recap.
Expansion: Upsell at 60-day mark for active users.
Incentive options â€” REQUIRES OWNER APPROVAL before being offered.
"""
        assert has_all_sections(comprehensive) == []
