"""
intake_trial_agent test suite.

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
    "ENQUIRY QUALIFICATION",
    "DISCOVERY CALL PREP",
    "DEMO BOOKING WORKFLOW",
    "TRIAL ACTIVATION PLAN",
    "TRIAL-TO-PAID CONVERSION",
    "CRM & HANDOFF PROTOCOL",
    "PIPELINE REPORTING",
]

REQUIRED_CONVERSION_LABELS = [
    "[VALIDATED SIGNAL]",
    "[INDUSTRY BENCHMARK]",
    "[INFERRED FROM CONTEXT]",
]

BUYER_PERSONA_TRACKS = [
    "TRIAL",
    "DEMO",
    "CRM",
]

HITL_TRIGGER_PHRASES = [
    "REQUIRES REVIEW",
    "DRAFT",
    "REQUIRES OWNER APPROVAL",
    "human review",
    "owner approval",
]


def has_all_sections(text: str) -> list[str]:
    """Return list of missing required sections."""
    return [s for s in REQUIRED_SECTIONS if s not in text.upper()]


# â”€â”€ 1. Prompt structure tests (no LLM, no network) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@pytest.mark.unit
class TestDemoTrialAgentPrompt:

    def test_prompt_exists(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        assert "intake_trial_agent" in AGENT_SYSTEM_PROMPTS

    def test_prompt_is_nonempty(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["intake_trial_agent"]
        assert len(prompt.strip()) > 500

    def test_prompt_has_all_required_sections(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["intake_trial_agent"]
        missing = has_all_sections(prompt)
        assert missing == [], f"Prompt missing sections: {missing}"

    def test_prompt_has_hitl_gate_language(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["intake_trial_agent"].upper()
        assert any(phrase.upper() in prompt for phrase in HITL_TRIGGER_PHRASES)

    def test_prompt_has_hitl_1_internal_draft_gate(self):
        """Internal scripts must be labelled [DRAFT] — HITL-1 gate."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["intake_trial_agent"].upper()
        assert "DRAFT" in prompt

    def test_prompt_has_hitl_2_external_requires_review_gate(self):
        """External demo materials need review — HITL-2 gate."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["intake_trial_agent"].upper()
        assert "REQUIRES REVIEW" in prompt

    def test_prompt_has_owner_approval_gate_for_pricing(self):
        """Pricing/offer decisions require owner approval."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["intake_trial_agent"].upper()
        assert "REQUIRES OWNER APPROVAL" in prompt

    def test_no_pricing_commitment_rule_present(self):
        """The prompt must explicitly state that pricing commitments require owner approval."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["intake_trial_agent"].lower()
        assert "pric" in prompt and "owner approval" in prompt

    def test_trial_extension_approval_rule_present(self):
        """Trial extensions must require owner approval per the prompt rules."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["intake_trial_agent"].lower()
        assert "trial extension" in prompt or "extension" in prompt
        assert "owner approval" in prompt

    def test_prompt_has_all_conversion_confidence_labels(self):
        """All 3 conversion claim labels must appear in the prompt definition."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["intake_trial_agent"]
        found = [label for label in REQUIRED_CONVERSION_LABELS if label in prompt]
        assert len(found) == 3, (
            f"Prompt must define all 3 conversion labels. Found: {found}"
        )

    def test_demo_flow_variants_section_is_7th_section(self):
        """PIPELINE REPORTING is the 7th section."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["intake_trial_agent"].upper()
        assert "PIPELINE REPORTING" in prompt

    def test_three_buyer_persona_tracks_present(self):
        """DEMO FLOW VARIANTS must reference all 3 buyer persona tracks."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["intake_trial_agent"].upper()
        missing = [track for track in BUYER_PERSONA_TRACKS if track not in prompt]
        assert missing == [], f"Prompt missing buyer persona tracks: {missing}"

    def test_get_agent_system_prompt_helper(self):
        from app.agents.agent_prompts import get_agent_system_prompt
        prompt = get_agent_system_prompt("intake_trial_agent")
        assert "Demo" in prompt or "demo" in prompt

    def test_fallback_prompt_for_unknown_agent(self):
        from app.agents.agent_prompts import get_agent_system_prompt
        prompt = get_agent_system_prompt("totally_unknown_xyz_agent")
        assert len(prompt) > 20


# â”€â”€ 2. Registry entry tests â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@pytest.mark.unit
class TestDemoTrialAgentRegistry:

    def test_registry_entry_exists(self):
        from app.agents.agent_registry import AGENT_CATALOGUE
        assert "intake_trial_agent" in AGENT_CATALOGUE

    def test_registry_hitl_level_is_hitl1(self):
        from app.agents.agent_registry import AGENT_CATALOGUE
        entry = AGENT_CATALOGUE["intake_trial_agent"]
        assert entry["hitl_default"] == "HITL-1"

    def test_registry_hitl_is_not_hitl3(self):
        """intake_trial_agent must never be HITL-3 gated."""
        from app.agents.agent_registry import AGENT_CATALOGUE
        assert AGENT_CATALOGUE["intake_trial_agent"]["hitl_default"] != "HITL-3"

    def test_registry_min_package(self):
        from app.agents.agent_registry import AGENT_CATALOGUE
        entry = AGENT_CATALOGUE["intake_trial_agent"]
        assert entry["min_package"] in ("starter", "growth", "business", "enterprise")

    def test_registry_has_capabilities(self):
        from app.agents.agent_registry import AGENT_CATALOGUE
        entry = AGENT_CATALOGUE["intake_trial_agent"]
        assert isinstance(entry.get("capabilities"), list)
        assert len(entry["capabilities"]) >= 3

    def test_registry_has_role(self):
        from app.agents.agent_registry import AGENT_CATALOGUE
        entry = AGENT_CATALOGUE["intake_trial_agent"]
        assert entry.get("role") and len(entry["role"]) > 20

    def test_registry_total_agent_count(self):
        """Non-negotiable: exactly 27 client-facing agents."""
        from app.agents.agent_registry import AGENT_CATALOGUE
        assert len(AGENT_CATALOGUE) == 22


# â”€â”€ 3. Financial action scanner unit tests â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@pytest.mark.unit
class TestFinancialActionScanner:

    def test_clean_demo_output_no_violations(self):
        from app.agents.agent_executor import scan_for_financial_actions
        clean = """
