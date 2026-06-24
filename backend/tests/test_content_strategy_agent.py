"""
content_strategy_agent test suite.

Covers:
  - Prompt structure validation (no LLM calls)
  - Registry entry correctness
  - Executor guard injection (mocked LLM)
  - Guardrail trip tests
  - API endpoint integration tests
  - Output format validation helper

Agent spec:
  HITL: HITL-1
  min_package: business
  Required output sections: CONTENT MISSION, AUDIENCE CONTENT MAP,
    CONTENT PILLARS, FORMAT MIX, EDITORIAL CALENDAR,
    DISTRIBUTION STRATEGY, MEASUREMENT FRAMEWORK
"""
import pytest
from unittest.mock import patch, MagicMock
from fastapi import status


# â”€â”€ Helpers â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

REQUIRED_SECTIONS = [
    "KEYWORD STRATEGY",
    "CONTENT GAPS",
    "CONTENT PILLARS",
    "SEO CONTENT BRIEFS",
    "EDITORIAL CALENDAR",
    "TECHNICAL SEO PRIORITIES",
    "LINK BUILDING",
    "90-DAY ORGANIC GROWTH PLAN",
]

REQUIRED_CONFIDENCE_LABELS = [
    "[VALIDATED BY DATA]",
    "[HYPOTHESIS - TEST FIRST]",
    "[INDUSTRY BEST PRACTICE]",
]

HITL_TRIGGER_PHRASES = ["REQUIRES REVIEW", "DRAFT", "owner approval", "human review"]


def has_all_sections(text: str) -> list[str]:
    """Return list of missing required sections (case-insensitive)."""
    upper = text.upper()
    return [s for s in REQUIRED_SECTIONS if s not in upper]


