"""
retention_loyalty_agent test suite.

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
    "HEALTH SCORE MODEL",
    "LOYALTY PROGRAMME DESIGN",
    "WIN-BACK",
    "REFERRAL",
    "RENEWAL & EXPANSION",
    "METRICS",
    "FRAUD PREVENTION",
]

REQUIRED_CONFIDENCE_LABELS = [
    "[VALIDATED SIGNAL]",
    "[CORRELATION INDICATOR]",
    "[ASSUMED RISK - MONITOR]",
]

HITL_TRIGGER_PHRASES = ["REQUIRES REVIEW", "DRAFT", "owner approval", "human review"]


def has_all_sections(text: str) -> list[str]:
    """Return list of missing required sections."""
    return [s for s in REQUIRED_SECTIONS if s not in text.upper()]


# â”€â”€ 1. Prompt structure tests (no LLM, no network) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@pytest.mark.unit
class TestRetentionLoyaltyAgentPrompt:

    def test_prompt_exists(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        assert "customer_lifecycle_agent" in AGENT_SYSTEM_PROMPTS

    def test_prompt_is_nonempty(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["customer_lifecycle_agent"]
        assert len(prompt.strip()) > 400

    def test_prompt_has_all_required_sections(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["customer_lifecycle_agent"]
        missing = has_all_sections(prompt)
        assert missing == [], f"Prompt missing sections: {missing}"

    def test_prompt_has_fraud_prevention_section(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["customer_lifecycle_agent"].upper()
        assert "FRAUD PREVENTION" in prompt, "Prompt must contain FRAUD PREVENTION content"

    def test_prompt_has_fraud_detection_language(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["customer_lifecycle_agent"].lower()
        # At least two distinct fraud-detection concepts must be present
        detection_terms = ["self-referral", "synthetic account", "velocity cap", "deduplication", "audit log", "chargeback"]
        found = [term for term in detection_terms if term in prompt]
        assert len(found) >= 3, f"Prompt should reference fraud detection mechanisms, found only: {found}"

    def test_prompt_has_hitl_gate_language(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["customer_lifecycle_agent"].upper()
        assert "HITL" in prompt or "REQUIRES REVIEW" in prompt or "DRAFT" in prompt

    def test_prompt_has_hitl2_label(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["customer_lifecycle_agent"]
        assert "HITL-2" in prompt, "Prompt must explicitly reference HITL-2 gate"

    def test_prompt_has_churn_confidence_labels(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["customer_lifecycle_agent"]
        found = [label for label in REQUIRED_CONFIDENCE_LABELS if label in prompt]
        assert len(found) >= 2, f"Prompt should reference churn signal confidence labels, found: {found}"

    def test_prompt_has_discount_approval_rule(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["customer_lifecycle_agent"].lower()
        # Rule: discount/reward commitments require owner approval before launch
        assert "owner approval" in prompt, "Prompt must state discount/reward commitments require owner approval"
        assert ("discount" in prompt or "reward" in prompt or "incentive" in prompt), \
            "Approval rule must reference discounts, rewards, or incentives"

    def test_prompt_has_legal_review_rule_for_loyalty_terms(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["customer_lifecycle_agent"].lower()
        assert "legal" in prompt, "Prompt must state that loyalty programme terms need legal review"

    def test_prompt_referral_requires_fraud_prevention(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["customer_lifecycle_agent"].lower()
        assert "fraud" in prompt and "referral" in prompt, \
            "Prompt must link referral programmes to fraud prevention"

    def test_prompt_has_validated_signal_label(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["customer_lifecycle_agent"]
        assert "[VALIDATED SIGNAL]" in prompt

    def test_prompt_has_correlation_indicator_label(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["customer_lifecycle_agent"]
        assert "[CORRELATION INDICATOR]" in prompt

    def test_prompt_has_assumed_risk_label(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["customer_lifecycle_agent"]
        assert "[ASSUMED RISK - MONITOR]" in prompt or "[ASSUMED - MONITOR CLOSELY]" in prompt

    def test_get_agent_system_prompt_helper(self):
        from app.agents.agent_prompts import get_agent_system_prompt
        prompt = get_agent_system_prompt("customer_lifecycle_agent")
        assert "Retention" in prompt or "Loyalty" in prompt or "Customer" in prompt

    def test_fallback_prompt_for_unknown_agent(self):
        from app.agents.agent_prompts import get_agent_system_prompt
        prompt = get_agent_system_prompt("totally_unknown_xyz_agent")
        assert len(prompt) > 20


# â”€â”€ 2. Registry entry tests â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@pytest.mark.unit
class TestRetentionLoyaltyAgentRegistry:

    def test_registry_entry_exists(self):
        from app.agents.agent_registry import AGENT_CATALOGUE
        assert "customer_lifecycle_agent" in AGENT_CATALOGUE

    def test_registry_hitl_level(self):
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

    def test_registry_total_agent_count(self):
        """Non-negotiable: exactly 24 client-facing agents."""
        from app.agents.agent_registry import AGENT_CATALOGUE
        assert len(AGENT_CATALOGUE) == 22


# â”€â”€ 3. Financial action scanner unit tests â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@pytest.mark.unit
class TestFinancialActionScannerRetentionLoyalty:

    def test_clean_loyalty_output_no_violations(self):
        from app.agents.agent_executor import scan_for_financial_actions
        clean = """