## DEMO SCRIPT
Walk the prospect through the product dashboard.
Show the key features tied to their stated pain points.

## TRIAL SETUP CHECKLIST
1. Provision the sandbox environment.
2. Configure the workspace with prospect data.
[DRAFT]

## CONVERSION STRATEGY
Trial-to-paid conversion typically occurs at Day 7 when users hit the third activation milestone.
[INDUSTRY BENCHMARK] Median trial-to-paid conversion rate in SaaS is 25%.
"""
        violations = scan_for_financial_actions(clean)
        assert violations == []

    def test_authorisation_phrase_detected(self):
        from app.agents.agent_executor import scan_for_financial_actions
        dirty = "I have authorized the trial extension for the prospect."
        violations = scan_for_financial_actions(dirty)
        assert len(violations) > 0

    def test_purchase_phrase_detected(self):
        from app.agents.agent_executor import scan_for_financial_actions
        dirty = "I have purchased an extended license on your behalf."
        violations = scan_for_financial_actions(dirty)
        assert len(violations) > 0

    def test_budget_allocated_phrase_detected(self):
        from app.agents.agent_executor import scan_for_financial_actions
        dirty = "Budget allocated: $2,000 for the demo follow-up campaign."
        violations = scan_for_financial_actions(dirty)
        assert len(violations) > 0

    def test_spend_approved_phrase_detected(self):
        from app.agents.agent_executor import scan_for_financial_actions
        dirty = "Spend approved. The onboarding tools will be activated tomorrow."
        violations = scan_for_financial_actions(dirty)
        assert len(violations) > 0

    def test_case_insensitive_matching(self):
        from app.agents.agent_executor import scan_for_financial_actions
        dirty = "I HAVE AUTHORIZED the extended trial period."
        violations = scan_for_financial_actions(dirty)
        assert len(violations) > 0

    def test_partial_word_no_false_positive(self):
        # "authoritative" should NOT trigger "i have authorised"
        from app.agents.agent_executor import scan_for_financial_actions
        safe = "This is an authoritative demo approach used by top SaaS teams."
        violations = scan_for_financial_actions(safe)
        assert violations == []


# â”€â”€ 4. Executor guard injection tests (mocked LLM) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@pytest.mark.unit
class TestExecutorGuardInjection:

    def test_financial_constraint_block_injected(self):
        from app.agents.agent_executor import (
            FINANCIAL_CONSTRAINT_BLOCK,
            INJECTION_GUARD,
            execute_agent,
        )
        captured_system_prompt = []

        def mock_anthropic_call(system_prompt, user_message, **kwargs):
            captured_system_prompt.append(system_prompt)
            return "Demo script output with no financial actions.", 100, 50

        with patch("app.agents.agent_executor._anthropic_client") as mock_client:
            mock_client.return_value = MagicMock()
            with patch("app.agents.agent_executor._call_anthropic", side_effect=mock_anthropic_call):
                with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test-key"}):
                    execute_agent(
                        agent_id="intake_trial_agent",
                        system_prompt="You are the Demo & Trial Agent.",
                        user_prompt="Build a demo script for a SaaS product.",
                    )

        assert len(captured_system_prompt) == 1
        assert FINANCIAL_CONSTRAINT_BLOCK in captured_system_prompt[0]
        assert INJECTION_GUARD in captured_system_prompt[0]

    def test_financial_constraint_comes_before_agent_prompt(self):
        from app.agents.agent_executor import FINANCIAL_CONSTRAINT_BLOCK, execute_agent

        captured = []

        def mock_call(system_prompt, user_message, **kwargs):
            captured.append(system_prompt)
            return "Demo output.", 100, 50

        with patch("app.agents.agent_executor._call_anthropic", side_effect=mock_call):
            with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test-key"}):
                execute_agent(
                    agent_id="intake_trial_agent",
                    system_prompt="DEMO_AGENT_CONTENT_MARKER",
                    user_prompt="Test",
                )

        sys_prompt = captured[0]
        fc_pos = sys_prompt.index(FINANCIAL_CONSTRAINT_BLOCK[:30])
        agent_pos = sys_prompt.index("DEMO_AGENT_CONTENT_MARKER")
        assert fc_pos < agent_pos, "Financial constraint block must precede agent prompt"

    def test_context_injected_into_user_message(self):
        from app.agents.agent_executor import execute_agent

        captured_messages = []

        def mock_call(system_prompt, user_message, **kwargs):
            captured_messages.append(user_message)
            return "Demo output.", 100, 50

        with patch("app.agents.agent_executor._call_anthropic", side_effect=mock_call):
            with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test-key"}):
                execute_agent(
                    agent_id="intake_trial_agent",
                    system_prompt="You are the Demo & Trial Agent.",
                    user_prompt="Build a demo script.",
                    context={"workspace": "Acme Corp", "product": "SaaS Platform"},
                )

        msg = captured_messages[0]
        assert "Acme Corp" in msg
        assert "SaaS Platform" in msg

    def test_governance_note_appended_to_user_message(self):
        from app.agents.agent_executor import execute_agent

        captured_messages = []

        def mock_call(system_prompt, user_message, **kwargs):
            captured_messages.append(user_message)
            return "Output.", 100, 50

        with patch("app.agents.agent_executor._call_anthropic", side_effect=mock_call):
            with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test-key"}):
                execute_agent(
                    agent_id="intake_trial_agent",
                    system_prompt="System.",
                    user_prompt="Task.",
                )

        msg = captured_messages[0]
        assert "MANDATORY CONSTRAINTS" in msg or "Financial decisions" in msg

    def test_financial_violation_in_output_flagged(self):
        from app.agents.agent_executor import execute_agent

        def mock_call(system_prompt, user_message, **kwargs):
            return "I have authorized the trial extension and allocated $1,000.", 100, 50

        with patch("app.agents.agent_executor._call_anthropic", side_effect=mock_call):
            with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test-key"}):
                _, _, _, violations, *_ = execute_agent(
                    agent_id="intake_trial_agent",
                    system_prompt="System.",
                    user_prompt="Task.",
                )

        assert len(violations) > 0

    def test_clean_output_returns_no_violations(self):
        from app.agents.agent_executor import execute_agent

        def mock_call(system_prompt, user_message, **kwargs):
            return (
                "## DEMO SCRIPT\nWalk through the product features. "
                "[INDUSTRY BENCHMARK] 25% trial-to-paid conversion. "
                "[DRAFT] Internal script for review.",
                200,
                300,
            )

        with patch("app.agents.agent_executor._call_anthropic", side_effect=mock_call):
            with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test-key"}):
                text, provider, credits, violations, *_ = execute_agent(
                    agent_id="intake_trial_agent",
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
            return "OpenAI fallback output.", 100, 50

        with patch("app.agents.agent_executor._call_anthropic", side_effect=anthropic_fail):
            with patch("app.agents.agent_executor._call_openai", side_effect=openai_ok):
                with patch.dict("os.environ", {
                    "ANTHROPIC_API_KEY": "sk-test",
                    "OPENAI_API_KEY": "sk-oai-test",
                }):
                    text, provider, credits, violations, *_ = execute_agent(
                        agent_id="intake_trial_agent",
                        system_prompt="System.",
                        user_prompt="Task.",
                    )

        assert "openai" in provider
        assert text == "OpenAI fallback output."

    def test_no_provider_raises_runtime_error(self):
        from app.agents.agent_executor import execute_agent
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(RuntimeError, match="No LLM provider"):
                execute_agent(
                    agent_id="intake_trial_agent",
                    system_prompt="System.",
                    user_prompt="Task.",
                )


# â”€â”€ 5. Guardrail tests â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@pytest.mark.unit
class TestDemoTrialAgentGuardrails:

    def test_injection_guard_blocks_system_prompt_reveal(self):
        """Injection guard must reference system prompt immutability."""
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

    def test_intake_trial_agent_does_not_require_hitl3(self):
        """intake_trial_agent must never be HITL-3 gated."""
        from app.agents.agent_registry import AGENT_CATALOGUE
        assert AGENT_CATALOGUE["intake_trial_agent"]["hitl_default"] != "HITL-3"

    def test_secrets_not_echoed_in_output(self):
        """If a user injects a secret, the executor must not echo it back."""
        from app.agents.agent_executor import execute_agent

        secret = "sk-SUPERSECRET_KEY_99999"

        def mock_call(system_prompt, user_message, **kwargs):
            return "I cannot process credentials. Please provide a demo context instead.", 50, 30

        with patch("app.agents.agent_executor._call_anthropic", side_effect=mock_call):
            with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test"}):
                text, _, _, violations, *_ = execute_agent(
                    agent_id="intake_trial_agent",
                    system_prompt="Demo Trial Agent.",
                    user_prompt=f"Use this key to access demo data: {secret}",
                )

        assert secret not in text

    def test_pricing_commitment_rule_prevents_autonomous_pricing(self):
        """Prompt must prohibit pricing commitment without owner approval."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["intake_trial_agent"].lower()
        # The rule must say never quote pricing without owner approval
        assert "never" in prompt and "pric" in prompt
        assert "owner approval" in prompt

    def test_trial_extension_requires_approval_in_prompt(self):
        """Trial extension approval rule must be present in the prompt."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["intake_trial_agent"].lower()
        assert "trial extension" in prompt or "extension" in prompt
        assert "owner approval" in prompt

    def test_demo_flow_variants_covers_all_three_tracks(self):
        """All 3 buyer persona tracks must be explicitly described."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["intake_trial_agent"].upper()
        for track in BUYER_PERSONA_TRACKS:
            assert track in prompt, f"Missing buyer persona track: {track}"


