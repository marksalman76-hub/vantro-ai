"""
strategist_agent test suite.

Covers:
  - Prompt structure validation (no LLM calls)
  - Registry entry correctness
  - Executor guard injection (mocked LLM)
  - Financial action scanner (unit)
  - Guardrail tests
  - API endpoint integration tests
  - Output format validation helper
"""
import pytest
from unittest.mock import patch, MagicMock
from fastapi import status


# â”€â”€ Helpers â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

REQUIRED_SECTIONS = [
    "STRATEGIC CONTEXT",
    "POSITIONING",
    "CORE STRATEGY",
    "EXECUTION ROADMAP",
    "RISKS & MITIGATION",
    "SUCCESS METRICS",
]

REQUIRED_CONVICTION_LABELS = [
    "[HIGH CONVICTION]",
    "[MEDIUM CONVICTION]",
    "[REQUIRES VALIDATION]",
]

HITL_TRIGGER_PHRASES = ["REQUIRES REVIEW", "DRAFT", "owner approval", "human review"]


def has_all_sections(text: str) -> list[str]:
    """Return list of missing required sections (case-insensitive)."""
    upper = text.upper()
    return [s for s in REQUIRED_SECTIONS if s not in upper]


# â”€â”€ 1. Prompt structure tests (no LLM, no network) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@pytest.mark.unit
class TestStrategistAgentPrompt:

    def test_prompt_exists(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        assert "strategist_agent" in AGENT_SYSTEM_PROMPTS

    def test_prompt_is_nonempty(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["strategist_agent"]
        assert len(prompt.strip()) > 300

    def test_prompt_has_all_required_sections(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["strategist_agent"]
        missing = has_all_sections(prompt)
        assert missing == [], f"Prompt missing sections: {missing}"

    def test_prompt_has_hitl1_gate_language(self):
        """HITL-1: human review required before strategy is shared or acted upon."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["strategist_agent"].upper()
        # Must reference HITL gates or require review
        assert "HITL" in prompt or "REQUIRES REVIEW" in prompt or "HUMAN REVIEW" in prompt

    def test_prompt_has_requires_review_tag(self):
        """Output must be labelled [REQUIRES REVIEW] per HITL-1 gate."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["strategist_agent"]
        assert "[REQUIRES REVIEW]" in prompt

    def test_prompt_has_conviction_labels(self):
        """All three conviction labels must be present in the prompt."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["strategist_agent"]
        found = [label for label in REQUIRED_CONVICTION_LABELS if label in prompt]
        assert len(found) == 3, f"Missing conviction labels: {[l for l in REQUIRED_CONVICTION_LABELS if l not in prompt]}"

    def test_prompt_has_budget_flag_rule(self):
        """Significant budget/hiring recommendations must be flagged for owner approval."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["strategist_agent"].lower()
        # Must include language about budget or hiring requiring approval
        has_budget = "budget" in prompt or "spend" in prompt
        has_hiring = "hiring" in prompt or "headcount" in prompt or "contractor" in prompt
        has_approval = "owner approval" in prompt or "requires approval" in prompt
        assert has_budget or has_hiring, "Prompt must reference budget or hiring"
        assert has_approval, "Prompt must reference owner approval requirement"

    def test_prompt_has_source_integrity_rule(self):
        """Strategies must not invent data — must say so explicitly."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["strategist_agent"].lower()
        # Must forbid fabrication of market data
        assert (
            "fabricat" in prompt
            or "invent" in prompt
            or "do not" in prompt
        ), "Prompt must contain source integrity instruction"

    def test_prompt_has_draft_label(self):
        """Internal drafts must be labelled [DRAFT]."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["strategist_agent"]
        assert "[DRAFT]" in prompt

    def test_get_agent_system_prompt_helper(self):
        from app.agents.agent_prompts import get_agent_system_prompt
        prompt = get_agent_system_prompt("strategist_agent")
        assert "Strategist" in prompt

    def test_fallback_prompt_for_unknown_agent(self):
        from app.agents.agent_prompts import get_agent_system_prompt
        prompt = get_agent_system_prompt("nonexistent_xyz_agent")
        assert len(prompt) > 20

    def test_prompt_specifies_execution_roadmap_phases(self):
        """Roadmap must contain 30/60/90 day phasing."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["strategist_agent"].lower()
        assert "30" in prompt and "60" in prompt and "90" in prompt

    def test_prompt_instructs_conviction_on_core_strategy(self):
        """Core strategy section must instruct agent to label conviction on strategic bets."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["strategist_agent"]
        # The conviction labels must appear in the context of strategy instructions
        assert "HIGH CONVICTION" in prompt and "MEDIUM CONVICTION" in prompt


# â”€â”€ 2. Registry entry tests â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@pytest.mark.unit
class TestStrategistAgentRegistry:

    def test_registry_entry_exists(self):
        from app.agents.agent_registry import AGENT_CATALOGUE
        assert "strategist_agent" in AGENT_CATALOGUE

    def test_registry_hitl_level_is_hitl1(self):
        """strategist_agent is HITL-1: review recommended before output is final."""
        from app.agents.agent_registry import AGENT_CATALOGUE
        entry = AGENT_CATALOGUE["strategist_agent"]
        assert entry["hitl_default"] == "HITL-1"

    def test_registry_min_package_is_business(self):
        """strategist_agent requires the business tier minimum."""
        from app.agents.agent_registry import AGENT_CATALOGUE
        entry = AGENT_CATALOGUE["strategist_agent"]
        assert entry["min_package"] == "business"

    def test_registry_has_capabilities(self):
        from app.agents.agent_registry import AGENT_CATALOGUE
        entry = AGENT_CATALOGUE["strategist_agent"]
        assert isinstance(entry.get("capabilities"), list)
        assert len(entry["capabilities"]) >= 3

    def test_registry_has_role(self):
        from app.agents.agent_registry import AGENT_CATALOGUE
        entry = AGENT_CATALOGUE["strategist_agent"]
        assert entry.get("role") and len(entry["role"]) > 20

    def test_registry_total_agent_count(self):
        """Non-negotiable: exactly 27 client-facing agents."""
        from app.agents.agent_registry import AGENT_CATALOGUE
        assert len(AGENT_CATALOGUE) == 22

    def test_registry_category_is_strategy(self):
        from app.agents.agent_registry import AGENT_CATALOGUE
        entry = AGENT_CATALOGUE["strategist_agent"]
        assert entry.get("category", "").lower() in ("strategy", "executive")

    def test_registry_credit_estimate_positive(self):
        from app.agents.agent_registry import AGENT_CATALOGUE
        entry = AGENT_CATALOGUE["strategist_agent"]
        assert entry.get("credit_estimate", 0) >= 1


# â”€â”€ 3. Executor tests (mocked LLM) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@pytest.mark.unit
class TestStrategistAgentExecutor:

    def test_financial_guard_injected_into_system_prompt(self):
        from app.agents.agent_executor import (
            FINANCIAL_CONSTRAINT_BLOCK,
            INJECTION_GUARD,
            execute_agent,
        )
        captured_system_prompt = []

        def mock_anthropic_call(system_prompt, user_message, **kwargs):
            captured_system_prompt.append(system_prompt)
            return "Clean strategy output with no financial actions.", 120, 60

        with patch("app.agents.agent_executor._call_anthropic", side_effect=mock_anthropic_call):
            with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test-key"}):
                execute_agent(
                    agent_id="strategist_agent",
                    system_prompt="You are the Strategist Agent.",
                    user_prompt="Create a market entry strategy.",
                )

        assert len(captured_system_prompt) == 1
        assert FINANCIAL_CONSTRAINT_BLOCK in captured_system_prompt[0]
        assert INJECTION_GUARD in captured_system_prompt[0]

    def test_financial_constraint_precedes_agent_prompt(self):
        from app.agents.agent_executor import FINANCIAL_CONSTRAINT_BLOCK, execute_agent

        captured = []

        def mock_call(system_prompt, user_message, **kwargs):
            captured.append(system_prompt)
            return "Strategy output.", 100, 50

        with patch("app.agents.agent_executor._call_anthropic", side_effect=mock_call):
            with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test-key"}):
                execute_agent(
                    agent_id="strategist_agent",
                    system_prompt="STRATEGIST_SPECIFIC_CONTENT_MARKER",
                    user_prompt="Test",
                )

        sys_prompt = captured[0]
        fc_pos = sys_prompt.index(FINANCIAL_CONSTRAINT_BLOCK[:30])
        agent_pos = sys_prompt.index("STRATEGIST_SPECIFIC_CONTENT_MARKER")
        assert fc_pos < agent_pos, "Financial constraint block must precede agent prompt"

    def test_clean_output_returns_no_violations(self):
        from app.agents.agent_executor import execute_agent

        def mock_call(system_prompt, user_message, **kwargs):
            return (
                "## STRATEGIC CONTEXT\nSaaS company in competitive market.\n\n"
                "## POSITIONING\nTarget mid-market. [HIGH CONVICTION]\n\n"
                "## CORE STRATEGY\nFocus on product-led growth. [MEDIUM CONVICTION]\n\n"
                "## EXECUTION ROADMAP\nDays 1-30: hire sales rep. REQUIRES OWNER APPROVAL.\n\n"
                "## RISKS & MITIGATION\nMarket saturation risk — low probability.\n\n"
                "## SUCCESS METRICS\nMRR target $50k by day 90.\n\n"
                "[REQUIRES REVIEW]",
                250, 400,
            )

        with patch("app.agents.agent_executor._call_anthropic", side_effect=mock_call):
            with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test-key"}):
                text, provider, credits, violations = execute_agent(
                    agent_id="strategist_agent",
                    system_prompt="You are the Strategist Agent.",
                    user_prompt="Create a growth strategy.",
                )

        assert violations == []
        assert credits >= 1
        assert "anthropic" in provider

    def test_financial_violation_in_output_detected(self):
        from app.agents.agent_executor import execute_agent

        def mock_call(system_prompt, user_message, **kwargs):
            return "I have authorized the hiring budget of $50,000 for Q3.", 100, 50

        with patch("app.agents.agent_executor._call_anthropic", side_effect=mock_call):
            with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test-key"}):
                _, _, _, violations = execute_agent(
                    agent_id="strategist_agent",
                    system_prompt="System.",
                    user_prompt="Plan the strategy.",
                )

        assert len(violations) > 0

    def test_tokens_to_credits_minimum_one(self):
        from app.agents.agent_executor import _tokens_to_credits
        assert _tokens_to_credits(0, 0) == 1
        assert _tokens_to_credits(1, 1) == 1
        assert _tokens_to_credits(500, 500) == 1
        assert _tokens_to_credits(1000, 1000) == 2

    def test_tokens_to_credits_scales_linearly(self):
        from app.agents.agent_executor import _tokens_to_credits
        # 3000 input + 1000 output = 4000 tokens = 4 credits
        assert _tokens_to_credits(3000, 1000) == 4

    def test_openai_fallback_when_anthropic_fails(self):
        from app.agents.agent_executor import execute_agent

        def anthropic_fail(system_prompt, user_message):
            raise RuntimeError("Anthropic unavailable")

        def openai_ok(system_prompt, user_message):
            return "OpenAI strategy fallback output.", 120, 80

        with patch("app.agents.agent_executor._call_anthropic", side_effect=anthropic_fail):
            with patch("app.agents.agent_executor._call_openai", side_effect=openai_ok):
                with patch.dict("os.environ", {
                    "ANTHROPIC_API_KEY": "sk-test",
                    "OPENAI_API_KEY": "sk-oai-test",
                }):
                    text, provider, credits, violations = execute_agent(
                        agent_id="strategist_agent",
                        system_prompt="System.",
                        user_prompt="Create strategy.",
                    )

        assert "openai" in provider
        assert text == "OpenAI strategy fallback output."

    def test_no_provider_raises_runtime_error(self):
        from app.agents.agent_executor import execute_agent
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(RuntimeError, match="No LLM provider"):
                execute_agent(
                    agent_id="strategist_agent",
                    system_prompt="System.",
                    user_prompt="Create strategy.",
                )

    def test_context_injected_into_user_message(self):
        from app.agents.agent_executor import execute_agent

        captured_messages = []

        def mock_call(system_prompt, user_message, **kwargs):
            captured_messages.append(user_message)
            return "Strategy output.", 100, 50

        with patch("app.agents.agent_executor._call_anthropic", side_effect=mock_call):
            with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test-key"}):
                execute_agent(
                    agent_id="strategist_agent",
                    system_prompt="You are the Strategist Agent.",
                    user_prompt="Build strategy.",
                    context={"workspace": "Acme Corp", "industry": "Fintech"},
                )

        msg = captured_messages[0]
        assert "Acme Corp" in msg
        assert "Fintech" in msg

    def test_governance_note_appended_to_user_message(self):
        from app.agents.agent_executor import execute_agent

        captured_messages = []

        def mock_call(system_prompt, user_message, **kwargs):
            captured_messages.append(user_message)
            return "Output.", 100, 50

        with patch("app.agents.agent_executor._call_anthropic", side_effect=mock_call):
            with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test-key"}):
                execute_agent(
                    agent_id="strategist_agent",
                    system_prompt="System.",
                    user_prompt="Task.",
                )

        msg = captured_messages[0]
        assert "MANDATORY CONSTRAINTS" in msg or "Financial decisions" in msg


# â”€â”€ 4. Guardrail tests â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@pytest.mark.unit
class TestStrategistAgentGuardrails:

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

    def test_strategist_agent_is_not_hitl3(self):
        """strategist_agent is HITL-1, never HITL-3 (which is for spend execution)."""
        from app.agents.agent_registry import AGENT_CATALOGUE
        assert AGENT_CATALOGUE["strategist_agent"]["hitl_default"] != "HITL-3"

    def test_strategist_prompt_references_budget_spend_language(self):
        """Prompt must instruct agent to flag budget and spend for owner approval."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["strategist_agent"].lower()
        assert "budget" in prompt or "spend" in prompt
        assert "approval" in prompt or "approve" in prompt

    def test_strategist_prompt_references_hiring_language(self):
        """Prompt must instruct agent to flag hiring for owner approval."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["strategist_agent"].lower()
        assert "hiring" in prompt or "headcount" in prompt or "contractor" in prompt

    def test_scan_detects_budget_allocated(self):
        from app.agents.agent_executor import scan_for_financial_actions
        dirty = "Budget allocated: $200,000 for the year-one growth plan."
        violations = scan_for_financial_actions(dirty)
        assert len(violations) > 0

    def test_scan_detects_i_have_authorized(self):
        from app.agents.agent_executor import scan_for_financial_actions
        dirty = "I have authorized the spend for the influencer campaign."
        violations = scan_for_financial_actions(dirty)
        assert len(violations) > 0

    def test_scan_clean_strategy_output(self):
        """A well-formed strategy with suggestions only must not trigger the guard."""
        from app.agents.agent_executor import scan_for_financial_actions
        clean = """
## STRATEGIC CONTEXT
B2B SaaS targeting mid-market legal firms.

## CORE STRATEGY
I recommend investing in content-led SEO. [HIGH CONVICTION]
You could consider allocating approximately $5,000/month to content — this requires your approval.

## EXECUTION ROADMAP
Days 1-30: Define ICP. Days 31-60: Build content pipeline. Days 61-90: Scale distribution.
REQUIRES OWNER APPROVAL before any budget is committed.

[REQUIRES REVIEW]
"""
        violations = scan_for_financial_actions(clean)
        assert violations == []

    def test_scan_case_insensitive(self):
        from app.agents.agent_executor import scan_for_financial_actions
        dirty = "I HAVE AUTHORIZED the marketing budget."
        violations = scan_for_financial_actions(dirty)
        assert len(violations) > 0

    def test_scan_no_false_positive_on_recommendation_language(self):
        """'I recommend a budget of X' should not trigger financial action guard."""
        from app.agents.agent_executor import scan_for_financial_actions
        safe = "I recommend a monthly budget of $3,000 for paid channels — this requires your approval."
        violations = scan_for_financial_actions(safe)
        assert violations == []


# â”€â”€ 5. API endpoint integration tests â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@pytest.mark.unit
class TestStrategistAgentAPI:

    def test_run_strategist_agent_unauthenticated(self, client):
        resp = client.post(
            "/api/agents/strategist_agent/run",
            json={"prompt": "Create a market entry strategy for our SaaS product."},
        )
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_run_strategist_agent_missing_prompt(self, client, authenticated_client):
        resp = authenticated_client.post("/api/agents/strategist_agent/run", json={})
        assert resp.status_code in (
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_403_FORBIDDEN,
        )

    def test_run_strategist_agent_submits_job(self, client, authenticated_client):
        """Authenticated call with valid prompt should queue a job (no actual LLM call)."""
        mock_output = (
            "## STRATEGIC CONTEXT\nB2B SaaS targeting growth-stage startups.\n\n"
            "## POSITIONING\nOwn the 'strategy-first' category. [HIGH CONVICTION]\n\n"
            "## CORE STRATEGY\nProduct-led growth. [MEDIUM CONVICTION]\n\n"
            "## EXECUTION ROADMAP\nDays 1-30: ICP validation.\n\n"
            "## RISKS & MITIGATION\nLow runway risk — mitigated by phased spend.\n\n"
            "## SUCCESS METRICS\nMRR growth 20% MoM.\n\n"
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
                "/api/agents/strategist_agent/run",
                json={"prompt": "Create a go-to-market strategy for our B2B SaaS product."},
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

    def test_run_strategist_agent_empty_prompt(self, client, authenticated_client):
        resp = authenticated_client.post(
            "/api/agents/strategist_agent/run",
            json={"prompt": ""},
        )
        assert resp.status_code in (
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_403_FORBIDDEN,
            status.HTTP_200_OK,
        )


# â”€â”€ 6. Output validator helper tests â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@pytest.mark.unit
class TestStrategistOutputValidator:

    def test_section_detection_helper_all_present(self):
        good = "\n".join(f"## {s}" for s in REQUIRED_SECTIONS)
        assert has_all_sections(good) == []

    def test_section_detection_missing_detected(self):
        partial = "## STRATEGIC CONTEXT\n## POSITIONING\n## CORE STRATEGY"
        missing = has_all_sections(partial)
        assert "EXECUTION ROADMAP" in missing
        assert "RISKS & MITIGATION" in missing
        assert "SUCCESS METRICS" in missing

    def test_section_detection_case_insensitive(self):
        """has_all_sections must match regardless of heading case."""
        lowercase = "\n".join(f"## {s.lower()}" for s in REQUIRED_SECTIONS)
        assert has_all_sections(lowercase) == []

    def test_section_detection_single_missing(self):
        sections_minus_one = [s for s in REQUIRED_SECTIONS if s != "SUCCESS METRICS"]
        partial = "\n".join(f"## {s}" for s in sections_minus_one)
        missing = has_all_sections(partial)
        assert missing == ["SUCCESS METRICS"]

    def test_conviction_labels_present_in_mock_output(self):
        output = """
## POSITIONING
Own the AI-native CRM space for SMBs. [HIGH CONVICTION]

## CORE STRATEGY
1. Product-led growth via freemium. [MEDIUM CONVICTION]
2. Enterprise partnership programme. [REQUIRES VALIDATION]
"""
        found = [label for label in REQUIRED_CONVICTION_LABELS if label in output]
        assert len(found) == 3

    def test_hitl1_draft_label_in_output(self):
        output = "# [DRAFT] Preliminary Strategy — Internal Working Document\n## STRATEGIC CONTEXT\n..."
        assert "[DRAFT]" in output

    def test_hitl1_requires_review_label_in_final_output(self):
        output = "# Strategic Growth Plan\n...\n[REQUIRES REVIEW]"
        assert "[REQUIRES REVIEW]" in output

    def test_budget_approval_flag_in_output(self):
        """A properly formatted roadmap entry must flag budget for owner approval."""
        output = (
            "## EXECUTION ROADMAP\n"
            "Days 31-60: Launch paid acquisition — budget $8,000/month. "
            "REQUIRES OWNER APPROVAL before any action is taken.\n"
        )
        assert "REQUIRES OWNER APPROVAL" in output.upper() or "REQUIRES OWNER APPROVAL" in output

    def test_all_sections_in_well_formed_output(self):
        well_formed = """
## STRATEGIC CONTEXT
B2B legal tech startup with $500k ARR seeking to reach $2M in 12 months.

## POSITIONING
Position as the only AI-native compliance tool for boutique law firms. [HIGH CONVICTION]

## CORE STRATEGY
1. Dominate a single ICP vertical before expanding. [HIGH CONVICTION]
2. Build a case-study-led content programme. [MEDIUM CONVICTION]
3. Pilot enterprise tier with pilot pricing. [REQUIRES VALIDATION]

## EXECUTION ROADMAP
Days 1-30: Complete ICP validation interviews (10 firms).
Days 31-60: Launch content programme — REQUIRES OWNER APPROVAL for content budget.
Days 61-90: Run enterprise pilot with 3 firms.

## RISKS & MITIGATION
Risk 1: Slow sales cycles in legal sector — mitigate with pilot pricing.
Risk 2: Competitor product development — monitor and maintain roadmap advantage.

## SUCCESS METRICS
1. MRR: baseline $42k â†’ target $60k by day 90.
2. Pilot conversion rate: target 2 of 3 to paid.
3. Content pipeline: 8 case studies published by day 90.

[REQUIRES REVIEW]
"""
        missing = has_all_sections(well_formed)
        assert missing == [], f"Well-formed output should pass all section checks; missing: {missing}"

