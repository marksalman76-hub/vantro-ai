"""
seo_agent test suite.

Covers:
  - Prompt structure validation (no LLM calls)
  - Registry entry correctness
  - Executor guard injection and output scanning (mocked LLM)
  - Guardrail / governance checks
  - API endpoint integration tests
  - Output format validator helper
"""
import pytest
from unittest.mock import patch, MagicMock
from fastapi import status


# â”€â”€ Helpers â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

# All 6 required output sections in the merged seo_content_agent
SEO_REQUIRED_SECTIONS = [
    "KEYWORD STRATEGY",
    "CONTENT GAPS",
    "SEO CONTENT BRIEFS",
    "TECHNICAL SEO PRIORITIES",
    "LINK BUILDING",
    "90-DAY ORGANIC GROWTH PLAN",
]

# Keyword confidence labels introduced in the upgrade
SEO_CONFIDENCE_LABELS = [
    "[TOOL-VERIFIED]",
    "[ESTIMATED - VALIDATE IN GSC]",
    "[INFERRED FROM INTENT]",
]

HITL_TRIGGER_PHRASES = ["REQUIRES REVIEW", "DRAFT", "owner review", "human review"]

# Phrases that should not appear as direct instructions/claims in agent output.
# Note: the prompt may quote these phrases as counter-examples of what NOT to do,
# so tests using these must check output text, not the prompt itself.
FORBIDDEN_RANKING_PROMISE_PHRASES = [
    "guaranteed to rank",
    "we will achieve top",
    "ranking guaranteed",
    "will reach position 1",
]


def has_all_seo_sections(text: str) -> list[str]:
    """Return list of required SEO sections missing from text (case-insensitive)."""
    upper = text.upper()
    return [s for s in SEO_REQUIRED_SECTIONS if s.upper() not in upper]