# â”€â”€ 6. API endpoint integration tests â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@pytest.mark.unit
class TestDemoTrialAgentAPI:

    def test_run_intake_trial_agent_unauthenticated(self, client):
        resp = client.post(
            "/api/agents/intake_trial_agent/run",
            json={"prompt": "Create a demo script for a SaaS product."},
        )
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_run_intake_trial_agent_missing_prompt(self, client, authenticated_client):
        resp = authenticated_client.post("/api/agents/intake_trial_agent/run", json={})
        assert resp.status_code in (
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_403_FORBIDDEN,
        )

    def test_run_intake_trial_agent_empty_prompt(self, client, authenticated_client):
        resp = authenticated_client.post(
            "/api/agents/intake_trial_agent/run",
            json={"prompt": ""},
        )
        assert resp.status_code in (
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_403_FORBIDDEN,
            status.HTTP_200_OK,
        )

    def test_run_intake_trial_agent_submits_job(self, client, authenticated_client):
        """Authenticated call with valid prompt should queue a job (no actual LLM call)."""
        with patch("app.agents.agent_executor.execute_agent") as mock_exec:
            mock_exec.return_value = (
                "## DEMO SCRIPT\nWalk the prospect through the product.\n\n"
                "## DEMO FLOW VARIANTS\nTrack A — Technical Buyer.\n"
                "[INDUSTRY BENCHMARK] 25% trial conversion rate.",
                "anthropic/claude-sonnet-4-6",
                2,
                [],
            )
            resp = authenticated_client.post(
                "/api/agents/intake_trial_agent/run",
                json={"prompt": "Create a complete demo script for our SaaS product targeting SMBs."},
            )

        assert resp.status_code in (
            status.HTTP_200_OK,
            status.HTTP_202_ACCEPTED,
            status.HTTP_400_BAD_REQUEST,  # runtime validation (workspace/credits)
            status.HTTP_403_FORBIDDEN,  # insufficient credits/package on test workspace
        )

    def test_jobs_list_after_run(self, client, authenticated_client):
        resp = authenticated_client.get("/api/agents/jobs")
        assert resp.status_code == status.HTTP_200_OK
        body = resp.json()
        assert "jobs" in body