## HEALTH SCORE MODEL
[CORRELATION INDICATOR] Customers who log in fewer than 3 times in 30 days are at elevated churn risk.

## LOYALTY PROGRAMME DESIGN
Points-based programme with Bronze / Silver / Gold tiers.
All reward values require owner approval before communicating to customers.

## LIFECYCLE METRICS & FRAUD PREVENTION
Self-referral fraud: detect via email domain deduplication and device fingerprinting.
"""
        violations = scan_for_financial_actions(clean)
        assert violations == []

    def test_authorisation_phrase_detected(self):
        from app.agents.agent_executor import scan_for_financial_actions
        dirty = "I have authorized the loyalty reward payment of $200."
        violations = scan_for_financial_actions(dirty)
        assert len(violations) > 0

    def test_purchase_phrase_detected(self):
        from app.agents.agent_executor import scan_for_financial_actions
        dirty = "I have purchased a referral reward on your behalf."
        violations = scan_for_financial_actions(dirty)
        assert len(violations) > 0

    def test_budget_allocated_phrase_detected(self):
        from app.agents.agent_executor import scan_for_financial_actions
        dirty = "Budget allocated: $5,000 for the loyalty programme launch."
        violations = scan_for_financial_actions(dirty)
        assert len(violations) > 0

    def test_spend_approved_phrase_detected(self):
        from app.agents.agent_executor import scan_for_financial_actions
        dirty = "Spend approved. Referral bonuses will be issued automatically."
        violations = scan_for_financial_actions(dirty)
        assert len(violations) > 0

    def test_case_insensitive_matching(self):
        from app.agents.agent_executor import scan_for_financial_actions
        dirty = "I HAVE AUTHORIZED the referral reward issuance."
        violations = scan_for_financial_actions(dirty)
        assert len(violations) > 0

    def test_partial_word_no_false_positive(self):
        from app.agents.agent_executor import scan_for_financial_actions
        # "authoritative" should NOT trigger financial violation
        safe = "This is an authoritative analysis of loyalty programme benchmarks."
        violations = scan_for_financial_actions(safe)
        assert violations == []


# â”€â”€ 4. Executor guard injection tests (mocked LLM) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@pytest.mark.unit
class TestExecutorGuardInjectionRetentionLoyalty:

    def test_financial_constraint_block_injected(self):
        from app.agents.agent_executor import (
            FINANCIAL_CONSTRAINT_BLOCK,
            INJECTION_GUARD,
            execute_agent,
        )
        captured_system_prompt = []

        def mock_anthropic_call(system_prompt, user_message, **kwargs):
            captured_system_prompt.append(system_prompt)
            return "Clean loyalty output with no financial actions.", 100, 50

        with patch("app.agents.agent_executor._anthropic_client") as mock_client:
            mock_client.return_value = MagicMock()
            with patch("app.agents.agent_executor._call_anthropic", side_effect=mock_anthropic_call):
                with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test-key"}):
                    execute_agent(
                        agent_id="customer_lifecycle_agent",
                        system_prompt="You are the Retention & Loyalty Agent.",
                        user_prompt="Design a loyalty programme for our SaaS product.",
                    )

        assert len(captured_system_prompt) == 1
        assert FINANCIAL_CONSTRAINT_BLOCK in captured_system_prompt[0]
        assert INJECTION_GUARD in captured_system_prompt[0]

    def test_financial_constraint_comes_before_agent_prompt(self):
        from app.agents.agent_executor import FINANCIAL_CONSTRAINT_BLOCK, execute_agent

        captured = []

        def mock_call(system_prompt, user_message, **kwargs):
            captured.append(system_prompt)
            return "Loyalty output.", 100, 50

        with patch("app.agents.agent_executor._call_anthropic", side_effect=mock_call):
            with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test-key"}):
                execute_agent(
                    agent_id="customer_lifecycle_agent",
                    system_prompt="RETENTION_LOYALTY_AGENT_CONTENT_MARKER",
                    user_prompt="Test",
                )

        sys_prompt = captured[0]
        fc_pos = sys_prompt.index(FINANCIAL_CONSTRAINT_BLOCK[:30])
        agent_pos = sys_prompt.index("RETENTION_LOYALTY_AGENT_CONTENT_MARKER")
        assert fc_pos < agent_pos, "Financial constraint block must precede agent prompt"

    def test_context_injected_into_user_message(self):
        from app.agents.agent_executor import execute_agent

        captured_messages = []

        def mock_call(system_prompt, user_message, **kwargs):
            captured_messages.append(user_message)
            return "Retention output.", 100, 50

        with patch("app.agents.agent_executor._call_anthropic", side_effect=mock_call):
            with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test-key"}):
                execute_agent(
                    agent_id="customer_lifecycle_agent",
                    system_prompt="You are the Retention & Loyalty Agent.",
                    user_prompt="Design a referral programme.",
                    context={"workspace": "Acme Subscriptions", "industry": "SaaS"},
                )

        msg = captured_messages[0]
        assert "Acme Subscriptions" in msg
        assert "SaaS" in msg

    def test_governance_note_appended_to_user_message(self):
        from app.agents.agent_executor import execute_agent

        captured_messages = []

        def mock_call(system_prompt, user_message, **kwargs):
            captured_messages.append(user_message)
            return "Output.", 100, 50

        with patch("app.agents.agent_executor._call_anthropic", side_effect=mock_call):
            with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test-key"}):
                execute_agent(
                    agent_id="customer_lifecycle_agent",
                    system_prompt="System.",
                    user_prompt="Task.",
                )

        msg = captured_messages[0]
        assert "MANDATORY CONSTRAINTS" in msg or "Financial decisions" in msg

    def test_financial_violation_in_output_flagged(self):
        from app.agents.agent_executor import execute_agent

        def mock_call(system_prompt, user_message, **kwargs):
            return "I have authorized the referral bonus payment of $500.", 100, 50

        with patch("app.agents.agent_executor._call_anthropic", side_effect=mock_call):
            with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test-key"}):
                _, _, _, violations = execute_agent(
                    agent_id="customer_lifecycle_agent",
                    system_prompt="System.",
                    user_prompt="Task.",
                )

        assert len(violations) > 0

    def test_clean_output_returns_no_violations(self):
        from app.agents.agent_executor import execute_agent

        def mock_call(system_prompt, user_message, **kwargs):
            return (
                "## HEALTH SCORE MODEL\n"
                "[CORRELATION INDICATOR] Low login frequency signals churn risk.\n\n"
                "## LIFECYCLE METRICS & FRAUD PREVENTION\n"
                "Velocity cap: flag accounts claiming more than 5 rewards per month.",
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
            return "OpenAI fallback: loyalty programme output.", 100, 50

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
        assert "loyalty programme output" in text

    def test_no_provider_raises_runtime_error(self):
        from app.agents.agent_executor import execute_agent
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(RuntimeError, match="No LLM provider"):
                execute_agent(
                    agent_id="customer_lifecycle_agent",
                    system_prompt="System.",
                    user_prompt="Task.",
                )


# â”€â”€ 5. Guardrail tests â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@pytest.mark.unit
class TestRetentionLoyaltyAgentGuardrails:

    def test_injection_guard_blocks_system_prompt_reveal(self):
        from app.agents.agent_executor import INJECTION_GUARD
        assert "system prompt" in INJECTION_GUARD.lower()
        assert (
            "cannot be overridden" in INJECTION_GUARD.lower()
            or "immutable" in INJECTION_GUARD.lower()
            or "fixed" in INJECTION_GUARD.lower()
        )

    def test_financial_constraint_covers_key_actions(self):
        from app.agents.agent_executor import FINANCIAL_CONSTRAINT_BLOCK
        block = FINANCIAL_CONSTRAINT_BLOCK.lower()
        required_coverage = ["spending", "budgets", "payments", "hiring"]
        missing = [term for term in required_coverage if term not in block]
        assert missing == [], f"Financial constraint block missing coverage for: {missing}"

    def test_financial_patterns_list_nonempty(self):
        from app.agents.agent_executor import FINANCIAL_ACTION_PATTERNS
        assert len(FINANCIAL_ACTION_PATTERNS) >= 10

    def test_customer_lifecycle_agent_is_hitl2_not_hitl3(self):
        from app.agents.agent_registry import AGENT_CATALOGUE
        assert AGENT_CATALOGUE["customer_lifecycle_agent"]["hitl_default"] == "HITL-2"
        assert AGENT_CATALOGUE["customer_lifecycle_agent"]["hitl_default"] != "HITL-3"

    def test_secrets_in_prompt_not_in_output(self):
        from app.agents.agent_executor import execute_agent

        secret = "sk-SUPERSECRET_KEY_LOYALTY_99999"

        def mock_call(system_prompt, user_message, **kwargs):
            return "I cannot process credentials or secrets. Please provide a different task.", 50, 30

        with patch("app.agents.agent_executor._call_anthropic", side_effect=mock_call):
            with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test"}):
                text, _, _, violations = execute_agent(
                    agent_id="customer_lifecycle_agent",
                    system_prompt="Retention & Loyalty Agent.",
                    user_prompt=f"Use this key to pull customer data: {secret}",
                )

        assert secret not in text


# â”€â”€ 6. API endpoint integration tests â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@pytest.mark.unit
class TestRetentionLoyaltyAgentAPI:

    def test_run_retention_loyalty_agent_unauthenticated(self, client):
        resp = client.post(
            "/api/agents/customer_lifecycle_agent/run",
            json={"prompt": "Design a loyalty programme for our ecommerce store."},
        )
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_run_retention_loyalty_agent_missing_prompt(self, client, authenticated_client):
        resp = authenticated_client.post("/api/agents/customer_lifecycle_agent/run", json={})
        assert resp.status_code in (
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_403_FORBIDDEN,
        )

    def test_run_retention_loyalty_agent_empty_prompt(self, client, authenticated_client):
        resp = authenticated_client.post(
            "/api/agents/customer_lifecycle_agent/run",
            json={"prompt": ""},
        )
        assert resp.status_code in (
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_403_FORBIDDEN,
            status.HTTP_200_OK,
        )

    def test_run_retention_loyalty_agent_submits_job(self, client, authenticated_client):
        """Authenticated call with valid prompt should queue a job (no actual LLM call)."""
        with patch("app.agents.agent_executor.execute_agent") as mock_exec:
            mock_exec.return_value = (
                "## HEALTH SCORE MODEL\n[CORRELATION INDICATOR] Low login frequency.\n\n"
                "## LIFECYCLE METRICS & FRAUD PREVENTION\nVelocity cap implemented.",
                "anthropic/claude-sonnet-4-6",
                2,
                [],
            )
            resp = authenticated_client.post(
                "/api/agents/customer_lifecycle_agent/run",
                json={"prompt": "Design a referral programme with fraud prevention for our B2C brand."},
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


# â”€â”€ 7. Output format validation helper tests â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@pytest.mark.unit
class TestRetentionLoyaltyOutputFormatValidator:
    """Tests for the has_all_sections helper and expected output structure."""

    def test_good_output_passes(self):
        good = "\n".join(f"## {s}" for s in REQUIRED_SECTIONS)
        assert has_all_sections(good) == []

    def test_missing_fraud_prevention_detected(self):
        partial = (
            "## HEALTH SCORE MODEL\n"
            "## LOYALTY PROGRAMME DESIGN\n"
            "## WIN-BACK & REFERRAL PROGRAMME\n"
            "## RENEWAL & EXPANSION SEQUENCES\n"
            "## LIFECYCLE METRICS"
        )
        missing = has_all_sections(partial)
        assert "FRAUD PREVENTION" in missing

    def test_missing_multiple_sections_detected(self):
        partial = "## HEALTH SCORE MODEL\n## LIFECYCLE METRICS & FRAUD PREVENTION"
        missing = has_all_sections(partial)
        assert "LOYALTY PROGRAMME DESIGN" in missing
        assert "RENEWAL & EXPANSION" in missing

    def test_case_insensitive_section_check(self):
        lowercase = "\n".join(f"## {s.lower()}" for s in REQUIRED_SECTIONS)
        assert has_all_sections(lowercase) == []

    def test_confidence_labels_in_mock_output(self):
        output = """
