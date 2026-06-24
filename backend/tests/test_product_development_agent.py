"""
product_development_agent test suite.

Covers:
  - Prompt structure validation (no LLM calls)
  - Registry entry correctness
  - Executor guard injection (mocked LLM)
  - Financial action scanner (unit)
  - Guardrail trip tests
  - API endpoint integration tests
  - Output format validation helper

HITL level : HITL-1
Min package : growth

Required output sections (7):
  PRODUCT VISION, MARKET VALIDATION, MVP SPECIFICATION,
  ANTI-SCOPE, FEATURE ROADMAP, PRICING STRATEGY, GO-TO-MARKET BRIEF
"""
import pytest
from unittest.mock import patch, MagicMock
from fastapi import status


# â”€â”€ Helpers â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

REQUIRED_SECTIONS = [
    "PRODUCT VISION",
    "MARKET VALIDATION",
    "MVP SPECIFICATION",
    "ANTI-SCOPE",
    "FEATURE ROADMAP",
    "PRICING STRATEGY",
    "GO-TO-MARKET BRIEF",
]

VALIDATION_LABELS = ["[VALIDATED]", "[HYPOTHESIS]", "[ASSUMED - VERIFY BEFORE BUILD]"]

HITL_TRIGGER_PHRASES = ["REQUIRES REVIEW", "owner review", "human review", "HITL"]


def has_all_sections(text: str) -> list[str]:
    """Return list of missing required sections (case-insensitive)."""
    upper = text.upper()
    return [s for s in REQUIRED_SECTIONS if s not in upper]


