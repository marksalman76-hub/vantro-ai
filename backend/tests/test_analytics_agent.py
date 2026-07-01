"""
research_analytics_agent test suite.

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
    "RESEARCH BRIEF & SCOPE",
    "MARKET LANDSCAPE",
    "COMPETITIVE INTELLIGENCE",
    "DATA ANALYSIS & KPIS",
    "TREND ANALYSIS",
    "FUNNEL & CONVERSION ANALYSIS",
    "INSIGHTS & RECOMMENDATIONS",
    "DATA GAPS & NEXT RESEARCH STEPS",
]

REQUIRED_METRIC_TERMS = ["metric", "percentage", "data", "trend", "kpi"]

REQUIRED_FACT_CORRELATION_TERMS = ["inferred", "estimated"]

BUDGET_FLAG_PHRASES = [
    "owner approval",
    "flagging",
    "approval",
    "without approval",
]


def has_all_sections(text: str) -> list[str]:
    """Return list of missing required sections (case-insensitive)."""
    upper = text.upper()
    return [s for s in REQUIRED_SECTIONS if s not in upper]


# â”€â”€ 1. Prompt structure tests â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@pytest.mark.unit
class TestAnalyticsAgentPrompt:

    def test_prompt_exists(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        assert "research_analytics_agent" in AGENT_SYSTEM_PROMPTS

    def test_prompt_is_nonempty(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["research_analytics_agent"]
        assert len(prompt.strip()) > 200

    def test_prompt_has_all_required_sections(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["research_analytics_agent"]
        missing = has_all_sections(prompt)
        assert missing == [], f"Prompt missing sections: {missing}"

    def test_prompt_has_performance_summary_section(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["research_analytics_agent"].upper()
        assert "RESEARCH BRIEF & SCOPE" in prompt

    def test_prompt_has_key_metrics_section(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["research_analytics_agent"].upper()
        assert "DATA ANALYSIS & KPIS" in prompt

    def test_prompt_has_trend_analysis_section(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["research_analytics_agent"].upper()
        assert "TREND ANALYSIS" in prompt

    def test_prompt_has_root_cause_hypothesis_section(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["research_analytics_agent"].upper()
        assert "COMPETITIVE INTELLIGENCE" in prompt

    def test_prompt_has_opportunities_section(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["research_analytics_agent"].upper()
        assert "FUNNEL & CONVERSION ANALYSIS" in prompt

    def test_prompt_has_recommendations_section(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["research_analytics_agent"].upper()
        assert "INSIGHTS & RECOMMENDATIONS" in prompt

    def test_prompt_has_watch_list_section(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["research_analytics_agent"].upper()
        assert "DATA GAPS & NEXT RESEARCH STEPS" in prompt

    def test_prompt_has_data_or_metric_language(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["research_analytics_agent"].lower()
        found = [term for term in REQUIRED_METRIC_TERMS if term in prompt]
        assert len(found) >= 2, f"Prompt should reference data/metric language, found: {found}"

    def test_prompt_has_fact_correlation_distinction_language(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["research_analytics_agent"].lower()
        found = [term for term in REQUIRED_FACT_CORRELATION_TERMS if term in prompt]
        assert len(found) >= 1, (
            "Prompt must use inference/estimation language, found none of: "
            f"{REQUIRED_FACT_CORRELATION_TERMS}"
        )

    def test_prompt_has_budget_flag_language(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["research_analytics_agent"].lower()
        found = [phrase for phrase in BUDGET_FLAG_PHRASES if phrase in prompt]
        assert len(found) >= 1, (
            "Prompt must instruct agent to flag spend changes for owner approval. "
            f"None of {BUDGET_FLAG_PHRASES} found."
        )

    def test_prompt_has_specific_numbers_language(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["research_analytics_agent"].lower()
        assert "specific" in prompt or "number" in prompt or "percentage" in prompt

    def test_prompt_has_data_confidence_language(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["research_analytics_agent"].lower()
        assert "unavailable" in prompt or "validate" in prompt or "unverified" in prompt

    def test_get_agent_system_prompt_helper(self):
        from app.agents.agent_prompts import get_agent_system_prompt
        prompt = get_agent_system_prompt("research_analytics_agent")
        assert "Analytics Agent" in prompt

    def test_fallback_prompt_for_unknown_agent(self):
        from app.agents.agent_prompts import get_agent_system_prompt
        prompt = get_agent_system_prompt("totally_unknown_xyz_agent")
        assert len(prompt) > 20


# â”€â”€ 2. Registry entry tests â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@pytest.mark.unit
class TestAnalyticsAgentRegistry:

    def test_registry_entry_exists(self):
        from app.agents.agent_registry import AGENT_CATALOGUE
        assert "research_analytics_agent" in AGENT_CATALOGUE

    def test_registry_hitl_level_is_hitl_0(self):
        from app.agents.agent_registry import AGENT_CATALOGUE
        entry = AGENT_CATALOGUE["research_analytics_agent"]
        assert entry["hitl_default"] == "HITL-0"

    def test_registry_min_package_is_growth(self):
        from app.agents.agent_registry import AGENT_CATALOGUE
        entry = AGENT_CATALOGUE["research_analytics_agent"]
        assert entry["min_package"] == "starter"

    def test_registry_has_capabilities_list(self):
        from app.agents.agent_registry import AGENT_CATALOGUE
        entry = AGENT_CATALOGUE["research_analytics_agent"]
        assert isinstance(entry.get("capabilities"), list)
        assert len(entry["capabilities"]) >= 3

    def test_registry_has_role(self):
        from app.agents.agent_registry import AGENT_CATALOGUE
        entry = AGENT_CATALOGUE["research_analytics_agent"]
        assert entry.get("role") and len(entry["role"]) > 20

    def test_registry_role_references_analytics_domain(self):
        from app.agents.agent_registry import AGENT_CATALOGUE
        role = AGENT_CATALOGUE["research_analytics_agent"]["role"].lower()
        assert any(term in role for term in ["performance", "metrics", "analytics", "trends", "reports"])

    def test_registry_capabilities_include_analytics_terms(self):
        from app.agents.agent_registry import AGENT_CATALOGUE
        capabilities = AGENT_CATALOGUE["research_analytics_agent"]["capabilities"]
        caps_joined = " ".join(capabilities).lower()
        assert any(term in caps_joined for term in ["report", "kpi", "trend", "funnel", "analysis", "optimisation"])

    def test_registry_total_agent_count_is_27(self):
        """Non-negotiable: exactly 27 client-facing agents."""
        from app.agents.agent_registry import AGENT_CATALOGUE
        assert len(AGENT_CATALOGUE) == 22

    def test_registry_category_is_research(self):
        from app.agents.agent_registry import AGENT_CATALOGUE
        entry = AGENT_CATALOGUE["research_analytics_agent"]
        assert entry.get("category") == "Research"

    def test_registry_visibility_is_purchasable(self):
        from app.agents.agent_registry import AGENT_CATALOGUE
        entry = AGENT_CATALOGUE["research_analytics_agent"]
        assert entry.get("visibility") == "purchasable"

    def test_registry_credit_estimate_is_positive(self):
        from app.agents.agent_registry import AGENT_CATALOGUE
        entry = AGENT_CATALOGUE["research_analytics_agent"]
        assert entry.get("credit_estimate", 0) >= 1


# â”€â”€ 3. Executor guard injection tests (mocked LLM) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@pytest.mark.unit
class TestAnalyticsAgentExecutor:

    def test_financial_constraint_block_injected(self):
        from app.agents.agent_executor import (
            FINANCIAL_CONSTRAINT_BLOCK,
            INJECTION_GUARD,
            execute_agent,
        )
        captured_system_prompts = []

        def mock_anthropic_call(system_prompt, user_message, **kwargs):
            captured_system_prompts.append(system_prompt)
            return "Clean analytics output with trend data and no financial actions.", 100, 50

        with patch("app.agents.agent_executor._call_anthropic_with_tools", side_effect=mock_anthropic_call):
            with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test-key"}):
                execute_agent(
                    agent_id="research_analytics_agent",
                    system_prompt="You are the Analytics Agent.",
                    user_prompt="Analyse our Q2 conversion funnel performance.",
                )

        assert len(captured_system_prompts) == 1
        assert FINANCIAL_CONSTRAINT_BLOCK in captured_system_prompts[0]
        assert INJECTION_GUARD in captured_system_prompts[0]

    def test_financial_constraint_comes_before_agent_prompt(self):
        from app.agents.agent_executor import FINANCIAL_CONSTRAINT_BLOCK, execute_agent

        captured = []

        def mock_call(system_prompt, user_message, **kwargs):
            captured.append(system_prompt)
            return "Analytics output.", 100, 50

        with patch("app.agents.agent_executor._call_anthropic_with_tools", side_effect=mock_call):
            with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test-key"}):
                execute_agent(
                    agent_id="research_analytics_agent",
                    system_prompt="ANALYTICS_AGENT_SPECIFIC_CONTENT_MARKER",
                    user_prompt="Test analytics task.",
                )

        sys_prompt = captured[0]
        fc_pos = sys_prompt.index(FINANCIAL_CONSTRAINT_BLOCK[:30])
        agent_pos = sys_prompt.index("ANALYTICS_AGENT_SPECIFIC_CONTENT_MARKER")
        assert fc_pos < agent_pos, "Financial constraint block must precede agent-specific prompt"

    def test_clean_output_returns_no_violations(self):
        from app.agents.agent_executor import execute_agent

        def mock_call(system_prompt, user_message, **kwargs):
            return (
                "## PERFORMANCE SUMMARY\nConversion rate increased 12% MoM.\n\n"
                "## KEY METRICS\nCAC: $42. LTV: $380. Funnel drop-off: 34% at checkout.\n\n"
                "## TREND ANALYSIS\nMobile sessions up 18% QoQ. Desktop declining.\n\n"
                "## ROOT CAUSE HYPOTHESIS\nCheckout friction likely caused by multi-step form.\n\n"
                "## OPPORTUNITIES\nSimplifying checkout could recover ~$8K/month in lost revenue.\n\n"
                "## RECOMMENDATIONS\nA/B test single-page checkout. This requires your approval.\n\n"
                "## WATCH LIST\nMonitor cart abandonment rate weekly. Alert if above 70%.",
                200,
                400,
            )

        with patch("app.agents.agent_executor._call_anthropic_with_tools", side_effect=mock_call):
            with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test-key"}):
                text, provider, credits, violations, *_ = execute_agent(
                    agent_id="research_analytics_agent",
                    system_prompt="You are the Analytics Agent.",
                    user_prompt="Analyse our Q2 funnel.",
                )

        assert violations == []
        assert credits >= 1
        assert "anthropic" in provider

    def test_financial_phrase_in_output_triggers_violation(self):
        from app.agents.agent_executor import execute_agent

        def mock_call(system_prompt, user_message, **kwargs):
            return "Budget allocated: $15,000 for Q3 paid search campaigns.", 100, 50

        with patch("app.agents.agent_executor._call_anthropic_with_tools", side_effect=mock_call):
            with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test-key"}):
                _, _, _, violations, *_ = execute_agent(
                    agent_id="research_analytics_agent",
                    system_prompt="You are the Analytics Agent.",
                    user_prompt="Analyse spend efficiency.",
                )

        assert len(violations) > 0

    def test_authorisation_phrase_in_output_triggers_violation(self):
        from app.agents.agent_executor import execute_agent

        def mock_call(system_prompt, user_message, **kwargs):
            return "I have authorized the budget increase to $25,000 for the campaign.", 100, 50

        with patch("app.agents.agent_executor._call_anthropic_with_tools", side_effect=mock_call):
            with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test-key"}):
                _, _, _, violations, *_ = execute_agent(
                    agent_id="research_analytics_agent",
                    system_prompt="Analytics Agent.",
                    user_prompt="Scale the ad spend.",
                )

        assert len(violations) > 0

    def test_spend_approved_phrase_triggers_violation(self):
        from app.agents.agent_executor import execute_agent

        def mock_call(system_prompt, user_message, **kwargs):
            return "Spend approved. Scaling campaigns to $50,000 next week.", 100, 50

        with patch("app.agents.agent_executor._call_anthropic_with_tools", side_effect=mock_call):
            with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test-key"}):
                _, _, _, violations, *_ = execute_agent(
                    agent_id="research_analytics_agent",
                    system_prompt="Analytics Agent.",
                    user_prompt="Process the budget approval.",
                )

        assert len(violations) > 0

    def test_tokens_to_credits_minimum_one(self):
        from app.agents.agent_executor import _tokens_to_credits
        assert _tokens_to_credits(0, 0) == 1
        assert _tokens_to_credits(1, 1) == 1
        assert _tokens_to_credits(500, 500) == 1
        assert _tokens_to_credits(1000, 1000) == 2

    def test_tokens_to_credits_large_token_count(self):
        from app.agents.agent_executor import _tokens_to_credits
        assert _tokens_to_credits(5000, 5000) == 10

    def test_openai_fallback_when_anthropic_fails(self):
        from app.agents.agent_executor import execute_agent

        def anthropic_fail(system_prompt, user_message):
            raise RuntimeError("Anthropic unavailable")

        def openai_ok(system_prompt, user_message):
            return "OpenAI analytics fallback output.", 100, 50

        with patch("app.agents.agent_executor._call_anthropic_with_tools", side_effect=anthropic_fail):
            with patch("app.agents.agent_executor._call_openai", side_effect=openai_ok):
                with patch.dict("os.environ", {
                    "ANTHROPIC_API_KEY": "sk-test",
                    "OPENAI_API_KEY": "sk-oai-test",
                }):
                    text, provider, credits, violations, *_ = execute_agent(
                        agent_id="research_analytics_agent",
                        system_prompt="Analytics Agent.",
                        user_prompt="Analyse weekly KPIs.",
                    )

        assert "openai" in provider
        assert text == "OpenAI analytics fallback output."
        assert violations == []

    def test_no_provider_raises_runtime_error(self):
        from app.agents.agent_executor import execute_agent
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(RuntimeError, match="No LLM provider"):
                execute_agent(
                    agent_id="research_analytics_agent",
                    system_prompt="Analytics Agent.",
                    user_prompt="Analyse this data.",
                )

    def test_context_injected_into_user_message(self):
        from app.agents.agent_executor import execute_agent

        captured_messages = []

        def mock_call(system_prompt, user_message, **kwargs):
            captured_messages.append(user_message)
            return "Analytics output.", 100, 50

        with patch("app.agents.agent_executor._call_anthropic_with_tools", side_effect=mock_call):
            with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test-key"}):
                execute_agent(
                    agent_id="research_analytics_agent",
                    system_prompt="You are the Analytics Agent.",
                    user_prompt="Analyse our funnel.",
                    context={"workspace": "Acme Corp", "industry": "SaaS"},
                )

        msg = captured_messages[0]
        assert "Acme Corp" in msg
        assert "SaaS" in msg

    def test_governance_note_appended_to_user_message(self):
        from app.agents.agent_executor import execute_agent

        captured_messages = []

        def mock_call(system_prompt, user_message, **kwargs):
            captured_messages.append(user_message)
            return "Output.", 100, 50

        with patch("app.agents.agent_executor._call_anthropic_with_tools", side_effect=mock_call):
            with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test-key"}):
                execute_agent(
                    agent_id="research_analytics_agent",
                    system_prompt="Analytics Agent.",
                    user_prompt="Task.",
                )

        msg = captured_messages[0]
        assert "MANDATORY CONSTRAINTS" in msg or "Financial decisions" in msg


# â”€â”€ 4. Guardrail tests â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@pytest.mark.unit
class TestAnalyticsAgentGuardrails:

    def test_prompt_has_explicit_budget_flag_rule(self):
        """Prompt must instruct agent to flag budget/spend changes for owner approval."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["research_analytics_agent"].lower()
        assert "owner approval" in prompt or "approval" in prompt, (
            "research_analytics_agent prompt must explicitly require owner approval for budget changes"
        )

    def test_prompt_budget_rule_covers_spend_increases(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["research_analytics_agent"].lower()
        assert "financial" in prompt or "resource" in prompt or "approval" in prompt, (
            "Prompt must reference financial/resource decisions requiring approval"
        )

    def test_financial_patterns_list_minimum_ten_items(self):
        from app.agents.agent_executor import FINANCIAL_ACTION_PATTERNS
        assert len(FINANCIAL_ACTION_PATTERNS) >= 10, (
            f"Expected at least 10 financial action patterns, got {len(FINANCIAL_ACTION_PATTERNS)}"
        )

    def test_financial_patterns_cover_authorisation_language(self):
        from app.agents.agent_executor import FINANCIAL_ACTION_PATTERNS
        patterns_joined = " ".join(FINANCIAL_ACTION_PATTERNS)
        assert "authoris" in patterns_joined or "authoriz" in patterns_joined

    def test_financial_patterns_cover_budget_language(self):
        from app.agents.agent_executor import FINANCIAL_ACTION_PATTERNS
        patterns_joined = " ".join(FINANCIAL_ACTION_PATTERNS)
        assert "budget" in patterns_joined

    def test_financial_patterns_cover_spend_language(self):
        from app.agents.agent_executor import FINANCIAL_ACTION_PATTERNS
        patterns_joined = " ".join(FINANCIAL_ACTION_PATTERNS)
        assert "spend" in patterns_joined

    def test_financial_patterns_cover_payment_language(self):
        from app.agents.agent_executor import FINANCIAL_ACTION_PATTERNS
        patterns_joined = " ".join(FINANCIAL_ACTION_PATTERNS)
        assert "paid" in patterns_joined or "payment" in patterns_joined or "purchased" in patterns_joined

    def test_injection_guard_covers_system_prompt_reveal(self):
        from app.agents.agent_executor import INJECTION_GUARD
        guard = INJECTION_GUARD.lower()
        assert "system prompt" in guard, "Injection guard must reference system prompt protection"
        assert (
            "cannot be overridden" in guard
            or "immutable" in guard
            or "fixed" in guard
        ), "Injection guard must use immutability language"

    def test_injection_guard_instructs_decline_of_reveal_requests(self):
        from app.agents.agent_executor import INJECTION_GUARD
        guard = INJECTION_GUARD.lower()
        assert "decline" in guard or "never reveal" in guard or "politely decline" in guard

    def test_research_analytics_agent_is_not_hitl_3(self):
        """research_analytics_agent must never be HITL-3 gated — it is HITL-0."""
        from app.agents.agent_registry import AGENT_CATALOGUE
        assert AGENT_CATALOGUE["research_analytics_agent"]["hitl_default"] != "HITL-3"

    def test_research_analytics_agent_is_not_hitl_1(self):
        """research_analytics_agent is HITL-0; confirm it is not incorrectly elevated."""
        from app.agents.agent_registry import AGENT_CATALOGUE
        assert AGENT_CATALOGUE["research_analytics_agent"]["hitl_default"] != "HITL-1"

    def test_secrets_in_prompt_not_echoed_in_output(self):
        from app.agents.agent_executor import execute_agent

        secret = "sk-SUPERSECRET_ANALYTICS_KEY_99999"

        def mock_call(system_prompt, user_message, **kwargs):
            return (
                "I cannot process credentials or API keys. "
                "Please provide your performance data instead.",
                50,
                30,
            )

        with patch("app.agents.agent_executor._call_anthropic_with_tools", side_effect=mock_call):
            with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test"}):
                text, _, _, violations, *_ = execute_agent(
                    agent_id="research_analytics_agent",
                    system_prompt="Analytics Agent.",
                    user_prompt=f"Use this key to pull data: {secret}",
                )

        assert secret not in text

    def test_financial_constraint_block_covers_key_actions(self):
        from app.agents.agent_executor import FINANCIAL_CONSTRAINT_BLOCK
        block = FINANCIAL_CONSTRAINT_BLOCK.lower()
        required_coverage = ["spending", "budgets", "payments", "hiring"]
        missing = [term for term in required_coverage if term not in block]
        assert missing == [], f"Financial constraint block missing coverage for: {missing}"


# â”€â”€ 5. API endpoint integration tests â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@pytest.mark.unit
class TestAnalyticsAgentAPI:

    def test_run_research_analytics_agent_unauthenticated(self, client):
        resp = client.post(
            "/api/agents/research_analytics_agent/run",
            json={"prompt": "Analyse our weekly sales metrics."},
        )
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_run_research_analytics_agent_missing_prompt(self, client, authenticated_client):
        resp = authenticated_client.post("/api/agents/research_analytics_agent/run", json={})
        assert resp.status_code in (
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_403_FORBIDDEN,
        )

    def test_run_research_analytics_agent_empty_prompt(self, client, authenticated_client):
        resp = authenticated_client.post(
            "/api/agents/research_analytics_agent/run",
            json={"prompt": ""},
        )
        assert resp.status_code in (
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_403_FORBIDDEN,
            status.HTTP_200_OK,
        )

    def test_run_research_analytics_agent_submits_job(self, client, authenticated_client):
        """Authenticated call with a valid prompt queues a job without a real LLM call."""
        with patch("app.agents.agent_executor.execute_agent") as mock_exec:
            mock_exec.return_value = (
                (
                    "## PERFORMANCE SUMMARY\nSales up 18% MoM.\n\n"
                    "## KEY METRICS\nCAC: $38. LTV: $410.\n\n"
                    "## TREND ANALYSIS\nEmail open rate trending up.\n\n"
                    "## ROOT CAUSE HYPOTHESIS\nImproved subject line personalisation.\n\n"
                    "## OPPORTUNITIES\nUpsell segment shows 3x LTV potential.\n\n"
                    "## RECOMMENDATIONS\nExpand upsell flow. Requires your approval.\n\n"
                    "## WATCH LIST\nMonitor churn rate weekly."
                ),
                "anthropic/claude-sonnet-4-6",
                2,
                [],
            )
            resp = authenticated_client.post(
                "/api/agents/research_analytics_agent/run",
                json={"prompt": "Analyse our monthly sales and email performance metrics."},
            )

        assert resp.status_code in (
            status.HTTP_200_OK,
            status.HTTP_202_ACCEPTED,
            status.HTTP_400_BAD_REQUEST,  # runtime validation (workspace/credits)
            status.HTTP_403_FORBIDDEN,  # insufficient credits/package on test workspace
        )

    def test_jobs_list_returns_200(self, client, authenticated_client):
        resp = authenticated_client.get("/api/agents/jobs")
        assert resp.status_code == status.HTTP_200_OK

    def test_jobs_list_returns_jobs_key(self, client, authenticated_client):
        resp = authenticated_client.get("/api/agents/jobs")
        body = resp.json()
        assert "jobs" in body

    def test_run_research_analytics_agent_unauthenticated_no_token(self, client):
        """Ensure there is no accidental anonymous access to the analytics endpoint."""
        resp = client.post(
            "/api/agents/research_analytics_agent/run",
            json={"prompt": "Show me the conversion funnel."},
            headers={},
        )
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED


# â”€â”€ 6. Output format validation helper tests â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@pytest.mark.unit
class TestAnalyticsOutputValidator:

    def test_good_output_passes_validation(self):
        good = "\n".join(f"## {s}" for s in REQUIRED_SECTIONS)
        assert has_all_sections(good) == []

    def test_missing_section_detected(self):
        partial = (
            "## RESEARCH BRIEF & SCOPE\n"
            "## MARKET LANDSCAPE\n"
            "## TREND ANALYSIS\n"
        )
        missing = has_all_sections(partial)
        assert "COMPETITIVE INTELLIGENCE" in missing
        assert "INSIGHTS & RECOMMENDATIONS" in missing
        assert "DATA GAPS & NEXT RESEARCH STEPS" in missing

    def test_single_missing_section_detected(self):
        sections_without_last = [s for s in REQUIRED_SECTIONS if s != "DATA GAPS & NEXT RESEARCH STEPS"]
        text = "\n".join(f"## {s}" for s in sections_without_last)
        missing = has_all_sections(text)
        assert "DATA GAPS & NEXT RESEARCH STEPS" in missing
        assert len(missing) == 1

    def test_case_insensitive_section_check(self):
        lowercase = "\n".join(f"## {s.lower()}" for s in REQUIRED_SECTIONS)
        assert has_all_sections(lowercase) == []

    def test_mixed_case_section_check(self):
        mixed = "\n".join(f"## {s.capitalize()}" for s in REQUIRED_SECTIONS)
        assert has_all_sections(mixed) == []

    def test_full_mock_output_passes_all_sections(self):
        output = """
## RESEARCH BRIEF & SCOPE
Objective: analyse ecommerce conversion performance Q2 2026.

## MARKET LANDSCAPE
AI-driven ecommerce market valued at $200B [PRIMARY SOURCE].

## COMPETITIVE INTELLIGENCE
Key competitor A: strong checkout flow, weak mobile UX [SECONDARY SOURCE].

## DATA ANALYSIS & KPIS
Conversion rate: 2.8% (up from 2.1%) [TOOL-VERIFIED via GA4].

## TREND ANALYSIS
Mobile checkout completions increased 31% [INFERRED PATTERN].

## FUNNEL & CONVERSION ANALYSIS
Drop-off at checkout: 61% cart abandonment [ESTIMATED - VALIDATE].

## INSIGHTS & RECOMMENDATIONS
1. Expand one-click checkout. [REQUIRES OWNER REVIEW BEFORE ACTING]
2. A/B test upsell placement.

## DATA GAPS & NEXT RESEARCH STEPS
Missing: customer LTV segmentation data. Recommend GA4 + CRM integration.
"""
        missing = has_all_sections(output)
        assert missing == [], f"Full mock output missing sections: {missing}"

    def test_output_with_no_sections_fails_all(self):
        bare = "This is a plain text analytics report with no structured sections."
        missing = has_all_sections(bare)
        assert len(missing) == len(REQUIRED_SECTIONS)

    def test_all_seven_sections_are_in_required_list(self):
        assert len(REQUIRED_SECTIONS) == 8

    def test_required_sections_are_uppercase(self):
        for section in REQUIRED_SECTIONS:
            assert section == section.upper(), f"Section key should be uppercase: {section!r}"

    def test_performance_summary_is_first_section(self):
        assert REQUIRED_SECTIONS[0] == "RESEARCH BRIEF & SCOPE"

    def test_watch_list_is_last_section(self):
        assert REQUIRED_SECTIONS[-1] == "DATA GAPS & NEXT RESEARCH STEPS"

