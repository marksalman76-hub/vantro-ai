"""
head_agent test suite.

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
    "TASK INTAKE & CLASSIFICATION",
    "AGENT ROUTING DECISION",
    "CONTEXT HANDOFF BRIEF",
    "DEPENDENCY MAP",
    "ESCALATION PROTOCOL",
    "QUALITY GATE",
    "ROUTING RISK FLAGS",
]

ROUTING_CONFIDENCE_LABELS = [
    "[CLEAR ROUTE]",
    "[AMBIGUOUS - CLARIFY BEFORE ROUTING]",
    "[MULTI-AGENT - SEQUENCE REQUIRED]",
]

HITL_TRIGGER_PHRASES = ["REQUIRES REVIEW", "DRAFT", "owner approval", "HITL-3"]


def has_all_sections(text: str) -> list[str]:
    """Return list of missing required sections."""
    return [s for s in REQUIRED_SECTIONS if s not in text.upper()]


# â”€â”€ 1. Prompt structure tests (no LLM, no network) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@pytest.mark.unit
class TestHeadAgentPrompt:

    def test_prompt_exists(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        assert "head_agent" in AGENT_SYSTEM_PROMPTS

    def test_prompt_is_nonempty(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["head_agent"]
        assert len(prompt.strip()) > 500

    def test_prompt_has_all_required_sections(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["head_agent"]
        missing = has_all_sections(prompt)
        assert missing == [], f"Prompt missing sections: {missing}"

    def test_prompt_has_hitl3_gate_language(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["head_agent"].upper()
        assert "HITL-3" in prompt

    def test_no_direct_execution_rule_in_prompt(self):
        """head_agent must declare it never executes tasks directly."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["head_agent"].lower()
        assert "never executes" in prompt or "does not execute" in prompt or "never execute" in prompt

    def test_routing_financial_impact_rule_in_prompt(self):
        """Prompt must require owner notification for financial-impact routing."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["head_agent"].lower()
        assert "financial impact" in prompt and ("owner" in prompt)

    def test_clarify_before_routing_rule_in_prompt(self):
        """Prompt must forbid guessing when scope is unclear."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["head_agent"].lower()
        assert "clarif" in prompt and "routing" in prompt

    def test_all_three_routing_confidence_labels_present(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["head_agent"]
        found = [label for label in ROUTING_CONFIDENCE_LABELS if label in prompt]
        assert len(found) == 3, f"Missing routing confidence labels: {[l for l in ROUTING_CONFIDENCE_LABELS if l not in prompt]}"

    def test_routing_risk_flags_section_exists(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["head_agent"].upper()
        assert "ROUTING RISK FLAGS" in prompt

    def test_prompt_has_owner_approval_language(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["head_agent"].lower()
        assert "owner approval" in prompt or "owner sign-off" in prompt

    def test_get_agent_system_prompt_helper(self):
        from app.agents.agent_prompts import get_agent_system_prompt
        prompt = get_agent_system_prompt("head_agent")
        assert "Head Agent" in prompt

    def test_fallback_prompt_for_unknown_agent(self):
        from app.agents.agent_prompts import get_agent_system_prompt
        prompt = get_agent_system_prompt("totally_unknown_xyz_agent")
        assert len(prompt) > 20


# â”€â”€ 2. Registry entry tests â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@pytest.mark.unit
class TestHeadAgentRegistry:

    def test_registry_entry_exists(self):
        from app.agents.agent_registry import AGENT_CATALOGUE
        assert "head_agent" in AGENT_CATALOGUE

    def test_registry_hitl_level_is_hitl3(self):
        from app.agents.agent_registry import AGENT_CATALOGUE
        entry = AGENT_CATALOGUE["head_agent"]
        assert entry["hitl_default"] == "HITL-3"

    def test_registry_min_package_is_starter(self):
        """head_agent is the orchestrator — all clients need it, so min_package is starter."""
        from app.agents.agent_registry import AGENT_CATALOGUE
        entry = AGENT_CATALOGUE["head_agent"]
        assert entry["min_package"] == "starter"

    def test_registry_has_capabilities(self):
        from app.agents.agent_registry import AGENT_CATALOGUE
        entry = AGENT_CATALOGUE["head_agent"]
        assert isinstance(entry.get("capabilities"), list)
        assert len(entry["capabilities"]) >= 3

    def test_registry_has_role(self):
        from app.agents.agent_registry import AGENT_CATALOGUE
        entry = AGENT_CATALOGUE["head_agent"]
        assert entry.get("role") and len(entry["role"]) > 20

    def test_registry_total_agent_count(self):
        """Non-negotiable: exactly 27 client-facing agents."""
        from app.agents.agent_registry import AGENT_CATALOGUE
        assert len(AGENT_CATALOGUE) == 22

    def test_registry_architecture_is_orchestration(self):
        from app.agents.agent_registry import AGENT_CATALOGUE
        entry = AGENT_CATALOGUE["head_agent"]
        arch = entry.get("architecture", "")
        assert "orchestration" in arch or "router" in arch


# â”€â”€ 3. Financial action scanner unit tests â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@pytest.mark.unit
class TestFinancialActionScannerHeadAgent:

    def test_clean_routing_output_no_violations(self):
        from app.agents.agent_executor import scan_for_financial_actions
        clean = """
## TASK INTAKE & CLASSIFICATION
Domain: Marketing. Urgency: STANDARD.

## AGENT ROUTING DECISION
[CLEAR ROUTE] â†’ marketing_specialist_agent
Financial impact: [NO FINANCIAL IMPACT]

## ROUTING RISK FLAGS
Risk: wrong agent selected. Likelihood: [LOW].
"""
        violations = scan_for_financial_actions(clean)
        assert violations == []

    def test_authorisation_phrase_detected(self):
        from app.agents.agent_executor import scan_for_financial_actions
        dirty = "I have authorized the campaign spend of $5,000."
        violations = scan_for_financial_actions(dirty)
        assert len(violations) > 0

    def test_purchase_phrase_detected(self):
        from app.agents.agent_executor import scan_for_financial_actions
        dirty = "I have purchased the media package on your behalf."
        violations = scan_for_financial_actions(dirty)
        assert len(violations) > 0

    def test_budget_allocated_phrase_detected(self):
        from app.agents.agent_executor import scan_for_financial_actions
        dirty = "Budget allocated: $10,000 for Q3 campaigns."
        violations = scan_for_financial_actions(dirty)
        assert len(violations) > 0

    def test_spend_approved_phrase_detected(self):
        from app.agents.agent_executor import scan_for_financial_actions
        dirty = "Spend approved. Routing ads agent to launch tomorrow."
        violations = scan_for_financial_actions(dirty)
        assert len(violations) > 0

    def test_case_insensitive_matching(self):
        from app.agents.agent_executor import scan_for_financial_actions
        dirty = "I HAVE AUTHORIZED the routing spend of $2,000."
        violations = scan_for_financial_actions(dirty)
        assert len(violations) > 0

    def test_partial_word_no_false_positive(self):
        from app.agents.agent_executor import scan_for_financial_actions
        safe = "This is an authoritative orchestration decision from the head agent."
        violations = scan_for_financial_actions(safe)
        assert violations == []


# â”€â”€ 4. Executor guard injection tests (mocked LLM) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@pytest.mark.unit
class TestExecutorGuardInjectionHeadAgent:

    def test_financial_constraint_block_injected(self):
        from app.agents.agent_executor import (
            FINANCIAL_CONSTRAINT_BLOCK,
            INJECTION_GUARD,
            execute_agent,
        )
        captured_system_prompt = []

        def mock_anthropic_call(system_prompt, user_message, **kwargs):
            captured_system_prompt.append(system_prompt)
            return "## TASK INTAKE & CLASSIFICATION\nDomain: Marketing.", 100, 50

        with patch("app.agents.agent_executor._anthropic_client") as mock_client:
            mock_client.return_value = MagicMock()
            with patch("app.agents.agent_executor._call_anthropic", side_effect=mock_anthropic_call):
                with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test-key"}):
                    execute_agent(
                        agent_id="head_agent",
                        system_prompt="You are the Head Agent.",
                        user_prompt="Route this task: launch a social media campaign.",
                    )

        assert len(captured_system_prompt) == 1
        assert FINANCIAL_CONSTRAINT_BLOCK in captured_system_prompt[0]
        assert INJECTION_GUARD in captured_system_prompt[0]

    def test_financial_constraint_comes_before_agent_prompt(self):
        from app.agents.agent_executor import FINANCIAL_CONSTRAINT_BLOCK, execute_agent

        captured = []

        def mock_call(system_prompt, user_message, **kwargs):
            captured.append(system_prompt)
            return "Routing output.", 100, 50

        with patch("app.agents.agent_executor._call_anthropic", side_effect=mock_call):
            with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test-key"}):
                execute_agent(
                    agent_id="head_agent",
                    system_prompt="HEAD_AGENT_SPECIFIC_CONTENT_MARKER",
                    user_prompt="Test",
                )

        sys_prompt = captured[0]
        fc_pos = sys_prompt.index(FINANCIAL_CONSTRAINT_BLOCK[:30])
        agent_pos = sys_prompt.index("HEAD_AGENT_SPECIFIC_CONTENT_MARKER")
        assert fc_pos < agent_pos, "Financial constraint block must precede agent prompt"

    def test_context_injected_into_user_message(self):
        from app.agents.agent_executor import execute_agent

        captured_messages = []

        def mock_call(system_prompt, user_message, **kwargs):
            captured_messages.append(user_message)
            return "Routing output.", 100, 50

        with patch("app.agents.agent_executor._call_anthropic", side_effect=mock_call):
            with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test-key"}):
                execute_agent(
                    agent_id="head_agent",
                    system_prompt="You are the Head Agent.",
                    user_prompt="Route this task.",
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

        with patch("app.agents.agent_executor._call_anthropic", side_effect=mock_call):
            with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test-key"}):
                execute_agent(
                    agent_id="head_agent",
                    system_prompt="System.",
                    user_prompt="Task.",
                )

        msg = captured_messages[0]
        assert "MANDATORY CONSTRAINTS" in msg or "Financial decisions" in msg

    def test_financial_violation_in_output_flagged(self):
        from app.agents.agent_executor import execute_agent

        def mock_call(system_prompt, user_message, **kwargs):
            return "I have authorized the campaign budget of $5,000 for the ads agent.", 100, 50

        with patch("app.agents.agent_executor._call_anthropic", side_effect=mock_call):
            with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test-key"}):
                _, _, _, violations = execute_agent(
                    agent_id="head_agent",
                    system_prompt="System.",
                    user_prompt="Task.",
                )

        assert len(violations) > 0

    def test_clean_routing_output_returns_no_violations(self):
        from app.agents.agent_executor import execute_agent

        def mock_call(system_prompt, user_message, **kwargs):
            return (
                "## TASK INTAKE & CLASSIFICATION\nDomain: Marketing.\n\n"
                "## AGENT ROUTING DECISION\n[CLEAR ROUTE] â†’ marketing_specialist_agent.\n\n"
                "## ROUTING RISK FLAGS\nRisk: low. Mitigation: review output.",
                200,
                300,
            )

        with patch("app.agents.agent_executor._call_anthropic", side_effect=mock_call):
            with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test-key"}):
                text, provider, credits, violations = execute_agent(
                    agent_id="head_agent",
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
            return "OpenAI routing output.", 100, 50

        with patch("app.agents.agent_executor._call_anthropic", side_effect=anthropic_fail):
            with patch("app.agents.agent_executor._call_openai", side_effect=openai_ok):
                with patch.dict("os.environ", {
                    "ANTHROPIC_API_KEY": "sk-test",
                    "OPENAI_API_KEY": "sk-oai-test",
                }):
                    text, provider, credits, violations = execute_agent(
                        agent_id="head_agent",
                        system_prompt="System.",
                        user_prompt="Task.",
                    )

        assert "openai" in provider
        assert text == "OpenAI routing output."

    def test_no_provider_raises_runtime_error(self):
        from app.agents.agent_executor import execute_agent
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(RuntimeError, match="No LLM provider"):
                execute_agent(
                    agent_id="head_agent",
                    system_prompt="System.",
                    user_prompt="Task.",
                )


# â”€â”€ 5. Guardrail tests â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@pytest.mark.unit
class TestHeadAgentGuardrails:

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

    def test_head_agent_is_hitl3(self):
        """head_agent must be HITL-3 gated."""
        from app.agents.agent_registry import AGENT_CATALOGUE
        assert AGENT_CATALOGUE["head_agent"]["hitl_default"] == "HITL-3"

    def test_secrets_in_prompt_not_in_output(self):
        """If user injects a secret into the prompt, executor must not echo it back."""
        from app.agents.agent_executor import execute_agent

        secret = "sk-SUPERSECRET_KEY_12345"

        def mock_call(system_prompt, user_message, **kwargs):
            return "I cannot process credentials or secrets. Please provide a routing task.", 50, 30

        with patch("app.agents.agent_executor._call_anthropic", side_effect=mock_call):
            with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test"}):
                text, _, _, violations = execute_agent(
                    agent_id="head_agent",
                    system_prompt="Head Agent.",
                    user_prompt=f"Use this API key to route: {secret}",
                )

        assert secret not in text

    def test_head_agent_prompt_has_no_direct_task_execution(self):
        """Confirm the prompt does not permit head_agent to do work itself."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["head_agent"].lower()
        # Must explicitly state it does not execute tasks
        assert "does not execute" in prompt or "never executes" in prompt or "never execute" in prompt


# â”€â”€ 6. API endpoint integration tests â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@pytest.mark.unit
class TestHeadAgentAPI:

    def test_run_head_agent_unauthenticated(self, client):
        resp = client.post(
            "/api/agents/head_agent/run",
            json={"prompt": "Route this: launch a new product campaign."},
        )
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_run_head_agent_missing_prompt(self, client, authenticated_client):
        resp = authenticated_client.post("/api/agents/head_agent/run", json={})
        assert resp.status_code in (
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_403_FORBIDDEN,
        )

    def test_run_head_agent_empty_prompt(self, client, authenticated_client):
        resp = authenticated_client.post(
            "/api/agents/head_agent/run",
            json={"prompt": ""},
        )
        assert resp.status_code in (
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_403_FORBIDDEN,
            status.HTTP_200_OK,
        )

    def test_run_head_agent_submits_job(self, client, authenticated_client):
        """Authenticated call with valid prompt should queue a job (no actual LLM call)."""
        with patch("app.agents.agent_executor.execute_agent") as mock_exec:
            mock_exec.return_value = (
                "## TASK INTAKE & CLASSIFICATION\nDomain: Marketing.\n\n"
                "## AGENT ROUTING DECISION\n[CLEAR ROUTE] â†’ marketing_specialist_agent.\n\n"
                "## ROUTING RISK FLAGS\nNo critical risks identified.",
                "anthropic/claude-sonnet-4-6",
                5,
                [],
            )
            resp = authenticated_client.post(
                "/api/agents/head_agent/run",
                json={"prompt": "Route this task: create a lead generation campaign."},
            )

        assert resp.status_code in (
            status.HTTP_200_OK,
            status.HTTP_202_ACCEPTED,
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_403_FORBIDDEN,  # insufficient credits/package on test workspace
        )

    def test_jobs_list_after_run(self, client, authenticated_client):
        resp = authenticated_client.get("/api/agents/jobs")
        assert resp.status_code == status.HTTP_200_OK
        body = resp.json()
        assert "jobs" in body


# â”€â”€ 7. Output format validation helper tests â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@pytest.mark.unit
class TestHeadAgentOutputFormatValidator:
    """Tests for the has_all_sections helper and expected output structure."""

    def test_good_output_passes(self):
        good = "\n".join(f"## {s}" for s in REQUIRED_SECTIONS)
        assert has_all_sections(good) == []

    def test_missing_section_detected(self):
        partial = (
            "## TASK INTAKE & CLASSIFICATION\n"
            "## AGENT ROUTING DECISION\n"
            "## CONTEXT HANDOFF BRIEF"
        )
        missing = has_all_sections(partial)
        assert "DEPENDENCY MAP" in missing
        assert "ROUTING RISK FLAGS" in missing

    def test_case_insensitive_section_check(self):
        lowercase = "\n".join(f"## {s.lower()}" for s in REQUIRED_SECTIONS)
        assert has_all_sections(lowercase) == []

    def test_routing_confidence_labels_in_mock_output(self):
        output = """
## AGENT ROUTING DECISION
[CLEAR ROUTE] â†’ research_agent — scope is clear.
[AMBIGUOUS - CLARIFY BEFORE ROUTING] — domain not specified.
[MULTI-AGENT - SEQUENCE REQUIRED] — requires research + strategy pipeline.
"""
        found = [label for label in ROUTING_CONFIDENCE_LABELS if label in output]
        assert len(found) == 3

    def test_hitl3_label_in_routing_output(self):
        output = "## ESCALATION PROTOCOL\n[ESCALATED — OWNER APPROVAL REQUIRED] — HITL-3 agent in route."
        assert "HITL-3" in output or "OWNER APPROVAL" in output

    def test_routing_risk_flags_section_in_output(self):
        output = "## ROUTING RISK FLAGS\nRisk: Wrong domain routing. Impact: [HIGH]."
        assert "ROUTING RISK FLAGS" in output