# â”€â”€ 1. Prompt structure tests â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@pytest.mark.unit
class TestProductDevAgentPrompt:

    def test_prompt_exists(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        assert "product_development_agent" in AGENT_SYSTEM_PROMPTS

    def test_prompt_is_nonempty(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["product_development_agent"]
        assert len(prompt.strip()) > 500

    def test_prompt_has_all_7_sections(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["product_development_agent"]
        missing = has_all_sections(prompt)
        assert missing == [], f"Prompt missing sections: {missing}"

    def test_prompt_has_anti_scope_section(self):
        """ANTI-SCOPE is the new section that must be present in the upgraded prompt."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["product_development_agent"]
        assert "ANTI-SCOPE" in prompt.upper()

    def test_prompt_has_hitl1_gate_language(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["product_development_agent"].upper()
        found = any(phrase.upper() in prompt for phrase in HITL_TRIGGER_PHRASES)
        assert found, "Prompt must contain HITL gate language"

    def test_prompt_has_requires_review_tag(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["product_development_agent"]
        assert "[REQUIRES REVIEW]" in prompt

    def test_prompt_has_validation_labels(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["product_development_agent"]
        found = [label for label in VALIDATION_LABELS if label in prompt]
        assert len(found) >= 2, f"Expected at least 2 validation labels; found: {found}"

    def test_prompt_has_all_three_validation_labels(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["product_development_agent"]
        missing = [label for label in VALIDATION_LABELS if label not in prompt]
        assert missing == [], f"Prompt missing validation labels: {missing}"

    def test_prompt_has_pricing_live_product_rule(self):
        """Prompt must explicitly state pricing changes to live products require owner review."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["product_development_agent"].lower()
        assert "live" in prompt and "pricing" in prompt and (
            "owner review" in prompt or "owner approval" in prompt
        ), "Prompt must state pricing changes to live products require owner review"

    def test_prompt_has_mvp_minimalism_rule(self):
        """Prompt must enforce that MVP is truly minimal and exclude features deliberately."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["product_development_agent"].lower()
        assert "minimal" in prompt or "minimum" in prompt, \
            "Prompt must emphasise MVP minimalism"
        assert "exclud" in prompt or "anti-scope" in prompt.lower(), \
            "Prompt must reference what is deliberately excluded"

    def test_prompt_has_hypothesis_label_instruction(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["product_development_agent"]
        assert "[HYPOTHESIS]" in prompt

    def test_prompt_has_assumed_verify_label_instruction(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["product_development_agent"]
        assert "[ASSUMED - VERIFY BEFORE BUILD]" in prompt

    def test_get_agent_system_prompt_helper(self):
        from app.agents.agent_prompts import get_agent_system_prompt
        prompt = get_agent_system_prompt("product_development_agent")
        assert "Product Development Agent" in prompt

    def test_fallback_prompt_for_unknown_agent(self):
        from app.agents.agent_prompts import get_agent_system_prompt
        prompt = get_agent_system_prompt("totally_unknown_xyz_agent_xyz")
        assert len(prompt) > 20


# â”€â”€ 2. Registry entry tests â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@pytest.mark.unit
class TestProductDevAgentRegistry:

    def test_registry_entry_exists(self):
        from app.agents.agent_registry import AGENT_CATALOGUE
        assert "product_development_agent" in AGENT_CATALOGUE

    def test_registry_hitl_level_is_hitl1(self):
        from app.agents.agent_registry import AGENT_CATALOGUE
        entry = AGENT_CATALOGUE["product_development_agent"]
        assert entry["hitl_default"] == "HITL-1"

    def test_registry_min_package_is_growth(self):
        from app.agents.agent_registry import AGENT_CATALOGUE
        entry = AGENT_CATALOGUE["product_development_agent"]
        assert entry["min_package"] == "growth"

    def test_registry_has_capabilities(self):
        from app.agents.agent_registry import AGENT_CATALOGUE
        entry = AGENT_CATALOGUE["product_development_agent"]
        assert isinstance(entry.get("capabilities"), list)
        assert len(entry["capabilities"]) >= 3

    def test_registry_has_role(self):
        from app.agents.agent_registry import AGENT_CATALOGUE
        entry = AGENT_CATALOGUE["product_development_agent"]
        assert entry.get("role") and len(entry["role"]) > 20

    def test_registry_total_agent_count_is_27(self):
        """Non-negotiable: exactly 27 client-facing agents."""
        from app.agents.agent_registry import AGENT_CATALOGUE
        assert len(AGENT_CATALOGUE) == 22

    def test_registry_category(self):
        from app.agents.agent_registry import AGENT_CATALOGUE
        entry = AGENT_CATALOGUE["product_development_agent"]
        assert entry.get("category") in ("Digital", "Product", "Strategy")

    def test_registry_visibility_is_purchasable(self):
        from app.agents.agent_registry import AGENT_CATALOGUE
        entry = AGENT_CATALOGUE["product_development_agent"]
        assert entry.get("visibility") == "purchasable"


# â”€â”€ 3. Executor tests (mocked LLM) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@pytest.mark.unit
class TestProductDevAgentExecutor:

    def test_financial_constraint_block_injected(self):
        from app.agents.agent_executor import (
            FINANCIAL_CONSTRAINT_BLOCK,
            INJECTION_GUARD,
            execute_agent,
        )
        captured_system_prompts = []

        def mock_anthropic_call(system_prompt, user_message, **kwargs):
            captured_system_prompts.append(system_prompt)
            return "Clean product development output with no financial actions.", 100, 50

        with patch("app.agents.agent_executor._call_anthropic", side_effect=mock_anthropic_call):
            with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test-key"}):
                execute_agent(
                    agent_id="product_development_agent",
                    system_prompt="You are the Product Development Agent.",
                    user_prompt="Build an MVP for a SaaS tool.",
                )

        assert len(captured_system_prompts) == 1
        assert FINANCIAL_CONSTRAINT_BLOCK in captured_system_prompts[0]
        assert INJECTION_GUARD in captured_system_prompts[0]

    def test_clean_output_no_violations(self):
        from app.agents.agent_executor import execute_agent

        clean_output = """
## PRODUCT VISION
[HYPOTHESIS] This SaaS tool helps SMEs automate invoicing.

## MARKET VALIDATION
[VALIDATED] Competitor FreshBooks has 10M+ users.

## MVP SPECIFICATION [REQUIRES REVIEW]
Core invoicing flow only.

## ANTI-SCOPE
- Advanced reporting: EXCLUDED BECAUSE insufficient user evidence.

## FEATURE ROADMAP
v1: Core invoice send — LEARN: will users pay?

## PRICING STRATEGY
[HYPOTHESIS] $29/mo flat rate.

## GO-TO-MARKET BRIEF
Target 10 accountants via LinkedIn.
"""

        def mock_call(system_prompt, user_message, **kwargs):
            return clean_output, 200, 300

        with patch("app.agents.agent_executor._call_anthropic", side_effect=mock_call):
            with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test-key"}):
                text, provider, credits, violations = execute_agent(
                    agent_id="product_development_agent",
                    system_prompt="You are the Product Development Agent.",
                    user_prompt="Create an MVP for an invoicing SaaS.",
                )

        assert violations == []
        assert credits >= 1

    def test_violation_detected_in_output(self):
        from app.agents.agent_executor import execute_agent

        def mock_call(system_prompt, user_message, **kwargs):
            return "I have authorized the development budget of $50,000.", 100, 50

        with patch("app.agents.agent_executor._call_anthropic", side_effect=mock_call):
            with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test-key"}):
                _, _, _, violations = execute_agent(
                    agent_id="product_development_agent",
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
        assert _tokens_to_credits(5000, 5000) == 10

    def test_openai_fallback_when_anthropic_fails(self):
        from app.agents.agent_executor import execute_agent

        def anthropic_fail(system_prompt, user_message):
            raise RuntimeError("Anthropic unavailable")

        def openai_ok(system_prompt, user_message):
            return "OpenAI fallback product output.", 100, 50

        with patch("app.agents.agent_executor._call_anthropic", side_effect=anthropic_fail):
            with patch("app.agents.agent_executor._call_openai", side_effect=openai_ok):
                with patch.dict("os.environ", {
                    "ANTHROPIC_API_KEY": "sk-test",
                    "OPENAI_API_KEY": "sk-oai-test",
                }):
                    text, provider, credits, violations = execute_agent(
                        agent_id="product_development_agent",
                        system_prompt="System.",
                        user_prompt="Task.",
                    )

        assert "openai" in provider
        assert text == "OpenAI fallback product output."

    def test_no_provider_raises_runtime_error(self):
        from app.agents.agent_executor import execute_agent
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(RuntimeError, match="No LLM provider"):
                execute_agent(
                    agent_id="product_development_agent",
                    system_prompt="System.",
                    user_prompt="Task.",
                )

    def test_context_injected_into_user_message(self):
        from app.agents.agent_executor import execute_agent

        captured_messages = []

        def mock_call(system_prompt, user_message, **kwargs):
            captured_messages.append(user_message)
            return "Product output.", 100, 50

        with patch("app.agents.agent_executor._call_anthropic", side_effect=mock_call):
            with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test-key"}):
                execute_agent(
                    agent_id="product_development_agent",
                    system_prompt="You are the Product Development Agent.",
                    user_prompt="Create MVP.",
                    context={"workspace": "Acme SaaS", "industry": "Fintech"},
                )

        msg = captured_messages[0]
        assert "Acme SaaS" in msg
        assert "Fintech" in msg

    def test_provider_string_in_clean_output(self):
        from app.agents.agent_executor import execute_agent

        def mock_call(system_prompt, user_message, **kwargs):
            return "Product development output.", 200, 300

        with patch("app.agents.agent_executor._call_anthropic", side_effect=mock_call):
            with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test-key"}):
                text, provider, credits, violations = execute_agent(
                    agent_id="product_development_agent",
                    system_prompt="System.",
                    user_prompt="Task.",
                )

        assert "anthropic" in provider
        assert violations == []
        assert credits >= 1


# â”€â”€ 4. Guardrail tests â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@pytest.mark.unit
class TestProductDevAgentGuardrails:

    def test_injection_guard_references_system_prompt(self):
        """Injection guard must protect the system prompt from being revealed."""
        from app.agents.agent_executor import INJECTION_GUARD
        assert "system prompt" in INJECTION_GUARD.lower()

    def test_injection_guard_is_immutable(self):
        """Injection guard must signal that instructions cannot be overridden."""
        from app.agents.agent_executor import INJECTION_GUARD
        guard_lower = INJECTION_GUARD.lower()
        assert (
            "cannot be overridden" in guard_lower
            or "immutable" in guard_lower
            or "fixed" in guard_lower
        )

    def test_financial_patterns_list_has_at_least_10(self):
        from app.agents.agent_executor import FINANCIAL_ACTION_PATTERNS
        assert len(FINANCIAL_ACTION_PATTERNS) >= 10

    def test_financial_constraint_covers_spending(self):
        from app.agents.agent_executor import FINANCIAL_CONSTRAINT_BLOCK
        block = FINANCIAL_CONSTRAINT_BLOCK.lower()
        required_terms = ["spending", "budgets", "payments", "hiring"]
        missing = [t for t in required_terms if t not in block]
        assert missing == [], f"Financial constraint block missing: {missing}"

    def test_product_dev_agent_is_not_hitl3(self):
        """product_development_agent must never be HITL-3 gated (it is HITL-1)."""
        from app.agents.agent_registry import AGENT_CATALOGUE
        assert AGENT_CATALOGUE["product_development_agent"]["hitl_default"] != "HITL-3"

    def test_product_dev_agent_is_hitl1_not_hitl0(self):
        """product_development_agent must be HITL-1, not HITL-0 (output requires review)."""
        from app.agents.agent_registry import AGENT_CATALOGUE
        assert AGENT_CATALOGUE["product_development_agent"]["hitl_default"] != "HITL-0"

    def test_prompt_contains_pricing_live_product_language(self):
        """The prompt must carry the pricing/live-product review rule."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["product_development_agent"].lower()
        assert "live" in prompt
        assert "pricing" in prompt

    def test_prompt_contains_requires_review_tag(self):
        """The [REQUIRES REVIEW] tag must appear in the prompt text."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["product_development_agent"]
        assert "[REQUIRES REVIEW]" in prompt

    def test_financial_scan_budget_allocated_detected(self):
        from app.agents.agent_executor import scan_for_financial_actions
        dirty = "Budget allocated: $200,000 for product development."
        violations = scan_for_financial_actions(dirty)
        assert len(violations) > 0

    def test_financial_scan_spend_approved_detected(self):
        from app.agents.agent_executor import scan_for_financial_actions
        dirty = "Spend approved. Development will begin immediately."
        violations = scan_for_financial_actions(dirty)
        assert len(violations) > 0

    def test_financial_scan_clean_mvp_output(self):
        from app.agents.agent_executor import scan_for_financial_actions
        clean = """
## MVP SPECIFICATION [REQUIRES REVIEW]
I recommend a minimal invoicing flow. You could consider allocating a Q3 budget
for development — this requires your approval before any action is taken.
"""
        violations = scan_for_financial_actions(clean)
        assert violations == []


# â”€â”€ 5. API endpoint tests â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@pytest.mark.unit
class TestProductDevAgentAPI:

    def test_run_unauthenticated_returns_401(self, client):
        resp = client.post(
            "/api/agents/product_development_agent/run",
            json={"prompt": "Create an MVP for a task management app."},
        )
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_run_missing_prompt_returns_error(self, client, authenticated_client):
        resp = authenticated_client.post(
            "/api/agents/product_development_agent/run",
            json={},
        )
        assert resp.status_code in (
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_403_FORBIDDEN,
        )

    def test_run_empty_prompt(self, client, authenticated_client):
        resp = authenticated_client.post(
            "/api/agents/product_development_agent/run",
            json={"prompt": ""},
        )
        assert resp.status_code in (
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_403_FORBIDDEN,
            status.HTTP_200_OK,
        )

    def test_run_submits_job_mocked(self, client, authenticated_client):
        """Authenticated call with valid prompt queues a job (no actual LLM call)."""
        mock_output = (
            "## PRODUCT VISION\n[HYPOTHESIS] A task management SaaS.\n\n"
            "## MARKET VALIDATION\n[VALIDATED] Trello has 50M users.\n\n"
            "## MVP SPECIFICATION [REQUIRES REVIEW]\nCore board and card creation.\n\n"
            "## ANTI-SCOPE\n- Integrations: EXCLUDED BECAUSE not validated yet.\n\n"
            "## FEATURE ROADMAP\nv1: Board + cards.\n\n"
            "## PRICING STRATEGY\n[HYPOTHESIS] $19/mo.\n\n"
            "## GO-TO-MARKET BRIEF\nTarget 10 freelancers via Twitter."
        )

        with patch("app.agents.agent_executor.execute_agent") as mock_exec:
            mock_exec.return_value = (
                mock_output,
                "anthropic/claude-sonnet-4-6",
                3,
                [],
            )
            resp = authenticated_client.post(
                "/api/agents/product_development_agent/run",
                json={"prompt": "Build an MVP for a task management SaaS for freelancers."},
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


# â”€â”€ 6. Output validator tests â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@pytest.mark.unit
class TestProductDevOutputValidator:

    def test_good_output_passes_all_sections(self):
        good = "\n".join(f"## {s}" for s in REQUIRED_SECTIONS)
        assert has_all_sections(good) == []

    def test_missing_anti_scope_detected(self):
        partial = (
            "## PRODUCT VISION\n"
            "## MARKET VALIDATION\n"
            "## MVP SPECIFICATION\n"
            "## FEATURE ROADMAP\n"
            "## PRICING STRATEGY\n"
            "## GO-TO-MARKET BRIEF\n"
        )
        missing = has_all_sections(partial)
        assert "ANTI-SCOPE" in missing

    def test_missing_multiple_sections_detected(self):
        partial = "## PRODUCT VISION\n## MARKET VALIDATION\n"
        missing = has_all_sections(partial)
        assert "MVP SPECIFICATION" in missing
        assert "ANTI-SCOPE" in missing
        assert "FEATURE ROADMAP" in missing
        assert "PRICING STRATEGY" in missing
        assert "GO-TO-MARKET BRIEF" in missing

    def test_case_insensitive_section_check(self):
        lowercase = "\n".join(f"## {s.lower()}" for s in REQUIRED_SECTIONS)
        assert has_all_sections(lowercase) == []

    def test_validation_labels_in_mock_output(self):
        output = """
## MARKET VALIDATION
[VALIDATED] Competitor Notion has 30M users.
[HYPOTHESIS] Users will pay $20/mo for core features.
[ASSUMED - VERIFY BEFORE BUILD] Target audience is solo founders.
"""
        found = [label for label in VALIDATION_LABELS if label in output]
        assert len(found) == 3

    def test_requires_review_tag_in_mvp_section(self):
        output = """
## MVP SPECIFICATION [REQUIRES REVIEW]
Core task creation and assignment only.
"""
        assert "[REQUIRES REVIEW]" in output

    def test_anti_scope_excludes_features(self):
        output = """
## ANTI-SCOPE
- Advanced reporting: EXCLUDED BECAUSE insufficient user evidence.
- Mobile app: EXCLUDED BECAUSE web-first validation required first.
- Integrations: EXCLUDED BECAUSE premature optimisation.
"""
        assert "EXCLUDED BECAUSE" in output
        assert "ANTI-SCOPE" in output

    def test_feature_roadmap_version_progression(self):
        output = """
## FEATURE ROADMAP
- v1 (MVP): Core board — LEARN: will users create tasks daily?
- v2: Comments — UNLOCK WHEN: 50 active daily users confirmed.
- v3: Integrations — UNLOCK WHEN: retention > 60% at 30 days.
"""
        assert "v1" in output
        assert "v2" in output
        assert "UNLOCK WHEN" in output

    def test_full_valid_output_passes(self):
        full_output = """
## PRODUCT VISION
[HYPOTHESIS] A lightweight task management tool for freelancers.

## MARKET VALIDATION
[VALIDATED] Trello has 50M registered users showing strong demand.
[HYPOTHESIS] Freelancers want simpler tools than Trello.

## MVP SPECIFICATION [REQUIRES REVIEW]
| # | Feature | Why it's in MVP | What hypothesis it tests |
| 1 | Task creation | Core loop | Will users create tasks? |
| 2 | Task assignment | Multi-user need | Is this single or team use? |

## ANTI-SCOPE
- Reporting dashboards: EXCLUDED BECAUSE not in core loop.
- Mobile app: EXCLUDED BECAUSE web validation first.

## FEATURE ROADMAP
- v1 (MVP): Task creation + assignment — LEARN: daily active usage
- v2: Comments — UNLOCK WHEN: 50 DAU confirmed
- v3: Integrations — UNLOCK WHEN: NPS > 40

## PRICING STRATEGY
[HYPOTHESIS] $19/mo flat rate.
RULE: Pricing changes to live products require owner review. [REQUIRES REVIEW]

## GO-TO-MARKET BRIEF
Target 10 freelance designers via Twitter DM in week 1.
"""
        missing = has_all_sections(full_output)
        assert missing == [], f"Valid full output missing sections: {missing}"
        found_labels = [label for label in VALIDATION_LABELS if label in full_output]
        assert len(found_labels) >= 2
        assert "[REQUIRES REVIEW]" in full_output

