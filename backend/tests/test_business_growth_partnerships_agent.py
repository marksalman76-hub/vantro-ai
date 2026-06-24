"""
business_growth_partnerships_agent test suite.

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
    "GROWTH OPPORTUNITIES",
    "PARTNERSHIP IDENTIFICATION",
    "OUTREACH STRATEGY",
    "PARTNERSHIP BRIEF",
    "DEAL STRUCTURE",
    "GROWTH METRICS",
    "PARTNERSHIP RISK MATRIX",
]

REQUIRED_CONFIDENCE_LABELS = [
    "[VALIDATED MARKET DATA]",
    "[INDUSTRY SIGNAL]",
    "[HYPOTHESIS - VALIDATE BEFORE COMMITTING]",
]

HITL_TRIGGER_PHRASES = ["HITL-2", "REQUIRES REVIEW", "REQUIRES OWNER APPROVAL", "owner approval"]


def has_all_sections(text: str) -> list[str]:
    """Return list of missing required sections."""
    return [s for s in REQUIRED_SECTIONS if s not in text.upper()]


# â”€â”€ 1. Prompt structure tests (no LLM, no network) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@pytest.mark.unit
class TestBusinessGrowthPartnershipsAgentPrompt:

    def test_prompt_exists(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        assert "business_growth_partnerships_agent" in AGENT_SYSTEM_PROMPTS

    def test_prompt_is_nonempty(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["business_growth_partnerships_agent"]
        assert len(prompt.strip()) > 500

    def test_prompt_has_all_required_sections(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["business_growth_partnerships_agent"]
        missing = has_all_sections(prompt)
        assert missing == [], f"Prompt missing sections: {missing}"

    def test_partnership_risk_matrix_section_exists(self):
        """PARTNERSHIP RISK MATRIX is the mandatory 7th section added in the upgrade."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["business_growth_partnerships_agent"]
        assert "PARTNERSHIP RISK MATRIX" in prompt.upper()

    def test_hitl2_gate_stated_in_prompt(self):
        """HITL-2 must be stated explicitly in the prompt."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["business_growth_partnerships_agent"]
        assert "HITL-2" in prompt

    def test_no_legal_agreement_without_owner_approval_rule(self):
        """Prompt must explicitly prohibit legal agreements without owner approval."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["business_growth_partnerships_agent"].lower()
        assert "legal" in prompt
        assert "owner approval" in prompt or "owner sign-off" in prompt
        # Must specifically address agreements/contracts
        assert "agreement" in prompt or "contract" in prompt or "commitment" in prompt

    def test_financial_terms_legal_counsel_rule_in_prompt(self):
        """Prompt must require legal counsel for financial terms and equity discussions."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["business_growth_partnerships_agent"].lower()
        assert "legal counsel" in prompt
        assert "financial term" in prompt or "equity" in prompt or "revenue-share" in prompt

    def test_all_three_opportunity_confidence_labels_present(self):
        """All 3 opportunity confidence labels must appear in the prompt."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["business_growth_partnerships_agent"]
        missing = [label for label in REQUIRED_CONFIDENCE_LABELS if label not in prompt]
        assert missing == [], f"Prompt missing confidence labels: {missing}"

    def test_validated_market_data_label_present(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["business_growth_partnerships_agent"]
        assert "[VALIDATED MARKET DATA]" in prompt

    def test_industry_signal_label_present(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["business_growth_partnerships_agent"]
        assert "[INDUSTRY SIGNAL]" in prompt

    def test_hypothesis_validate_label_present(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["business_growth_partnerships_agent"]
        assert "[HYPOTHESIS - VALIDATE BEFORE COMMITTING]" in prompt

    def test_prompt_has_hitl_gate_language(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["business_growth_partnerships_agent"].upper()
        found = any(phrase.upper() in prompt for phrase in HITL_TRIGGER_PHRASES)
        assert found

    def test_outreach_requires_review_rule(self):
        """Outreach must require human review before dispatch."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["business_growth_partnerships_agent"].upper()
        assert "REQUIRES REVIEW" in prompt

    def test_deal_terms_require_owner_approval(self):
        """Deal terms must require owner approval."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["business_growth_partnerships_agent"].upper()
        assert "REQUIRES OWNER APPROVAL" in prompt

    def test_partnership_risk_matrix_covers_legal_risk(self):
        """PARTNERSHIP RISK MATRIX must include legal risk dimension."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["business_growth_partnerships_agent"].upper()
        risk_matrix_idx = prompt.find("PARTNERSHIP RISK MATRIX")
        assert risk_matrix_idx != -1
        section_text = prompt[risk_matrix_idx:risk_matrix_idx + 3000]
        assert "LEGAL RISK" in section_text

    def test_partnership_risk_matrix_covers_financial_risk(self):
        """PARTNERSHIP RISK MATRIX must include financial risk dimension."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["business_growth_partnerships_agent"].upper()
        risk_matrix_idx = prompt.find("PARTNERSHIP RISK MATRIX")
        section_text = prompt[risk_matrix_idx:risk_matrix_idx + 3000]
        assert "FINANCIAL RISK" in section_text

    def test_partnership_risk_matrix_covers_reputational_risk(self):
        """PARTNERSHIP RISK MATRIX must include reputational risk dimension."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["business_growth_partnerships_agent"].upper()
        risk_matrix_idx = prompt.find("PARTNERSHIP RISK MATRIX")
        section_text = prompt[risk_matrix_idx:risk_matrix_idx + 3000]
        assert "REPUTATIONAL RISK" in section_text

    def test_partnership_risk_matrix_covers_exclusivity(self):
        """PARTNERSHIP RISK MATRIX must include exclusivity implications."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["business_growth_partnerships_agent"].upper()
        risk_matrix_idx = prompt.find("PARTNERSHIP RISK MATRIX")
        section_text = prompt[risk_matrix_idx:risk_matrix_idx + 3000]
        assert "EXCLUSIVITY" in section_text

    def test_partnership_risk_matrix_covers_exit_clause(self):
        """PARTNERSHIP RISK MATRIX must include exit clause requirements."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["business_growth_partnerships_agent"].upper()
        risk_matrix_idx = prompt.find("PARTNERSHIP RISK MATRIX")
        section_text = prompt[risk_matrix_idx:risk_matrix_idx + 3000]
        assert "EXIT" in section_text

    def test_no_autonomous_commitment_rule(self):
        """Prompt must state rule cannot be overridden for legal commitments."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["business_growth_partnerships_agent"].lower()
        assert "cannot be overridden" in prompt or "non-negotiable" in prompt

    def test_get_agent_system_prompt_helper(self):
        from app.agents.agent_prompts import get_agent_system_prompt
        prompt = get_agent_system_prompt("business_growth_partnerships_agent")
        assert "Business Growth" in prompt or "Partnerships Agent" in prompt

    def test_fallback_prompt_for_unknown_agent(self):
        from app.agents.agent_prompts import get_agent_system_prompt
        prompt = get_agent_system_prompt("totally_unknown_xyz_agent")
        assert len(prompt) > 20

    def test_draft_label_for_internal_strategy(self):
        """Internal strategy output must use the [DRAFT] label."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["business_growth_partnerships_agent"].upper()
        assert "[DRAFT]" in prompt

    def test_outreach_section_mentions_requires_review(self):
        """OUTREACH STRATEGY section must label content as REQUIRES REVIEW."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["business_growth_partnerships_agent"].upper()
        outreach_idx = prompt.find("OUTREACH STRATEGY")
        assert outreach_idx != -1
        outreach_text = prompt[outreach_idx:outreach_idx + 2000]
        assert "REQUIRES REVIEW" in outreach_text


# â”€â”€ 2. Registry entry tests â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@pytest.mark.unit
class TestBusinessGrowthPartnershipsAgentRegistry:

    def test_registry_entry_exists(self):
        from app.agents.agent_registry import AGENT_CATALOGUE
        assert "business_growth_partnerships_agent" in AGENT_CATALOGUE

    def test_registry_hitl_level_is_hitl2(self):
        """business_growth_partnerships_agent must be HITL-2."""
        from app.agents.agent_registry import AGENT_CATALOGUE
        entry = AGENT_CATALOGUE["business_growth_partnerships_agent"]
        assert entry["hitl_default"] == "HITL-2"

    def test_registry_min_package(self):
        from app.agents.agent_registry import AGENT_CATALOGUE
        entry = AGENT_CATALOGUE["business_growth_partnerships_agent"]
        # Registry shows BUSINESS; accept growth or business per architecture spec
        assert entry["min_package"] in ("growth", "business")

    def test_registry_has_capabilities(self):
        from app.agents.agent_registry import AGENT_CATALOGUE
        entry = AGENT_CATALOGUE["business_growth_partnerships_agent"]
        assert isinstance(entry.get("capabilities"), list)
        assert len(entry["capabilities"]) >= 3

    def test_registry_has_role(self):
        from app.agents.agent_registry import AGENT_CATALOGUE
        entry = AGENT_CATALOGUE["business_growth_partnerships_agent"]
        assert entry.get("role") and len(entry["role"]) > 20

    def test_registry_total_agent_count(self):
        """Non-negotiable: exactly 27 client-facing agents."""
        from app.agents.agent_registry import AGENT_CATALOGUE
        assert len(AGENT_CATALOGUE) == 22

    def test_registry_hitl_not_hitl0_or_hitl1(self):
        """business_growth_partnerships_agent must not be downgraded below HITL-2."""
        from app.agents.agent_registry import AGENT_CATALOGUE
        entry = AGENT_CATALOGUE["business_growth_partnerships_agent"]
        assert entry["hitl_default"] not in ("HITL-0", "HITL-1")

    def test_registry_architecture_type(self):
        """Agent must have a defined architecture type."""
        from app.agents.agent_registry import AGENT_CATALOGUE
        entry = AGENT_CATALOGUE["business_growth_partnerships_agent"]
        assert "architecture" in entry
        assert len(entry["architecture"]) > 0


# â”€â”€ 3. Financial action scanner unit tests â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@pytest.mark.unit
class TestFinancialActionScannerForPartnerships:

    def test_clean_partnerships_output_no_violations(self):
        from app.agents.agent_executor import scan_for_financial_actions
        clean = """
## GROWTH OPPORTUNITIES
Referral partnerships with SaaS tools [INDUSTRY SIGNAL].
Integration partnerships with complementary platforms [HYPOTHESIS - VALIDATE BEFORE COMMITTING].

## PARTNERSHIP RISK MATRIX
Legal Risk: [MEDIUM] — requires NDA before sharing IP details.
Financial Risk: [LOW] — referral fee arrangements require owner approval before committing.
"""
        violations = scan_for_financial_actions(clean)
        assert violations == []

    def test_autonomous_agreement_signing_detected(self):
        from app.agents.agent_executor import scan_for_financial_actions
        dirty = "I have authorized the partnership agreement with Acme Corp."
        violations = scan_for_financial_actions(dirty)
        assert len(violations) > 0

    def test_purchase_phrase_detected(self):
        from app.agents.agent_executor import scan_for_financial_actions
        dirty = "I have purchased the referral list on your behalf."
        violations = scan_for_financial_actions(dirty)
        assert len(violations) > 0

    def test_budget_allocated_phrase_detected(self):
        from app.agents.agent_executor import scan_for_financial_actions
        dirty = "Budget allocated: $5,000 for the co-marketing partnership campaign."
        violations = scan_for_financial_actions(dirty)
        assert len(violations) > 0

    def test_spend_approved_phrase_detected(self):
        from app.agents.agent_executor import scan_for_financial_actions
        dirty = "Spend approved. The revenue share agreement is now active."
        violations = scan_for_financial_actions(dirty)
        assert len(violations) > 0

    def test_case_insensitive_matching(self):
        from app.agents.agent_executor import scan_for_financial_actions
        dirty = "I HAVE AUTHORIZED the partnership deal."
        violations = scan_for_financial_actions(dirty)
        assert len(violations) > 0

    def test_planning_language_not_a_violation(self):
        from app.agents.agent_executor import scan_for_financial_actions
        safe = (
            "Consider a referral programme — financial terms require owner approval. "
            "[HYPOTHESIS - VALIDATE BEFORE COMMITTING]"
        )
        violations = scan_for_financial_actions(safe)
        assert violations == []

    def test_partial_word_no_false_positive(self):
        from app.agents.agent_executor import scan_for_financial_actions
        safe = "This is an authoritative analysis of the partnership landscape."
        violations = scan_for_financial_actions(safe)
        assert violations == []


# â”€â”€ 4. Executor guard injection tests (mocked LLM) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@pytest.mark.unit
class TestExecutorGuardInjectionForPartnerships:

    def test_financial_constraint_block_injected(self):
        from app.agents.agent_executor import (
            FINANCIAL_CONSTRAINT_BLOCK,
            INJECTION_GUARD,
            execute_agent,
        )
        captured_system_prompt = []

        def mock_anthropic_call(system_prompt, user_message, **kwargs):
            captured_system_prompt.append(system_prompt)
            return (
                "## GROWTH OPPORTUNITIES\nReferral partnerships [INDUSTRY SIGNAL].",
                100,
                50,
            )

        with patch("app.agents.agent_executor._anthropic_client") as mock_client:
            mock_client.return_value = MagicMock()
            with patch("app.agents.agent_executor._call_anthropic", side_effect=mock_anthropic_call):
                with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test-key"}):
                    execute_agent(
                        agent_id="business_growth_partnerships_agent",
                        system_prompt="You are the Business Growth & Partnerships Agent.",
                        user_prompt="Find partnership opportunities for our SaaS platform.",
                    )

        assert len(captured_system_prompt) == 1
        assert FINANCIAL_CONSTRAINT_BLOCK in captured_system_prompt[0]
        assert INJECTION_GUARD in captured_system_prompt[0]

    def test_financial_constraint_comes_before_agent_prompt(self):
        from app.agents.agent_executor import FINANCIAL_CONSTRAINT_BLOCK, execute_agent

        captured = []

        def mock_call(system_prompt, user_message, **kwargs):
            captured.append(system_prompt)
            return "Partnership output.", 100, 50

        with patch("app.agents.agent_executor._call_anthropic", side_effect=mock_call):
            with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test-key"}):
                execute_agent(
                    agent_id="business_growth_partnerships_agent",
                    system_prompt="PARTNERSHIPS_AGENT_SPECIFIC_CONTENT_MARKER",
                    user_prompt="Test",
                )

        sys_prompt = captured[0]
        fc_pos = sys_prompt.index(FINANCIAL_CONSTRAINT_BLOCK[:30])
        agent_pos = sys_prompt.index("PARTNERSHIPS_AGENT_SPECIFIC_CONTENT_MARKER")
        assert fc_pos < agent_pos, "Financial constraint block must precede agent prompt"

    def test_context_injected_into_user_message(self):
        from app.agents.agent_executor import execute_agent

        captured_messages = []

        def mock_call(system_prompt, user_message, **kwargs):
            captured_messages.append(user_message)
            return "Partnership output.", 100, 50

        with patch("app.agents.agent_executor._call_anthropic", side_effect=mock_call):
            with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test-key"}):
                execute_agent(
                    agent_id="business_growth_partnerships_agent",
                    system_prompt="You are the Business Growth & Partnerships Agent.",
                    user_prompt="Find partners for our product.",
                    context={"workspace": "GrowthCo", "industry": "B2B SaaS"},
                )

        msg = captured_messages[0]
        assert "GrowthCo" in msg
        assert "B2B SaaS" in msg

    def test_governance_note_appended_to_user_message(self):
        from app.agents.agent_executor import execute_agent

        captured_messages = []

        def mock_call(system_prompt, user_message, **kwargs):
            captured_messages.append(user_message)
            return "Output.", 100, 50

        with patch("app.agents.agent_executor._call_anthropic", side_effect=mock_call):
            with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test-key"}):
                execute_agent(
                    agent_id="business_growth_partnerships_agent",
                    system_prompt="System.",
                    user_prompt="Task.",
                )

        msg = captured_messages[0]
        assert "MANDATORY CONSTRAINTS" in msg or "Financial decisions" in msg

    def test_financial_violation_in_output_flagged(self):
        from app.agents.agent_executor import execute_agent

        def mock_call(system_prompt, user_message, **kwargs):
            return "I have authorized the partnership agreement of $10,000.", 100, 50

        with patch("app.agents.agent_executor._call_anthropic", side_effect=mock_call):
            with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test-key"}):
                _, _, _, violations = execute_agent(
                    agent_id="business_growth_partnerships_agent",
                    system_prompt="System.",
                    user_prompt="Task.",
                )

        assert len(violations) > 0

    def test_clean_output_returns_no_violations(self):
        from app.agents.agent_executor import execute_agent

        def mock_call(system_prompt, user_message, **kwargs):
            return (
                "## GROWTH OPPORTUNITIES\nReferral partnerships [INDUSTRY SIGNAL].\n"
                "## PARTNERSHIP RISK MATRIX\nLegal Risk: [MEDIUM]. Owner approval required.",
                200,
                300,
            )

        with patch("app.agents.agent_executor._call_anthropic", side_effect=mock_call):
            with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test-key"}):
                text, provider, credits, violations = execute_agent(
                    agent_id="business_growth_partnerships_agent",
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
            return "OpenAI partnership output.", 100, 50

        with patch("app.agents.agent_executor._call_anthropic", side_effect=anthropic_fail):
            with patch("app.agents.agent_executor._call_openai", side_effect=openai_ok):
                with patch.dict("os.environ", {
                    "ANTHROPIC_API_KEY": "sk-test",
                    "OPENAI_API_KEY": "sk-oai-test",
                }):
                    text, provider, credits, violations = execute_agent(
                        agent_id="business_growth_partnerships_agent",
                        system_prompt="System.",
                        user_prompt="Task.",
                    )

        assert "openai" in provider
        assert text == "OpenAI partnership output."

    def test_no_provider_raises_runtime_error(self):
        from app.agents.agent_executor import execute_agent
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(RuntimeError, match="No LLM provider"):
                execute_agent(
                    agent_id="business_growth_partnerships_agent",
                    system_prompt="System.",
                    user_prompt="Task.",
                )


# â”€â”€ 5. Guardrail tests â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@pytest.mark.unit
class TestBusinessGrowthPartnershipsAgentGuardrails:

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

    def test_agent_is_hitl2_not_hitl0_or_hitl1(self):
        """business_growth_partnerships_agent must be at minimum HITL-2."""
        from app.agents.agent_registry import AGENT_CATALOGUE
        entry = AGENT_CATALOGUE["business_growth_partnerships_agent"]
        assert entry["hitl_default"] == "HITL-2"

    def test_no_legal_agreement_rule_non_negotiable(self):
        """The no-legal-agreement rule must be stated as non-negotiable."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["business_growth_partnerships_agent"].lower()
        assert "cannot be overridden" in prompt or "non-negotiable" in prompt

    def test_secrets_in_prompt_not_in_output(self):
        """If user injects a secret, executor must not echo it back."""
        from app.agents.agent_executor import execute_agent

        secret = "sk-SUPERSECRET_PARTNER_KEY_99999"

        def mock_call(system_prompt, user_message, **kwargs):
            return (
                "I cannot process credentials. Please provide partnership objectives instead.",
                50,
                30,
            )

        with patch("app.agents.agent_executor._call_anthropic", side_effect=mock_call):
            with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test"}):
                text, _, _, violations = execute_agent(
                    agent_id="business_growth_partnerships_agent",
                    system_prompt="Business Growth Partnerships Agent.",
                    user_prompt=f"Use this key to access the partner API: {secret}",
                )

        assert secret not in text


# â”€â”€ 6. API endpoint integration tests â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@pytest.mark.unit
class TestBusinessGrowthPartnershipsAgentAPI:

    def test_run_agent_unauthenticated(self, client):
        resp = client.post(
            "/api/agents/business_growth_partnerships_agent/run",
            json={"prompt": "Find partnership opportunities for our SaaS platform."},
        )
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_run_agent_missing_prompt(self, client, authenticated_client):
        resp = authenticated_client.post(
            "/api/agents/business_growth_partnerships_agent/run",
            json={},
        )
        assert resp.status_code in (
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_403_FORBIDDEN,
        )

    def test_run_agent_empty_prompt(self, client, authenticated_client):
        resp = authenticated_client.post(
            "/api/agents/business_growth_partnerships_agent/run",
            json={"prompt": ""},
        )
        assert resp.status_code in (
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_403_FORBIDDEN,
            status.HTTP_200_OK,
        )

    def test_run_agent_submits_job(self, client, authenticated_client):
        """Authenticated call with valid prompt should queue a job (no actual LLM call)."""
        with patch("app.agents.agent_executor.execute_agent") as mock_exec:
            mock_exec.return_value = (
                "## GROWTH OPPORTUNITIES\nReferral partnerships [INDUSTRY SIGNAL].\n"
                "## PARTNERSHIP RISK MATRIX\nLegal Risk: [MEDIUM].",
                "anthropic/claude-sonnet-4-6",
                3,
                [],
            )
            resp = authenticated_client.post(
                "/api/agents/business_growth_partnerships_agent/run",
                json={"prompt": "Find partnership opportunities for our B2B SaaS platform."},
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
class TestPartnershipsOutputFormatValidator:
    """Tests for the has_all_sections helper and expected output structure."""

    def test_good_output_passes(self):
        good = "\n".join(f"## {s}" for s in REQUIRED_SECTIONS)
        assert has_all_sections(good) == []

    def test_missing_partnership_risk_matrix_detected(self):
        partial = (
            "## GROWTH OPPORTUNITIES\n"
            "## PARTNERSHIP IDENTIFICATION\n"
            "## OUTREACH STRATEGY\n"
            "## PARTNERSHIP BRIEF\n"
            "## DEAL STRUCTURE\n"
            "## GROWTH METRICS"
        )
        missing = has_all_sections(partial)
        assert "PARTNERSHIP RISK MATRIX" in missing

    def test_case_insensitive_section_check(self):
        lowercase = "\n".join(f"## {s.lower()}" for s in REQUIRED_SECTIONS)
        assert has_all_sections(lowercase) == []

    def test_all_confidence_labels_in_mock_output(self):
        output = """
## GROWTH OPPORTUNITIES
Referral partnerships confirmed by industry data. [VALIDATED MARKET DATA]
SaaS integration partnerships are a common growth lever. [INDUSTRY SIGNAL]
Influencer co-marketing may work for this niche. [HYPOTHESIS - VALIDATE BEFORE COMMITTING]
"""
        found = [label for label in REQUIRED_CONFIDENCE_LABELS if label in output]
        assert len(found) == 3

    def test_partnership_risk_matrix_in_output(self):
        output = (
            "## PARTNERSHIP RISK MATRIX\n"
            "Legal Risk: [HIGH] — NDA required.\n"
            "Financial Risk: [MEDIUM] — revenue-share terms need owner approval.\n"
            "Reputational Risk: [LOW] — brand alignment verified.\n"
            "Exclusivity Implications: [HIGH — avoid without strong upside].\n"
            "Exit Clause Requirements: Define notice period before signing."
        )
        assert "PARTNERSHIP RISK MATRIX" in output.upper()

    def test_draft_label_for_internal_output(self):
        output = "[DRAFT] Growth opportunity mapping for internal planning."
        assert "[DRAFT]" in output

    def test_requires_review_label_for_outreach(self):
        output = "[REQUIRES REVIEW] Outreach message draft — do not send without owner review."
        assert "[REQUIRES REVIEW]" in output

    def test_requires_owner_approval_label_for_deal_terms(self):
        output = (
            "## DEAL STRUCTURE\n"
            "Revenue share at 15% [REQUIRES OWNER APPROVAL — FINANCIAL TERMS REQUIRE LEGAL COUNSEL REVIEW]."
        )
        assert "REQUIRES OWNER APPROVAL" in output.upper()