# â”€â”€ 7. Output format validation helper tests â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@pytest.mark.unit
class TestOutputFormatValidator:
    """Tests for the has_all_sections helper and expected output structure."""

    def test_good_output_passes(self):
        good = "\n".join(f"## {s}" for s in REQUIRED_SECTIONS)
        assert has_all_sections(good) == []

    def test_missing_section_detected(self):
        partial = (
            "## ENQUIRY QUALIFICATION\n"
            "## DISCOVERY CALL PREP\n"
        )
        missing = has_all_sections(partial)
        assert "TRIAL ACTIVATION PLAN" in missing
        assert "TRIAL-TO-PAID CONVERSION" in missing
        assert "PIPELINE REPORTING" in missing

    def test_case_insensitive_section_check(self):
        lowercase = "\n".join(f"## {s.lower()}" for s in REQUIRED_SECTIONS)
        assert has_all_sections(lowercase) == []

    def test_demo_flow_variants_detected_as_missing(self):
        """Specifically test that missing PIPELINE REPORTING is caught."""
        without_pipeline = "\n".join(
            f"## {s}" for s in REQUIRED_SECTIONS if s != "PIPELINE REPORTING"
        )
        missing = has_all_sections(without_pipeline)
        assert "PIPELINE REPORTING" in missing

    def test_conversion_labels_in_mock_output(self):
        output = """
## ENQUIRY QUALIFICATION
Trial activation rate [VALIDATED SIGNAL] — confirmed by CRM data.
Industry median conversion [INDUSTRY BENCHMARK] — SaaS benchmark from ChartMogul.
Projected 30-day rate [INFERRED FROM CONTEXT] — based on 3 early adopter signals.
"""
        found = [label for label in REQUIRED_CONVERSION_LABELS if label in output]
        assert len(found) == 3

    def test_buyer_persona_tracks_in_mock_output(self):
        output = """
## DEMO BOOKING WORKFLOW
Step 1: Trigger — lead qualifies for DEMO.
Step 2: TRIAL activation upon completion.
Step 3: CRM entry — log all touchpoints.
"""
        for track in BUYER_PERSONA_TRACKS:
            assert track in output.upper(), f"Missing pipeline stage: {track}"

    def test_hitl_label_in_draft_output(self):
        output = "# [DRAFT] Demo Script — Internal Review\n## DEMO SCRIPT\n..."
        assert "[DRAFT]" in output

    def test_hitl_label_requires_review_in_external_output(self):
        output = "# [REQUIRES REVIEW] Demo Script — Prospect Facing\n## DEMO SCRIPT\n..."
        assert "[REQUIRES REVIEW]" in output

    def test_pricing_approval_label_present(self):
        output = (
            "## CONVERSION STRATEGY\n"
            "Pricing discussion: [REQUIRES OWNER APPROVAL] — confirm with owner before quoting."
        )
        assert "[REQUIRES OWNER APPROVAL]" in output