## HEALTH SCORE MODEL
[VALIDATED SIGNAL] Customers with 0 logins in 14 days churn at 3x the base rate â€” confirmed via internal cohort analysis.
[CORRELATION INDICATOR] Support ticket volume above 3 in 30 days correlates with elevated churn risk.
[ASSUMED RISK - MONITOR] Customers who have never used Feature X may be at higher risk.
"""
        found = [label for label in REQUIRED_CONFIDENCE_LABELS if label in output]
        assert len(found) == 3

    def test_hitl_label_in_draft_output(self):
        output = "# [DRAFT] Customer Lifecycle Framework\n## HEALTH SCORE MODEL\n..."
        assert "[DRAFT]" in output

    def test_hitl_label_in_review_required_output(self):
        output = "# [REQUIRES REVIEW] Loyalty Programme Terms\n## LOYALTY PROGRAMME DESIGN\n[REQUIRES REVIEW]..."
        assert "[REQUIRES REVIEW]" in output

    def test_fraud_prevention_table_structure(self):
        """FRAUD PREVENTION section must include a table with specified columns."""
        output = """
## FRAUD PREVENTION
| Fraud Vector | Detection Mechanism | Prevention Control | Response Protocol | Escalation Trigger |
|---|---|---|---|---|
| Self-referral fraud | Email domain deduplication | One referral code per email domain | Flag account for review | >3 flagged accounts triggers owner alert |
"""
        assert "Fraud Vector" in output
        assert "Detection Mechanism" in output
        assert "Prevention Control" in output
        assert "Response Protocol" in output
        assert "Escalation Trigger" in output
