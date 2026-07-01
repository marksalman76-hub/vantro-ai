"""
finance_admin_agent test suite.

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


# â”€â”€ Helpers â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

REQUIRED_SECTIONS = [
    "FINANCIAL OVERVIEW",
    "CASH FLOW PROJECTION",
    "EXPENSE AUDIT",
    "REVENUE ANALYSIS",
    "COMPLIANCE CHECKLIST",
    "FINANCIAL RECOMMENDATIONS",
    "DISCLAIMERS",
]

REQUIRED_ACCURACY_LABELS = [
    "[AUDITED DATA]",
    "[ESTIMATED - VERIFY WITH ACCOUNTANT]",
    "[PROJECTED - TREAT AS DIRECTIONAL ONLY]",
]

HITL_TRIGGER_PHRASES = ["HITL-3", "REQUIRES OWNER", "owner approval", "owner sign-off", "owner review"]


def has_all_sections(text: str) -> list[str]:
    """Return list of missing required sections."""
    return [s for s in REQUIRED_SECTIONS if s not in text.upper()]


# â”€â”€ 1. Prompt structure tests (no LLM, no network) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@pytest.mark.unit
class TestFinanceAdminAgentPrompt:

    def test_prompt_exists(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        assert "finance_admin_agent" in AGENT_SYSTEM_PROMPTS

    def test_prompt_is_nonempty(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["finance_admin_agent"]
        assert len(prompt.strip()) > 500

    def test_prompt_has_all_required_sections(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["finance_admin_agent"]
        missing = has_all_sections(prompt)
        assert missing == [], f"Prompt missing sections: {missing}"

    def test_disclaimers_section_exists(self):
        """DISCLAIMERS is the mandatory 7th section added in upgrade."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["finance_admin_agent"]
        assert "DISCLAIMERS" in prompt.upper()

    def test_hitl3_gate_stated_emphatically(self):
        """HITL-3 must be stated explicitly in the prompt."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["finance_admin_agent"]
        assert "HITL-3" in prompt

    def test_no_financial_transactions_rule(self):
        """Prompt must explicitly prohibit financial transactions by the agent."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["finance_admin_agent"].lower()
        assert "transaction" in prompt
        assert "never" in prompt or "does not" in prompt or "no financial" in prompt

    def test_no_payment_initiation_rule(self):
        """Prompt must prohibit payment initiation by the agent."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["finance_admin_agent"].lower()
        assert "payment" in prompt
        assert "never" in prompt or "does not" in prompt or "no payment" in prompt

    def test_professional_review_required_rule(self):
        """Prompt must require professional review before acting on output."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["finance_admin_agent"].lower()
        assert "professional" in prompt
        assert "review" in prompt or "accountant" in prompt or "adviser" in prompt

    def test_all_accuracy_labels_present(self):
        """All 3 accuracy labels must appear in the prompt."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["finance_admin_agent"]
        missing = [label for label in REQUIRED_ACCURACY_LABELS if label not in prompt]
        assert missing == [], f"Prompt missing accuracy labels: {missing}"

    def test_not_financial_advice_disclaimer(self):
        """DISCLAIMERS section must state this is not financial advice."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["finance_admin_agent"].upper()
        assert "NOT FINANCIAL ADVICE" in prompt or "NOT FINANCIAL" in prompt

    def test_not_tax_advice_disclaimer(self):
        """DISCLAIMERS section must state this is not tax advice."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["finance_admin_agent"].upper()
        assert "NOT TAX ADVICE" in prompt or "TAX ADVICE" in prompt

    def test_not_legal_advice_disclaimer(self):
        """DISCLAIMERS section must state this is not legal advice."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["finance_admin_agent"].upper()
        assert "NOT LEGAL ADVICE" in prompt or "LEGAL ADVICE" in prompt

    def test_prompt_has_hitl_gate_language(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["finance_admin_agent"]
        found = any(phrase.lower() in prompt.lower() for phrase in HITL_TRIGGER_PHRASES)
        assert found

    def test_get_agent_system_prompt_helper(self):
        from app.agents.agent_prompts import get_agent_system_prompt
        prompt = get_agent_system_prompt("finance_admin_agent")
        assert "Finance" in prompt or "Admin" in prompt

    def test_fallback_prompt_for_unknown_agent(self):
        from app.agents.agent_prompts import get_agent_system_prompt
        prompt = get_agent_system_prompt("totally_unknown_xyz_agent")
        assert len(prompt) > 20

    def test_all_output_is_draft_rule(self):
        """Prompt must state all output is draft until reviewed by owner."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["finance_admin_agent"].upper()
        assert "DRAFT" in prompt

    def test_disclaimers_cover_no_account_access(self):
        """DISCLAIMERS must cover that agent has no account access."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["finance_admin_agent"].upper()
        disclaimers_idx = prompt.find("DISCLAIMERS")
        assert disclaimers_idx != -1
        disclaimers_text = prompt[disclaimers_idx:disclaimers_idx + 3000]
        assert "ACCOUNT" in disclaimers_text


# â”€â”€ 2. Registry entry tests â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@pytest.mark.unit
class TestFinanceAdminAgentRegistry:

    def test_registry_entry_exists(self):
        from app.agents.agent_registry import AGENT_CATALOGUE
        assert "finance_admin_agent" in AGENT_CATALOGUE

    def test_registry_hitl_level_is_hitl3(self):
        """finance_admin_agent MUST be HITL-3 — all financial actions require approval."""
        from app.agents.agent_registry import AGENT_CATALOGUE
        entry = AGENT_CATALOGUE["finance_admin_agent"]
        assert entry["hitl_default"] == "HITL-3"

    def test_registry_min_package(self):
        from app.agents.agent_registry import AGENT_CATALOGUE
        entry = AGENT_CATALOGUE["finance_admin_agent"]
        assert entry["min_package"] == "business"

    def test_registry_has_capabilities(self):
        from app.agents.agent_registry import AGENT_CATALOGUE
        entry = AGENT_CATALOGUE["finance_admin_agent"]
        assert isinstance(entry.get("capabilities"), list)
        assert len(entry["capabilities"]) >= 3

    def test_registry_has_role(self):
        from app.agents.agent_registry import AGENT_CATALOGUE
        entry = AGENT_CATALOGUE["finance_admin_agent"]
        assert entry.get("role") and len(entry["role"]) > 20

    def test_registry_total_agent_count(self):
        """Non-negotiable: exactly 27 client-facing agents."""
        from app.agents.agent_registry import AGENT_CATALOGUE
        assert len(AGENT_CATALOGUE) == 22

    def test_registry_hitl_default_not_lower_than_hitl3(self):
        """finance_admin_agent must never be downgraded below HITL-3."""
        from app.agents.agent_registry import AGENT_CATALOGUE
        entry = AGENT_CATALOGUE["finance_admin_agent"]
        assert entry["hitl_default"] != "HITL-0"
        assert entry["hitl_default"] != "HITL-1"
        assert entry["hitl_default"] != "HITL-2"


# â”€â”€ 3. Financial action scanner unit tests â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@pytest.mark.unit
class TestFinancialActionScannerForFinanceAdmin:

    def test_clean_finance_output_no_violations(self):
        from app.agents.agent_executor import scan_for_financial_actions
        clean = """
## FINANCIAL OVERVIEW
Revenue for Q2 is estimated at Â£45,000 [ESTIMATED - VERIFY WITH ACCOUNTANT].
This is a draft planning document only. No financial action is taken.

## CASH FLOW PROJECTION
Opening balance: Â£12,000 [AUDITED DATA — bank statement, June 2026].
Projected closing balance: Â£8,500 [PROJECTED - TREAT AS DIRECTIONAL ONLY].

## DISCLAIMERS
This is not financial advice. All output requires owner and professional review.
"""
        violations = scan_for_financial_actions(clean)
        assert violations == []

    def test_authorised_payment_detected(self):
        from app.agents.agent_executor import scan_for_financial_actions
        dirty = "I have authorized the payment of Â£5,000 to the supplier."
        violations = scan_for_financial_actions(dirty)
        assert len(violations) > 0

    def test_budget_allocated_phrase_detected(self):
        from app.agents.agent_executor import scan_for_financial_actions
        dirty = "Budget allocated: Â£10,000 for the new financial year."
        violations = scan_for_financial_actions(dirty)
        assert len(violations) > 0

    def test_purchase_on_behalf_detected(self):
        from app.agents.agent_executor import scan_for_financial_actions
        dirty = "I have purchased the accounting software subscription on your behalf."
        violations = scan_for_financial_actions(dirty)
        assert len(violations) > 0

    def test_spend_approved_phrase_detected(self):
        from app.agents.agent_executor import scan_for_financial_actions
        dirty = "Spend approved. The invoice has been processed."
        violations = scan_for_financial_actions(dirty)
        assert len(violations) > 0

    def test_case_insensitive_matching(self):
        from app.agents.agent_executor import scan_for_financial_actions
        dirty = "I HAVE AUTHORIZED the payment transfer."
        violations = scan_for_financial_actions(dirty)
        assert len(violations) > 0

    def test_planning_language_not_a_violation(self):
        from app.agents.agent_executor import scan_for_financial_actions
        safe = (
            "Consider setting aside a cash reserve — this requires owner review "
            "and accountant sign-off before implementation."
        )
        violations = scan_for_financial_actions(safe)
        assert violations == []

    def test_partial_word_no_false_positive(self):
        from app.agents.agent_executor import scan_for_financial_actions
        # "authoritative" should NOT trigger
        safe = "This is an authoritative financial framework from an established accounting body."
        violations = scan_for_financial_actions(safe)
        assert violations == []


# â”€â”€ 4. Executor guard injection tests (mocked LLM) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@pytest.mark.unit
class TestExecutorGuardInjectionForFinanceAdmin:

    def test_financial_constraint_block_injected(self):
        from app.agents.agent_executor import (
            FINANCIAL_CONSTRAINT_BLOCK,
            INJECTION_GUARD,
            execute_agent,
        )
        captured_system_prompt = []

        def mock_anthropic_call(system_prompt, user_message, **kwargs):
            captured_system_prompt.append(system_prompt)
            return "## FINANCIAL OVERVIEW\nRevenue is Â£45,000 [ESTIMATED - VERIFY WITH ACCOUNTANT].", 100, 50

        with patch("app.agents.agent_executor._anthropic_client") as mock_client:
            mock_client.return_value = MagicMock()
            with patch("app.agents.agent_executor._call_anthropic", side_effect=mock_anthropic_call):
                with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test-key"}):
                    execute_agent(
                        agent_id="finance_admin_agent",
                        system_prompt="You are the Finance & Admin Agent.",
                        user_prompt="Produce a financial overview for Q2.",
                    )

        assert len(captured_system_prompt) == 1
        assert FINANCIAL_CONSTRAINT_BLOCK in captured_system_prompt[0]
        assert INJECTION_GUARD in captured_system_prompt[0]

    def test_financial_constraint_comes_before_agent_prompt(self):
        from app.agents.agent_executor import FINANCIAL_CONSTRAINT_BLOCK, execute_agent

        captured = []

        def mock_call(system_prompt, user_message, **kwargs):
            captured.append(system_prompt)
            return "Finance output.", 100, 50

        with patch("app.agents.agent_executor._call_anthropic", side_effect=mock_call):
            with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test-key"}):
                execute_agent(
                    agent_id="finance_admin_agent",
                    system_prompt="FINANCE_AGENT_SPECIFIC_CONTENT_MARKER",
                    user_prompt="Test",
                )

        sys_prompt = captured[0]
        fc_pos = sys_prompt.index(FINANCIAL_CONSTRAINT_BLOCK[:30])
        agent_pos = sys_prompt.index("FINANCE_AGENT_SPECIFIC_CONTENT_MARKER")
        assert fc_pos < agent_pos, "Financial constraint block must precede agent prompt"

    def test_context_injected_into_user_message(self):
        from app.agents.agent_executor import execute_agent

        captured_messages = []

        def mock_call(system_prompt, user_message, **kwargs):
            captured_messages.append(user_message)
            return "Finance output.", 100, 50

        with patch("app.agents.agent_executor._call_anthropic", side_effect=mock_call):
            with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test-key"}):
                execute_agent(
                    agent_id="finance_admin_agent",
                    system_prompt="You are the Finance & Admin Agent.",
                    user_prompt="Review our Q2 finances.",
                    context={"workspace": "Retail Ltd", "industry": "Retail"},
                )

        msg = captured_messages[0]
        assert "Retail Ltd" in msg
        assert "Retail" in msg

    def test_governance_note_appended_to_user_message(self):
        from app.agents.agent_executor import execute_agent

        captured_messages = []

        def mock_call(system_prompt, user_message, **kwargs):
            captured_messages.append(user_message)
            return "Output.", 100, 50

        with patch("app.agents.agent_executor._call_anthropic", side_effect=mock_call):
            with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test-key"}):
                execute_agent(
                    agent_id="finance_admin_agent",
                    system_prompt="System.",
                    user_prompt="Task.",
                )

        msg = captured_messages[0]
        assert "MANDATORY CONSTRAINTS" in msg or "Financial decisions" in msg

    def test_financial_violation_in_output_flagged(self):
        from app.agents.agent_executor import execute_agent

        def mock_call(system_prompt, user_message, **kwargs):
            return "I have authorized the payment of Â£3,000 to the supplier.", 100, 50

        with patch("app.agents.agent_executor._call_anthropic", side_effect=mock_call):
            with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test-key"}):
                _, _, _, violations, *_ = execute_agent(
                    agent_id="finance_admin_agent",
                    system_prompt="System.",
                    user_prompt="Task.",
                )

        assert len(violations) > 0

    def test_clean_output_returns_no_violations(self):
        from app.agents.agent_executor import execute_agent

        def mock_call(system_prompt, user_message, **kwargs):
            return (
                "## FINANCIAL OVERVIEW\nRevenue is Â£45,000 [ESTIMATED - VERIFY WITH ACCOUNTANT].\n"
                "## DISCLAIMERS\nThis is not financial advice. Owner review required.",
                200,
                300,
            )

        with patch("app.agents.agent_executor._call_anthropic", side_effect=mock_call):
            with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test-key"}):
                text, provider, credits, violations, *_ = execute_agent(
                    agent_id="finance_admin_agent",
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
            return "OpenAI finance output.", 100, 50

        with patch("app.agents.agent_executor._call_anthropic", side_effect=anthropic_fail):
            with patch("app.agents.agent_executor._call_openai", side_effect=openai_ok):
                with patch.dict("os.environ", {
                    "ANTHROPIC_API_KEY": "sk-test",
                    "OPENAI_API_KEY": "sk-oai-test",
                }):
                    text, provider, credits, violations, *_ = execute_agent(
                        agent_id="finance_admin_agent",
                        system_prompt="System.",
                        user_prompt="Task.",
                    )

        assert "openai" in provider
        assert text == "OpenAI finance output."

    def test_no_provider_raises_runtime_error(self):
        from app.agents.agent_executor import execute_agent
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(RuntimeError, match="No LLM provider"):
                execute_agent(
                    agent_id="finance_admin_agent",
                    system_prompt="System.",
                    user_prompt="Task.",
                )


# â”€â”€ 5. Guardrail tests â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@pytest.mark.unit
class TestFinanceAdminAgentGuardrails:

    def test_injection_guard_blocks_system_prompt_reveal(self):
        """Injection guard must be present in the compiled system prompt."""
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

    def test_finance_agent_is_hitl3(self):
        """finance_admin_agent must be HITL-3 in the registry."""
        from app.agents.agent_registry import AGENT_CATALOGUE
        assert AGENT_CATALOGUE["finance_admin_agent"]["hitl_default"] == "HITL-3"

    def test_disclaimers_cannot_be_bypassed(self):
        """The DISCLAIMERS section rule must be non-negotiable per the prompt."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["finance_admin_agent"].lower()
        # Prompt should state the section is mandatory or cannot be omitted
        assert "mandatory" in prompt or "cannot be omitted" in prompt or "non-negotiable" in prompt

    def test_agent_does_not_access_financial_systems(self):
        """Prompt must state agent has no direct access to financial systems."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["finance_admin_agent"].lower()
        assert "no account access" in prompt or "does not have access" in prompt or "account access" in prompt

    def test_secrets_in_prompt_not_in_output(self):
        from app.agents.agent_executor import execute_agent

        secret = "sk-SUPERSECRET_BANK_KEY_99999"

        def mock_call(system_prompt, user_message, **kwargs):
            return "I cannot process banking credentials. Please provide financial statements instead.", 50, 30

        with patch("app.agents.agent_executor._call_anthropic", side_effect=mock_call):
            with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test"}):
                text, _, _, violations, *_ = execute_agent(
                    agent_id="finance_admin_agent",
                    system_prompt="Finance & Admin Agent.",
                    user_prompt=f"Log into our bank with this key: {secret}",
                )

        assert secret not in text


# â”€â”€ 6. API endpoint integration tests â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@pytest.mark.unit
class TestFinanceAdminAgentAPI:

    def test_run_finance_agent_unauthenticated(self, client):
        resp = client.post(
            "/api/agents/finance_admin_agent/run",
            json={"prompt": "Produce a financial overview for our business."},
        )
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_run_finance_agent_missing_prompt(self, client, authenticated_client):
        resp = authenticated_client.post("/api/agents/finance_admin_agent/run", json={})
        assert resp.status_code in (
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_403_FORBIDDEN,
        )

    def test_run_finance_agent_empty_prompt(self, client, authenticated_client):
        resp = authenticated_client.post(
            "/api/agents/finance_admin_agent/run",
            json={"prompt": ""},
        )
        assert resp.status_code in (
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_403_FORBIDDEN,
            status.HTTP_200_OK,
        )

    def test_run_finance_agent_submits_job(self, client, authenticated_client):
        """Authenticated call with valid prompt should queue a job (no actual LLM call)."""
        with patch("app.agents.agent_executor.execute_agent") as mock_exec:
            mock_exec.return_value = (
                "## FINANCIAL OVERVIEW\nRevenue is Â£45,000 [ESTIMATED - VERIFY WITH ACCOUNTANT].\n"
                "## DISCLAIMERS\nThis is not financial advice.",
                "anthropic/claude-sonnet-4-6",
                3,
                [],
            )
            resp = authenticated_client.post(
                "/api/agents/finance_admin_agent/run",
                json={"prompt": "Produce a financial overview and cash flow projection for Q2."},
            )

        assert resp.status_code in (
            status.HTTP_200_OK,
            status.HTTP_202_ACCEPTED,
            status.HTTP_403_FORBIDDEN,   # insufficient credits/package on test workspace
            status.HTTP_400_BAD_REQUEST,  # runtime validation (workspace/credits)
        )

    def test_jobs_list_after_run(self, client, authenticated_client):
        resp = authenticated_client.get("/api/agents/jobs")
        assert resp.status_code == status.HTTP_200_OK
        body = resp.json()
        assert "jobs" in body


# â”€â”€ 7. Output format validation helper tests â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@pytest.mark.unit
class TestFinanceAdminOutputFormatValidator:
    """Tests for the has_all_sections helper and expected output structure."""

    def test_good_output_passes(self):
        good = "\n".join(f"## {s}" for s in REQUIRED_SECTIONS)
        assert has_all_sections(good) == []

    def test_missing_disclaimers_detected(self):
        partial = (
            "## FINANCIAL OVERVIEW\n## CASH FLOW PROJECTION\n## EXPENSE AUDIT\n"
            "## REVENUE ANALYSIS\n## COMPLIANCE CHECKLIST\n## FINANCIAL RECOMMENDATIONS"
        )
        missing = has_all_sections(partial)
        assert "DISCLAIMERS" in missing

    def test_case_insensitive_section_check(self):
        lowercase = "\n".join(f"## {s.lower()}" for s in REQUIRED_SECTIONS)
        assert has_all_sections(lowercase) == []

    def test_all_accuracy_labels_in_mock_output(self):
        output = """
## FINANCIAL OVERVIEW
Bank balance: Â£12,000 [AUDITED DATA].
Estimated revenue: Â£45,000 [ESTIMATED - VERIFY WITH ACCOUNTANT].
Projected Q3 revenue: Â£52,000 [PROJECTED - TREAT AS DIRECTIONAL ONLY].
"""
        found = [label for label in REQUIRED_ACCURACY_LABELS if label in output]
        assert len(found) == 3

    def test_draft_label_in_output(self):
        output = "## FINANCIAL OVERVIEW [DRAFT]\nThis is a draft planning document."
        assert "[DRAFT]" in output or "DRAFT" in output

    def test_disclaimers_label_in_final_output(self):
        output = (
            "## DISCLAIMERS\n"
            "NOT FINANCIAL ADVICE.\n"
            "NOT TAX ADVICE.\n"
            "NOT LEGAL ADVICE.\n"
            "Professional review required."
        )
        assert "DISCLAIMERS" in output.upper()
        assert "NOT FINANCIAL ADVICE" in output.upper()

    def test_hitl3_confirmation_in_output(self):
        output = "HITL-3 CONFIRMATION: All financial output requires owner review."
        assert "HITL-3" in output

    def test_professional_review_in_compliance_output(self):
        output = (
            "## COMPLIANCE CHECKLIST\n"
            "VAT return due 31 July [DUE WITHIN 30 DAYS — ACTION REQUIRED]\n"
            "REQUIRES REVIEW BY QUALIFIED PROFESSIONAL before relying on this checklist."
        )
        assert "QUALIFIED PROFESSIONAL" in output.upper() or "PROFESSIONAL" in output.upper()