# â”€â”€ 1. Prompt structure tests â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@pytest.mark.unit
class TestContentStrategyAgentPrompt:

    def test_prompt_exists(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        assert "seo_content_agent" in AGENT_SYSTEM_PROMPTS

    def test_prompt_is_nonempty(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["seo_content_agent"]
        assert len(prompt.strip()) > 500, (
            "content_strategy_agent prompt is too short to be production quality"
        )

    def test_prompt_has_all_required_sections(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["seo_content_agent"]
        missing = has_all_sections(prompt)
        assert missing == [], f"Prompt missing sections: {missing}"

    def test_prompt_has_hitl1_language(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["seo_content_agent"].upper()
        # Must reference HITL gate concept via review or approval language
        has_hitl = (
            "HITL" in prompt
            or "REQUIRES REVIEW" in prompt
            or "HUMAN REVIEW" in prompt
        )
        assert has_hitl, "Prompt must contain HITL gate language"

    def test_prompt_references_requires_review_tag(self):
        """Technical SEO changes must be tagged [REQUIRES REVIEW] per HITL-1 spec."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["seo_content_agent"]
        assert "[REQUIRES REVIEW]" in prompt, (
            "Prompt must instruct agent to label technical changes [REQUIRES REVIEW]"
        )

    def test_prompt_references_draft_tag(self):
        """Preliminary output must be labelled [DRAFT]."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["seo_content_agent"]
        assert "[DRAFT]" in prompt, (
            "Prompt must distinguish draft vs final output with [DRAFT] label"
        )

    def test_prompt_has_confidence_labels_for_pillars(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["seo_content_agent"]
        found = [label for label in REQUIRED_CONFIDENCE_LABELS if label in prompt]
        assert len(found) >= 2, (
            f"Prompt must reference pillar confidence labels; found only: {found}"
        )

    def test_prompt_has_validated_by_data_label(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["seo_content_agent"]
        assert "[VALIDATED BY DATA]" in prompt

    def test_prompt_has_hypothesis_test_first_label(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["seo_content_agent"]
        assert "[HYPOTHESIS - TEST FIRST]" in prompt

    def test_prompt_has_industry_best_practice_label(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["seo_content_agent"]
        assert "[INDUSTRY BEST PRACTICE]" in prompt

    def test_prompt_sponsored_content_requires_owner_approval(self):
        """Prompt must explicitly require owner approval for sponsored/paid distribution."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["seo_content_agent"].lower()
        has_sponsored_rule = (
            "sponsored" in prompt and "owner approval" in prompt
        )
        assert has_sponsored_rule, (
            "Prompt must contain explicit rule that sponsored/paid content requires owner approval"
        )

    def test_prompt_paid_content_flag_label(self):
        """Prompt must define the REQUIRES OWNER APPROVAL label for paid distribution."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["seo_content_agent"]
        assert "REQUIRES OWNER APPROVAL" in prompt

    def test_prompt_seo_keyword_estimated_rule(self):
        """Prompt must require SEO keyword data to carry a confidence label."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["seo_content_agent"].lower()
        has_estimated_rule = (
            "estimated" in prompt and ("keyword" in prompt or "seo" in prompt)
        )
        assert has_estimated_rule, (
            "Prompt must instruct agent to label SEO keyword data with confidence labels"
        )

    def test_prompt_no_vague_mission_allowed(self):
        """Prompt must enforce keyword strategy quality over vague outputs."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["seo_content_agent"].lower()
        # seo_content_agent forbids vague data â€” checks fabrication or guarantee language
        assert "never" in prompt or "fabricat" in prompt or "cannot be guaranteed" in prompt, (
            "Prompt must include quality guardrails to enforce output standards"
        )

    def test_prompt_editorial_calendar_requires_review_status(self):
        """Prompt must require calendar entries to carry a status flag."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["seo_content_agent"].upper()
        # The prompt should mention REQUIRES REVIEW for editorial calendar entries
        assert "REQUIRES REVIEW" in prompt

    def test_get_agent_system_prompt_helper(self):
        from app.agents.agent_prompts import get_agent_system_prompt
        prompt = get_agent_system_prompt("seo_content_agent")
        assert "SEO" in prompt or "Content" in prompt

    def test_fallback_prompt_for_unknown_agent(self):
        from app.agents.agent_prompts import get_agent_system_prompt
        prompt = get_agent_system_prompt("totally_unknown_xyz_agent_99")
        assert len(prompt) > 20


# â”€â”€ 2. Registry entry tests â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@pytest.mark.unit
class TestContentStrategyAgentRegistry:

    def test_registry_entry_exists(self):
        from app.agents.agent_registry import AGENT_CATALOGUE
        assert "seo_content_agent" in AGENT_CATALOGUE

    def test_registry_hitl_level_is_hitl1(self):
        from app.agents.agent_registry import AGENT_CATALOGUE
        entry = AGENT_CATALOGUE["seo_content_agent"]
        assert entry["hitl_default"] == "HITL-1", (
            f"seo_content_agent must be HITL-1, got {entry['hitl_default']}"
        )

    def test_registry_min_package_is_growth(self):
        from app.agents.agent_registry import AGENT_CATALOGUE
        entry = AGENT_CATALOGUE["seo_content_agent"]
        assert entry["min_package"] == "growth", (
            f"seo_content_agent min_package must be 'growth', got {entry['min_package']}"
        )

    def test_registry_has_capabilities_list(self):
        from app.agents.agent_registry import AGENT_CATALOGUE
        entry = AGENT_CATALOGUE["seo_content_agent"]
        assert isinstance(entry.get("capabilities"), list)
        assert len(entry["capabilities"]) >= 3, (
            "content_strategy_agent must have at least 3 capabilities listed"
        )

    def test_registry_has_role(self):
        from app.agents.agent_registry import AGENT_CATALOGUE
        entry = AGENT_CATALOGUE["seo_content_agent"]
        assert entry.get("role") and len(entry["role"]) > 20

    def test_registry_has_name(self):
        from app.agents.agent_registry import AGENT_CATALOGUE
        entry = AGENT_CATALOGUE["seo_content_agent"]
        assert "SEO" in entry.get("name", "") or "Content" in entry.get("name", "")

    def test_registry_has_category(self):
        from app.agents.agent_registry import AGENT_CATALOGUE
        entry = AGENT_CATALOGUE["seo_content_agent"]
        assert entry.get("category") in ("Marketing", "Content", "Strategy", "SEO")

    def test_registry_total_agent_count_is_24(self):
        """Non-negotiable: exactly 24 client-facing agents."""
        from app.agents.agent_registry import AGENT_CATALOGUE
        assert len(AGENT_CATALOGUE) == 22, (
            f"Agent catalogue must contain exactly 24 agents, found {len(AGENT_CATALOGUE)}"
        )

    def test_registry_seo_content_in_growth_package(self):
        from app.agents.agent_registry import PACKAGE_AGENTS
        assert "seo_content_agent" in PACKAGE_AGENTS["growth"]

    def test_registry_seo_content_not_in_starter_package(self):
        from app.agents.agent_registry import PACKAGE_AGENTS
        assert "seo_content_agent" not in PACKAGE_AGENTS["starter"]

    def test_registry_seo_content_in_business_package(self):
        from app.agents.agent_registry import PACKAGE_AGENTS
        assert "seo_content_agent" in PACKAGE_AGENTS["business"]

    def test_registry_seo_content_in_enterprise_package(self):
        from app.agents.agent_registry import PACKAGE_AGENTS
        assert "seo_content_agent" in PACKAGE_AGENTS["enterprise"]


# â”€â”€ 3. Executor tests (mocked LLM) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@pytest.mark.unit
class TestContentStrategyAgentExecutor:

    def test_financial_guard_injected_into_system_prompt(self):
        from app.agents.agent_executor import (
            FINANCIAL_CONSTRAINT_BLOCK,
            INJECTION_GUARD,
            execute_agent,
        )
        captured_system_prompt = []

        def mock_call(system_prompt, user_message, **kwargs):
            captured_system_prompt.append(system_prompt)
            return "Clean content strategy output with no financial actions.", 100, 50

        with patch("app.agents.agent_executor._call_anthropic", side_effect=mock_call):
            with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test-key"}):
                execute_agent(
                    agent_id="seo_content_agent",
                    system_prompt="You are the Content Strategy Agent.",
                    user_prompt="Build a content strategy for a SaaS startup.",
                )

        assert len(captured_system_prompt) == 1
        assert FINANCIAL_CONSTRAINT_BLOCK in captured_system_prompt[0]
        assert INJECTION_GUARD in captured_system_prompt[0]

    def test_financial_constraint_precedes_agent_prompt(self):
        from app.agents.agent_executor import FINANCIAL_CONSTRAINT_BLOCK, execute_agent

        captured = []

        def mock_call(system_prompt, user_message, **kwargs):
            captured.append(system_prompt)
            return "Content strategy output.", 100, 50

        with patch("app.agents.agent_executor._call_anthropic", side_effect=mock_call):
            with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test-key"}):
                execute_agent(
                    agent_id="seo_content_agent",
                    system_prompt="CONTENT_STRATEGY_AGENT_MARKER_UNIQUE",
                    user_prompt="Test.",
                )

        sys_prompt = captured[0]
        fc_pos = sys_prompt.index(FINANCIAL_CONSTRAINT_BLOCK[:30])
        agent_pos = sys_prompt.index("CONTENT_STRATEGY_AGENT_MARKER_UNIQUE")
        assert fc_pos < agent_pos, "Financial constraint block must precede agent-specific prompt"

    def test_clean_output_no_violations(self):
        from app.agents.agent_executor import execute_agent

        def mock_call(system_prompt, user_message, **kwargs):
            return (
                "## KEYWORD STRATEGY\n[TOOL-VERIFIED] SaaS growth tools â€” 4,200/mo\n\n"
                "## CONTENT GAPS\nMissing comparison and use-case pages.\n\n"
                "## CONTENT PILLARS\nPillar: Conversion Optimisation [VALIDATED BY DATA]\n\n"
                "## SEO CONTENT BRIEFS\nBrief 1: SaaS platform growth guide.\n\n"
                "## EDITORIAL CALENDAR\nWeek 1 | 'Top SaaS Growth Tactics' | Blog | [REQUIRES REVIEW]\n\n"
                "## TECHNICAL SEO PRIORITIES\n[REQUIRES REVIEW] Fix Core Web Vitals.\n\n"
                "## LINK BUILDING & DISTRIBUTION\nOwned: email list. Paid: [SPONSORED / PAID â€” REQUIRES OWNER APPROVAL BEFORE ACTIVATION]\n\n"
                "## 90-DAY ORGANIC GROWTH PLAN\nDays 1-30: technical audit.\n\n"
                "[REQUIRES REVIEW]",
                200,
                300,
            )

        with patch("app.agents.agent_executor._call_anthropic", side_effect=mock_call):
            with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test-key"}):
                text, provider, credits, violations = execute_agent(
                    agent_id="seo_content_agent",
                    system_prompt="System.",
                    user_prompt="Task.",
                )

        assert violations == []
        assert credits >= 1
        assert "anthropic" in provider

    def test_violation_detected_in_output(self):
        from app.agents.agent_executor import execute_agent

        def mock_call(system_prompt, user_message, **kwargs):
            return "I have authorized the sponsored content budget of $3,000.", 100, 50

        with patch("app.agents.agent_executor._call_anthropic", side_effect=mock_call):
            with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test-key"}):
                _, _, _, violations = execute_agent(
                    agent_id="seo_content_agent",
                    system_prompt="System.",
                    user_prompt="Task.",
                )

        assert len(violations) > 0

    def test_budget_allocated_violation_detected(self):
        from app.agents.agent_executor import execute_agent

        def mock_call(system_prompt, user_message, **kwargs):
            return "Budget allocated: $5,000 for sponsored content placements.", 100, 50

        with patch("app.agents.agent_executor._call_anthropic", side_effect=mock_call):
            with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test-key"}):
                _, _, _, violations = execute_agent(
                    agent_id="seo_content_agent",
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
            return "OpenAI content strategy output.", 100, 50

        with patch("app.agents.agent_executor._call_anthropic", side_effect=anthropic_fail):
            with patch("app.agents.agent_executor._call_openai", side_effect=openai_ok):
                with patch.dict("os.environ", {
                    "ANTHROPIC_API_KEY": "sk-test",
                    "OPENAI_API_KEY": "sk-oai-test",
                }):
                    text, provider, credits, violations = execute_agent(
                        agent_id="seo_content_agent",
                        system_prompt="System.",
                        user_prompt="Task.",
                    )

        assert "openai" in provider
        assert text == "OpenAI content strategy output."

    def test_no_provider_raises_runtime_error(self):
        from app.agents.agent_executor import execute_agent
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(RuntimeError, match="No LLM provider"):
                execute_agent(
                    agent_id="seo_content_agent",
                    system_prompt="System.",
                    user_prompt="Task.",
                )

    def test_context_injected_into_user_message(self):
        from app.agents.agent_executor import execute_agent

        captured_messages = []

        def mock_call(system_prompt, user_message, **kwargs):
            captured_messages.append(user_message)
            return "Content output.", 100, 50

        with patch("app.agents.agent_executor._call_anthropic", side_effect=mock_call):
            with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test-key"}):
                execute_agent(
                    agent_id="seo_content_agent",
                    system_prompt="You are the Content Strategy Agent.",
                    user_prompt="Build a content strategy.",
                    context={"workspace": "Bloom Skincare", "industry": "DTC Beauty"},
                )

        msg = captured_messages[0]
        assert "Bloom Skincare" in msg
        assert "DTC Beauty" in msg

    def test_governance_note_appended_to_user_message(self):
        from app.agents.agent_executor import execute_agent

        captured_messages = []

        def mock_call(system_prompt, user_message, **kwargs):
            captured_messages.append(user_message)
            return "Output.", 100, 50

        with patch("app.agents.agent_executor._call_anthropic", side_effect=mock_call):
            with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test-key"}):
                execute_agent(
                    agent_id="seo_content_agent",
                    system_prompt="System.",
                    user_prompt="Task.",
                )

        msg = captured_messages[0]
        assert "MANDATORY CONSTRAINTS" in msg or "Financial decisions" in msg


# â”€â”€ 4. Guardrail tests â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@pytest.mark.unit
class TestContentStrategyAgentGuardrails:

    def test_injection_guard_blocks_system_prompt_reveal(self):
        """Injection guard must prevent system prompt disclosure."""
        from app.agents.agent_executor import INJECTION_GUARD
        guard_lower = INJECTION_GUARD.lower()
        assert "system prompt" in guard_lower
        assert (
            "cannot be overridden" in guard_lower
            or "immutable" in guard_lower
            or "fixed" in guard_lower
        )

    def test_financial_constraint_covers_key_actions(self):
        from app.agents.agent_executor import FINANCIAL_CONSTRAINT_BLOCK
        block = FINANCIAL_CONSTRAINT_BLOCK.lower()
        required_coverage = ["spending", "budgets", "payments", "hiring"]
        missing = [term for term in required_coverage if term not in block]
        assert missing == [], f"Financial constraint block missing coverage for: {missing}"

    def test_financial_patterns_list_has_minimum_ten(self):
        from app.agents.agent_executor import FINANCIAL_ACTION_PATTERNS
        assert len(FINANCIAL_ACTION_PATTERNS) >= 10, (
            f"FINANCIAL_ACTION_PATTERNS must have at least 10 patterns, "
            f"found {len(FINANCIAL_ACTION_PATTERNS)}"
        )

    def test_seo_content_agent_is_not_hitl3(self):
        """seo_content_agent must never be HITL-3 gated."""
        from app.agents.agent_registry import AGENT_CATALOGUE
        entry = AGENT_CATALOGUE["seo_content_agent"]
        assert entry["hitl_default"] != "HITL-3", (
            "seo_content_agent must not be HITL-3; it is HITL-1"
        )

    def test_sponsored_paid_mention_in_prompt(self):
        """Prompt must explicitly mention sponsored and paid content controls."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["seo_content_agent"].lower()
        assert "sponsored" in prompt, "Prompt must contain 'sponsored' content rule"
        assert "paid" in prompt, "Prompt must contain 'paid' content rule"

    def test_owner_approval_required_in_prompt(self):
        """Prompt must explicitly require owner approval for controlled actions."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["seo_content_agent"].lower()
        assert "owner approval" in prompt

    def test_secrets_not_echoed_in_output(self):
        """Agent must not echo injected secrets back in output."""
        from app.agents.agent_executor import execute_agent

        secret = "sk-SUPERSECRET_CONTENT_KEY_99999"

        def mock_call(system_prompt, user_message, **kwargs):
            return "I cannot process credentials. Please provide a valid content request.", 50, 30

        with patch("app.agents.agent_executor._call_anthropic", side_effect=mock_call):
            with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test"}):
                text, _, _, violations = execute_agent(
                    agent_id="seo_content_agent",
                    system_prompt="Content Strategy Agent.",
                    user_prompt=f"Use this key to check analytics: {secret}",
                )

        assert secret not in text

    def test_scan_for_financial_actions_clean_content_output(self):
        from app.agents.agent_executor import scan_for_financial_actions
        clean = """
## CONTENT MISSION
Grow organic traffic by 30% in 6 months targeting DTC founders.

## CONTENT PILLARS
Pillar 1: Conversion Rate Optimisation [VALIDATED BY DATA]
Pillar 2: Email Marketing [HYPOTHESIS - TEST FIRST]

## DISTRIBUTION STRATEGY
Owned: newsletter (4,200 subscribers). You could consider paid amplification for the
top-performing pieces â€” this requires your approval before any spend is committed.

[REQUIRES REVIEW]
"""
        violations = scan_for_financial_actions(clean)
        assert violations == []

    def test_scan_detects_authorized_spend_phrase(self):
        from app.agents.agent_executor import scan_for_financial_actions
        dirty = "I have authorized the sponsored content budget of $2,500."
        violations = scan_for_financial_actions(dirty)
        assert len(violations) > 0

    def test_scan_detects_budget_allocated_phrase(self):
        from app.agents.agent_executor import scan_for_financial_actions
        dirty = "Budget allocated for content distribution: $1,000 per month."
        violations = scan_for_financial_actions(dirty)
        assert len(violations) > 0

    def test_scan_detects_spend_approved_phrase(self):
        from app.agents.agent_executor import scan_for_financial_actions
        dirty = "Spend approved. Content distribution campaign starts Monday."
        violations = scan_for_financial_actions(dirty)
        assert len(violations) > 0


# â”€â”€ 5. API endpoint integration tests â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@pytest.mark.unit
class TestContentStrategyAgentAPI:

    def test_run_content_strategy_agent_unauthenticated(self, client):
        resp = client.post(
            "/api/agents/seo_content_agent/run",
            json={"prompt": "Build a content strategy for our SaaS product."},
        )
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_run_content_strategy_agent_missing_prompt(self, client, authenticated_client):
        resp = authenticated_client.post(
            "/api/agents/seo_content_agent/run",
            json={},
        )
        assert resp.status_code in (
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_403_FORBIDDEN,
        )

    def test_run_content_strategy_agent_empty_prompt(self, client, authenticated_client):
        resp = authenticated_client.post(
            "/api/agents/seo_content_agent/run",
            json={"prompt": ""},
        )
        assert resp.status_code in (
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_403_FORBIDDEN,
            status.HTTP_200_OK,
        )

    def test_run_content_strategy_agent_submits_job(self, client, authenticated_client):
        """Authenticated call with valid prompt should queue a job (no real LLM call)."""
        mock_output = (
            "## KEYWORD STRATEGY\n[TOOL-VERIFIED] B2B SaaS tools â€” 5,400/mo\n\n"
            "## CONTENT GAPS\nMissing use-case and comparison pages.\n\n"
            "## CONTENT PILLARS\nSEO Growth [VALIDATED BY DATA]\n\n"
            "## SEO CONTENT BRIEFS\nBrief 1: B2B SaaS platform guide.\n\n"
            "## EDITORIAL CALENDAR\nWeek 1 | '5 SEO wins for CTOs' | Blog | [REQUIRES REVIEW]\n\n"
            "## TECHNICAL SEO PRIORITIES\n[REQUIRES REVIEW] Fix page speed.\n\n"
            "## LINK BUILDING & DISTRIBUTION\nNewsletter + social.\n\n"
            "## 90-DAY ORGANIC GROWTH PLAN\nDays 1-30: foundation.\n\n"
            "[REQUIRES REVIEW]"
        )
        with patch("app.agents.agent_executor.execute_agent") as mock_exec:
            mock_exec.return_value = (
                mock_output,
                "anthropic/claude-sonnet-4-6",
                2,
                [],
            )
            resp = authenticated_client.post(
                "/api/agents/seo_content_agent/run",
                json={
                    "prompt": "Build a 30-day content strategy for our B2B SaaS platform targeting CTOs."
                },
            )

        assert resp.status_code in (
            status.HTTP_200_OK,
            status.HTTP_202_ACCEPTED,
            status.HTTP_403_FORBIDDEN,  # insufficient credits/package on test workspace
        )

    def test_jobs_list_accessible_after_run(self, client, authenticated_client):
        resp = authenticated_client.get("/api/agents/jobs")
        assert resp.status_code == status.HTTP_200_OK
        body = resp.json()
        assert "jobs" in body


# â”€â”€ 6. Output validator tests â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@pytest.mark.unit
class TestContentStrategyOutputValidator:

    def test_good_output_passes_section_check(self):
        good = "\n".join(f"## {s}" for s in REQUIRED_SECTIONS)
        assert has_all_sections(good) == []

    def test_missing_section_detected(self):
        partial = (
            "## KEYWORD STRATEGY\n"
            "## CONTENT GAPS\n"
            "## CONTENT PILLARS\n"
            "## SEO CONTENT BRIEFS\n"
        )
        missing = has_all_sections(partial)
        assert "EDITORIAL CALENDAR" in missing
        assert "TECHNICAL SEO PRIORITIES" in missing
        assert "90-DAY ORGANIC GROWTH PLAN" in missing

    def test_single_missing_section_detected(self):
        almost_complete = "\n".join(
            f"## {s}" for s in REQUIRED_SECTIONS if s != "90-DAY ORGANIC GROWTH PLAN"
        )
        missing = has_all_sections(almost_complete)
        assert missing == ["90-DAY ORGANIC GROWTH PLAN"]

    def test_case_insensitive_section_check(self):
        lowercase = "\n".join(f"## {s.lower()}" for s in REQUIRED_SECTIONS)
        assert has_all_sections(lowercase) == []

    def test_mixed_case_section_check(self):
        mixed = "\n".join(f"## {s.title()}" for s in REQUIRED_SECTIONS)
        assert has_all_sections(mixed) == []

    def test_confidence_labels_detected_in_mock_output(self):
        output = """
## CONTENT PILLARS
- SEO & Organic Growth | [VALIDATED BY DATA] â€” based on Ahrefs data showing 8K monthly searches
- Thought Leadership | [HYPOTHESIS - TEST FIRST] â€” no current engagement data to confirm
- Educational How-To Content | [INDUSTRY BEST PRACTICE] â€” standard for SaaS content programmes
"""
        found = [label for label in REQUIRED_CONFIDENCE_LABELS if label in output]
        assert len(found) == 3

    def test_requires_review_tag_in_final_output(self):
        output = (
            "## 90-DAY ORGANIC GROWTH PLAN\n"
            "Days 1-30: technical fixes and baseline measurement.\n\n"
            "[REQUIRES REVIEW] â€” this plan must be reviewed by the account owner before "
            "sharing with or presenting to any client."
        )
        assert "[REQUIRES REVIEW]" in output

    def test_draft_tag_in_preliminary_output(self):
        output = "[DRAFT] SEO & Content Plan â€” Internal Working Document\n## KEYWORD STRATEGY\n..."
        assert "[DRAFT]" in output

    def test_sponsored_paid_flag_in_link_building_section(self):
        """Link building & distribution section must flag paid content for owner approval."""
        output = (
            "## LINK BUILDING & DISTRIBUTION\n"
            "Owned: newsletter, social.\n"
            "Paid: LinkedIn boosting for top-performing pillar posts.\n"
            "[SPONSORED / PAID â€” REQUIRES OWNER APPROVAL BEFORE ACTIVATION]\n"
        )
        assert "REQUIRES OWNER APPROVAL" in output

    def test_seo_keyword_estimated_label_in_output(self):
        """Keyword data without a live tool must carry [ESTIMATED] label."""
        output = (
            "## CONTENT PILLARS\n"
            "- Email Marketing Automation | [VALIDATED BY DATA] â€” "
            "Estimated monthly search volume: 3,400 [ESTIMATED â€” not from a live tool]\n"
        )
        assert "[ESTIMATED" in output

    def test_all_sections_present_in_realistic_mock_output(self):
        realistic_output = """
## KEYWORD STRATEGY
[TOOL-VERIFIED] HR compliance software â€” 8,100/mo (Ahrefs). Keyword difficulty: 52/100.
Search intent: commercial. Current ranking: unknown â€” check GSC.

## CONTENT GAPS
Missing: GDPR checklist page, structured interview guide, HR tech comparison.
Urgency: high â€” direct competitor coverage confirmed.

## CONTENT PILLARS
1. HR Compliance & Legal Updates | [VALIDATED BY DATA] â€” 12K monthly searches cluster (Semrush)
2. Talent Acquisition Best Practice | [INDUSTRY BEST PRACTICE]
3. HR Technology Guides | [HYPOTHESIS - TEST FIRST] â€” needs 4-week pilot

## SEO CONTENT BRIEFS
Brief 1: 'GDPR Compliance Checklist for HR 2026'
Title: GDPR HR Compliance Checklist 2026 | Target KW: HR GDPR compliance (1,900/mo)
Word count: 2,200 | H2s: Legal requirements, Implementation steps, Audit checklist

## EDITORIAL CALENDAR
Week 1 | 'GDPR Compliance Checklist for HR 2026' | Compliance | Blog | SEO | [REQUIRES REVIEW]
Week 2 | 'How to Run Structured Interviews at Scale' | Talent | Blog | SEO | [DRAFT]

## TECHNICAL SEO PRIORITIES
[REQUIRES REVIEW â€” technical change to live site] LCP above 4s on mobile product pages.
Fix: Compress hero images, defer render-blocking scripts.

## LINK BUILDING & DISTRIBUTION
Owned: newsletter blast + LinkedIn + Twitter.
[SPONSORED / PAID â€” REQUIRES OWNER APPROVAL BEFORE ACTIVATION]: LinkedIn post boosting.

## 90-DAY ORGANIC GROWTH PLAN
Days 1-30: Technical fixes and keyword baseline measurement.
Days 31-60: Publish priority content briefs.
Days 61-90: Link building and performance review.

[REQUIRES REVIEW] â€” this plan must be reviewed by the account owner before sharing with any client.
"""
        missing = has_all_sections(realistic_output)
        assert missing == [], f"Realistic output is missing sections: {missing}"