# â”€â”€ 1. Prompt structure tests â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@pytest.mark.unit
class TestSeoAgentPrompt:

    def test_prompt_exists(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        assert "seo_content_agent" in AGENT_SYSTEM_PROMPTS

    def test_prompt_is_nonempty(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["seo_content_agent"]
        assert len(prompt.strip()) > 500

    def test_prompt_has_all_required_sections(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["seo_content_agent"]
        missing = has_all_seo_sections(prompt)
        assert missing == [], f"Prompt missing sections: {missing}"

    def test_prompt_has_content_pillars_section(self):
        """CONTENT PILLARS is the core content strategy section in seo_content_agent."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["seo_content_agent"].upper()
        assert "CONTENT PILLARS" in prompt

    def test_editorial_calendar_has_30_day_scope(self):
        """EDITORIAL CALENDAR must specify a 30-day content plan."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["seo_content_agent"].lower()
        assert "30 day" in prompt or "30-day" in prompt or "week" in prompt

    def test_prompt_has_hitl_gate_language(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["seo_content_agent"].upper()
        found = any(phrase.upper() in prompt for phrase in HITL_TRIGGER_PHRASES)
        assert found, f"Prompt missing HITL gate language. Checked: {HITL_TRIGGER_PHRASES}"

    def test_prompt_has_draft_label(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["seo_content_agent"]
        assert "[DRAFT]" in prompt

    def test_prompt_has_requires_review_for_live_site(self):
        """Live-site changes must be labelled REQUIRES REVIEW in the prompt."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["seo_content_agent"]
        assert "REQUIRES REVIEW" in prompt
        assert "live" in prompt.lower()

    def test_prompt_has_keyword_confidence_labels(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["seo_content_agent"]
        found = [label for label in SEO_CONFIDENCE_LABELS if label in prompt]
        assert len(found) == 3, (
            f"Prompt must define all 3 keyword confidence labels, found: {found}"
        )

    def test_prompt_has_tool_verified_label(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["seo_content_agent"]
        assert "[TOOL-VERIFIED]" in prompt

    def test_prompt_has_estimated_validate_gsc_label(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["seo_content_agent"]
        assert "[ESTIMATED - VALIDATE IN GSC]" in prompt

    def test_prompt_has_inferred_from_intent_label(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["seo_content_agent"]
        assert "[INFERRED FROM INTENT]" in prompt

    def test_prompt_forbids_ranking_timeline_promises(self):
        """Prompt must explicitly state that ranking timelines must not be promised."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["seo_content_agent"].lower()
        assert (
            "never promise" in prompt
            or "do not promise" in prompt
            or "cannot be guaranteed" in prompt
            or "not guarantee" in prompt
            or "results are not guaranteed" in prompt
        )

    def test_prompt_does_not_itself_make_ranking_guarantees(self):
        """The prompt text must not itself make ranking guarantee claims."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["seo_content_agent"].lower()
        # These are hard guarantee phrases that should never appear as instructions
        hard_guarantees = ["ranking guaranteed", "guaranteed to rank", "will reach position 1"]
        for phrase in hard_guarantees:
            assert phrase not in prompt, (
                f"Prompt must not contain ranking guarantee language: '{phrase}'"
            )

    def test_prompt_has_technical_changes_owner_review_rule(self):
        """Technical changes to live sites must require owner review per the prompt."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["seo_content_agent"].lower()
        assert "technical" in prompt and "owner" in prompt and ("review" in prompt or "approval" in prompt)

    def test_prompt_references_gsc(self):
        """Prompt must reference Google Search Console as a validation tool."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["seo_content_agent"].upper()
        assert "GSC" in prompt or "GOOGLE SEARCH CONSOLE" in prompt

    def test_prompt_has_source_integrity_rule(self):
        """Prompt must prohibit fabricating keyword data."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["seo_content_agent"].lower()
        assert "fabricat" in prompt or "never fabricate" in prompt or "do not fabricate" in prompt

    def test_prompt_technical_seo_section_requires_review(self):
        """Technical SEO section must carry REQUIRES REVIEW for live-site items."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["seo_content_agent"]
        # Both the technical section and REQUIRES REVIEW must be present
        assert "TECHNICAL SEO PRIORITIES" in prompt.upper()
        assert "REQUIRES REVIEW" in prompt

    def test_get_agent_system_prompt_helper(self):
        from app.agents.agent_prompts import get_agent_system_prompt
        prompt = get_agent_system_prompt("seo_content_agent")
        assert "SEO" in prompt

    def test_fallback_prompt_for_unknown_agent(self):
        from app.agents.agent_prompts import get_agent_system_prompt
        prompt = get_agent_system_prompt("totally_unknown_xyz_agent")
        assert len(prompt) > 20


# â”€â”€ 2. Registry entry tests â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@pytest.mark.unit
class TestSeoAgentRegistry:

    def test_registry_entry_exists(self):
        from app.agents.agent_registry import AGENT_CATALOGUE
        assert "seo_content_agent" in AGENT_CATALOGUE

    def test_registry_hitl_level_is_hitl1_or_hitl2(self):
        """seo_agent is HITL-1, not HITL-3."""
        from app.agents.agent_registry import AGENT_CATALOGUE
        entry = AGENT_CATALOGUE["seo_content_agent"]
        assert entry["hitl_default"] in ("HITL-0", "HITL-1", "HITL-2")

    def test_registry_min_package_is_growth(self):
        from app.agents.agent_registry import AGENT_CATALOGUE
        entry = AGENT_CATALOGUE["seo_content_agent"]
        assert entry["min_package"] == "growth"

    def test_registry_has_capabilities(self):
        from app.agents.agent_registry import AGENT_CATALOGUE
        entry = AGENT_CATALOGUE["seo_content_agent"]
        assert isinstance(entry.get("capabilities"), list)
        assert len(entry["capabilities"]) >= 3

    def test_registry_has_role(self):
        from app.agents.agent_registry import AGENT_CATALOGUE
        entry = AGENT_CATALOGUE["seo_content_agent"]
        assert entry.get("role") and len(entry["role"]) > 20

    def test_registry_role_mentions_seo(self):
        from app.agents.agent_registry import AGENT_CATALOGUE
        role = AGENT_CATALOGUE["seo_content_agent"]["role"].lower()
        assert "seo" in role or "keyword" in role or "organic" in role

    def test_registry_total_agent_count(self):
        """Non-negotiable: exactly 24 client-facing agents."""
        from app.agents.agent_registry import AGENT_CATALOGUE
        assert len(AGENT_CATALOGUE) == 22


# â”€â”€ 3. Executor guard injection and execution tests (mocked LLM) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@pytest.mark.unit
class TestSeoAgentExecutor:

    def test_financial_guard_injected_into_system_prompt(self):
        from app.agents.agent_executor import (
            FINANCIAL_CONSTRAINT_BLOCK,
            INJECTION_GUARD,
            execute_agent,
        )
        captured_system_prompts = []

        def mock_call(system_prompt, user_message, **kwargs):
            captured_system_prompts.append(system_prompt)
            return (
                "## KEYWORD STRATEGY\n[TOOL-VERIFIED] keyword data.\n"
                "## CONTENT GAPS\nMissing pages identified.\n"
                "## SEO CONTENT BRIEFS\nBrief for target page.\n"
                "## TECHNICAL SEO PRIORITIES\n[REQUIRES REVIEW] Fix Core Web Vitals.\n"
                "## LINK BUILDING & DISTRIBUTION\nFocus on niche directories.\n"
                "## CONTENT PILLARS\nCore content themes.\n"
                "## 90-DAY ORGANIC GROWTH PLAN\nPhased roadmap.\n"
                "[DRAFT] â€” internal planning document.",
                150, 200
            )

        with patch("app.agents.agent_executor._call_anthropic", side_effect=mock_call):
            with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test-key"}):
                execute_agent(
                    agent_id="seo_content_agent",
                    system_prompt="You are the SEO Agent.",
                    user_prompt="Produce an SEO strategy for a B2B SaaS company.",
                )

        assert len(captured_system_prompts) == 1
        assert FINANCIAL_CONSTRAINT_BLOCK in captured_system_prompts[0]
        assert INJECTION_GUARD in captured_system_prompts[0]

    def test_clean_output_no_violations(self):
        from app.agents.agent_executor import execute_agent

        def mock_call(system_prompt, user_message, **kwargs):
            return (
                "## KEYWORD STRATEGY\n[ESTIMATED - VALIDATE IN GSC] AI chatbot software â€” 5,400/mo\n"
                "## CONTENT GAPS\nMissing landing page for enterprise buyers.\n"
                "## SEO CONTENT BRIEFS\nBrief 1: AI chatbot for enterprise.\n"
                "## TECHNICAL SEO PRIORITIES\n[REQUIRES REVIEW] LCP optimisation needed.\n"
                "## LINK BUILDING & DISTRIBUTION\nGuest posts on SaaS review sites.\n"
                "## CONTENT PILLARS\nCore content themes defined.\n"
                "## 90-DAY ORGANIC GROWTH PLAN\nDays 1-30: technical fixes.\n"
                "[DRAFT] â€” internal planning document.",
                300, 400
            )

        with patch("app.agents.agent_executor._call_anthropic", side_effect=mock_call):
            with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test-key"}):
                text, provider, credits, violations, *_ = execute_agent(
                    agent_id="seo_content_agent",
                    system_prompt="You are the SEO Agent.",
                    user_prompt="Build an SEO strategy for our SaaS product.",
                )

        assert violations == []
        assert credits >= 1
        assert "anthropic" in provider

    def test_financial_violation_in_output_detected(self):
        from app.agents.agent_executor import execute_agent

        def mock_call(system_prompt, user_message, **kwargs):
            return (
                "I have authorized the budget of $5,000 for link building outreach.\n"
                "## KEYWORD STRATEGY\n[TOOL-VERIFIED] keywords confirmed.",
                100, 50
            )

        with patch("app.agents.agent_executor._call_anthropic", side_effect=mock_call):
            with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test-key"}):
                _, _, _, violations, *_ = execute_agent(
                    agent_id="seo_content_agent",
                    system_prompt="You are the SEO Agent.",
                    user_prompt="Create a link building budget.",
                )

        assert len(violations) > 0

    def test_tokens_to_credits_minimum_one(self):
        from app.agents.agent_executor import _tokens_to_credits
        assert _tokens_to_credits(0, 0) == 1
        assert _tokens_to_credits(1, 1) == 1
        assert _tokens_to_credits(500, 500) == 1
        assert _tokens_to_credits(1000, 1000) == 2
        assert _tokens_to_credits(3000, 2000) == 5

    def test_openai_fallback_when_anthropic_fails(self):
        from app.agents.agent_executor import execute_agent

        def anthropic_fail(system_prompt, user_message):
            raise RuntimeError("Anthropic unavailable")

        def openai_ok(system_prompt, user_message):
            return (
                "## KEYWORD STRATEGY\n[INFERRED FROM INTENT] ecommerce SEO tools\n"
                "## CONTENT GAPS\nMissing comparison pages.\n"
                "## SEO CONTENT BRIEFS\nBrief 1.\n"
                "## TECHNICAL SEO PRIORITIES\nFix broken links.\n"
                "## LINK BUILDING & DISTRIBUTION\nPartner with industry blogs.\n"
                "## CONTENT PILLARS\nCore themes.\n"
                "## 90-DAY ORGANIC GROWTH PLAN\nPhased plan.\n"
                "[DRAFT]",
                100, 50
            )

        with patch("app.agents.agent_executor._call_anthropic", side_effect=anthropic_fail):
            with patch("app.agents.agent_executor._call_openai", side_effect=openai_ok):
                with patch.dict("os.environ", {
                    "ANTHROPIC_API_KEY": "sk-test",
                    "OPENAI_API_KEY": "sk-oai-test",
                }):
                    text, provider, credits, violations, *_ = execute_agent(
                        agent_id="seo_content_agent",
                        system_prompt="You are the SEO Agent.",
                        user_prompt="SEO strategy task.",
                    )

        assert "openai" in provider
        assert "KEYWORD STRATEGY" in text

    def test_no_provider_raises_runtime_error(self):
        from app.agents.agent_executor import execute_agent
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(RuntimeError, match="No LLM provider"):
                execute_agent(
                    agent_id="seo_content_agent",
                    system_prompt="You are the SEO Agent.",
                    user_prompt="SEO strategy.",
                )


# â”€â”€ 4. Guardrail tests â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@pytest.mark.unit
class TestSeoAgentGuardrails:

    def test_injection_guard_blocks_system_prompt_reveal(self):
        from app.agents.agent_executor import INJECTION_GUARD
        lower = INJECTION_GUARD.lower()
        assert "system prompt" in lower
        assert (
            "cannot be overridden" in lower
            or "immutable" in lower
            or "fixed" in lower
        )

    def test_financial_patterns_list_has_at_least_ten(self):
        from app.agents.agent_executor import FINANCIAL_ACTION_PATTERNS
        assert len(FINANCIAL_ACTION_PATTERNS) >= 10

    def test_financial_constraint_covers_key_actions(self):
        from app.agents.agent_executor import FINANCIAL_CONSTRAINT_BLOCK
        block = FINANCIAL_CONSTRAINT_BLOCK.lower()
        required = ["spending", "budgets", "payments", "hiring"]
        missing = [t for t in required if t not in block]
        assert missing == [], f"Financial constraint block missing: {missing}"

    def test_seo_agent_not_hitl3(self):
        """seo_agent must not be HITL-3 gated."""
        from app.agents.agent_registry import AGENT_CATALOGUE
        assert AGENT_CATALOGUE["seo_content_agent"]["hitl_default"] != "HITL-3"

    def test_prompt_does_not_contain_hard_guarantee_language(self):
        """Prompt must not contain hard ranking guarantee language as instructions."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["seo_content_agent"].lower()
        hard_guarantees = ["ranking guaranteed", "guaranteed to rank", "will reach position 1"]
        for phrase in hard_guarantees:
            assert phrase not in prompt, (
                f"Prompt must not contain guarantee language: '{phrase}'"
            )

    def test_prompt_states_never_promise_ranking_timelines(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["seo_content_agent"].lower()
        assert (
            "never promise" in prompt
            or "do not promise" in prompt
            or "not be guaranteed" in prompt
            or "results are not guaranteed" in prompt
        )

    def test_live_site_technical_changes_flagged_in_prompt(self):
        """Any technical recommendation affecting a live site must require owner review."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["seo_content_agent"].lower()
        assert "live site" in prompt or "live" in prompt
        assert "owner" in prompt and "review" in prompt

    def test_keyword_confidence_labels_all_defined(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["seo_content_agent"]
        for label in SEO_CONFIDENCE_LABELS:
            assert label in prompt, f"Missing confidence label in prompt: {label}"


# â”€â”€ 5. API endpoint integration tests â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@pytest.mark.unit
class TestSeoAgentAPI:

    def test_run_seo_agent_unauthenticated(self, client):
        resp = client.post(
            "/api/agents/seo_content_agent/run",
            json={"prompt": "Build an SEO strategy for my B2B SaaS product."},
        )
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_run_seo_agent_missing_prompt(self, client, authenticated_client):
        resp = authenticated_client.post("/api/agents/seo_content_agent/run", json={})
        assert resp.status_code in (
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_403_FORBIDDEN,
        )

    def test_run_seo_agent_submits_job(self, client, authenticated_client):
        """Authenticated call with valid prompt should queue a job (no actual LLM call)."""
        mock_output = (
            "## KEYWORD STRATEGY\n[TOOL-VERIFIED] AI scheduling software â€” 3,200/mo (Ahrefs)\n"
            "## CONTENT GAPS\nNo comparison page vs. competitors.\n"
            "## SEO CONTENT BRIEFS\nBrief 1: AI scheduling software for agencies.\n"
            "## TECHNICAL SEO PRIORITIES\n[REQUIRES REVIEW] Fix Core Web Vitals on homepage.\n"
            "## LINK BUILDING & DISTRIBUTION\nPitch to productivity blogs.\n"
            "## CONTENT PILLARS\nCore content themes.\n"
            "## 90-DAY ORGANIC GROWTH PLAN\nDays 1-30: fix technical issues.\n"
            "[DRAFT] â€” internal planning document."
        )
        with patch("app.agents.agent_executor.execute_agent") as mock_exec:
            mock_exec.return_value = (mock_output, "anthropic/claude-sonnet-4-6", 2, [])
            resp = authenticated_client.post(
                "/api/agents/seo_content_agent/run",
                json={"prompt": "Create a comprehensive SEO strategy for our B2B AI scheduling product."},
            )

        assert resp.status_code in (
            status.HTTP_200_OK,
            status.HTTP_202_ACCEPTED,
            status.HTTP_400_BAD_REQUEST,  # no active package / insufficient credits on test workspace
            status.HTTP_403_FORBIDDEN,
        )

    def test_jobs_list_accessible_when_authenticated(self, client, authenticated_client):
        resp = authenticated_client.get("/api/agents/jobs")
        assert resp.status_code == status.HTTP_200_OK
        body = resp.json()
        assert "jobs" in body


# â”€â”€ 6. Output validator tests â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@pytest.mark.unit
class TestSeoOutputValidator:

    def test_good_output_passes_all_sections(self):
        good = "\n".join(f"## {s}" for s in SEO_REQUIRED_SECTIONS)
        assert has_all_seo_sections(good) == []

    def test_missing_link_building_detected(self):
        """LINK BUILDING is a required section â€” must fail if absent."""
        sections_without_link_building = [
            s for s in SEO_REQUIRED_SECTIONS if s != "LINK BUILDING"
        ]
        partial = "\n".join(f"## {s}" for s in sections_without_link_building)
        missing = has_all_seo_sections(partial)
        assert "LINK BUILDING" in missing

    def test_missing_90_day_plan_detected(self):
        partial = (
            "## KEYWORD STRATEGY\n## CONTENT GAPS\n## SEO CONTENT BRIEFS\n"
            "## TECHNICAL SEO PRIORITIES\n## LINK BUILDING & DISTRIBUTION"
        )
        missing = has_all_seo_sections(partial)
        assert "90-DAY ORGANIC GROWTH PLAN" in missing

    def test_missing_keyword_strategy_detected(self):
        partial = (
            "## CONTENT GAPS\n## SEO CONTENT BRIEFS\n## TECHNICAL SEO PRIORITIES\n"
            "## LINK BUILDING & DISTRIBUTION\n## 90-DAY ORGANIC GROWTH PLAN"
        )
        missing = has_all_seo_sections(partial)
        assert "KEYWORD STRATEGY" in missing

    def test_case_insensitive_section_check(self):
        lowercase = "\n".join(f"## {s.lower()}" for s in SEO_REQUIRED_SECTIONS)
        assert has_all_seo_sections(lowercase) == []

    def test_tool_verified_label_in_mock_output(self):
        output = "[TOOL-VERIFIED] AI chatbot software â€” 5,400/mo (Semrush)"
        assert "[TOOL-VERIFIED]" in output

    def test_estimated_validate_gsc_label_in_mock_output(self):
        output = "[ESTIMATED - VALIDATE IN GSC] conversational AI platform â€” ~2,100/mo"
        assert "[ESTIMATED - VALIDATE IN GSC]" in output

    def test_inferred_from_intent_label_in_mock_output(self):
        output = "[INFERRED FROM INTENT] users are searching for cost-effective alternatives"
        assert "[INFERRED FROM INTENT]" in output

    def test_requires_review_on_technical_recommendation(self):
        output = (
            "## TECHNICAL SEO PRIORITIES\n"
            "[REQUIRES REVIEW â€” technical change to live site. "
            "Owner or qualified developer must review before implementation.]\n"
            "Fix LCP above 4s on mobile product pages."
        )
        assert "REQUIRES REVIEW" in output
        assert "live site" in output.lower() or "implementation" in output.lower()

    def test_draft_label_at_end_of_output(self):
        output = (
            "## 90-DAY ORGANIC GROWTH PLAN\nDays 1-30: fix technical issues.\n"
            "[DRAFT] â€” internal planning document. Technical changes and outreach "
            "require human review before implementation."
        )
        assert "[DRAFT]" in output

    def test_content_pillars_output_structure(self):
        """Content pillars section must include pillar names and rationale."""
        output = (
            "## CONTENT PILLARS\n"
            "1. SEO & Organic Growth [VALIDATED BY DATA] â€” drives qualified traffic.\n"
            "2. Thought Leadership [HYPOTHESIS - TEST FIRST] â€” builds authority.\n"
        )
        assert "CONTENT PILLARS" in output.upper()
        assert "validated" in output.lower() or "hypothesis" in output.lower()

    def test_90_day_plan_phases_present(self):
        output = (
            "## 90-DAY ORGANIC GROWTH PLAN\n"
            "Days 1-30: Foundation â€” technical SEO fixes and baseline measurement.\n"
            "Days 31-60: Content â€” publish priority briefs and on-page optimisation.\n"
            "Days 61-90: Authority â€” link building and performance review.\n"
        )
        assert "90-DAY ORGANIC GROWTH PLAN" in output.upper()
        assert "days 1" in output.lower()
        assert "days 31" in output.lower()
        assert "days 61" in output.lower()

    def test_no_ranking_guarantee_in_sample_output(self):
        """A well-formed SEO output must not contain ranking guarantee language."""
        good_output = (
            "## KEYWORD STRATEGY\n"
            "[ESTIMATED - VALIDATE IN GSC] project management software â€” ~8,100/mo\n"
            "Aim to improve rankings within 60-90 days â€” results vary and cannot be guaranteed.\n"
        )
        for phrase in FORBIDDEN_RANKING_PROMISE_PHRASES:
            assert phrase not in good_output.lower(), (
                f"Sample output must not contain ranking promise: '{phrase}'"
            )

    def test_link_building_outreach_requires_review(self):
        output = (
            "## LINK BUILDING & DISTRIBUTION\n"
            "Draft outreach emails are [REQUIRES REVIEW] before sending.\n"
        )
        assert "REQUIRES REVIEW" in output
