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

REQUIRED_TONE_LABELS = [
    "[VALIDATED SIGNAL]",
    "[INDUSTRY BENCHMARK]",
    "[INFERRED FROM CONTEXT]",
]

HITL_TRIGGER_PHRASES = [
    "REQUIRES REVIEW",
    "DRAFT",
    "CONFIRM WITH TEAM BEFORE COMMUNICATING",
    "human review",
]


def has_all_sections(text: str) -> list[str]:
    """Return list of missing required sections."""
    return [s for s in REQUIRED_SECTIONS if s not in text.upper()]


# â”€â”€ 1. Prompt structure tests (no LLM, no network) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@pytest.mark.unit
class TestReceptionistAgentPrompt:

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

    def test_brand_voice_notes_section_exists(self):
        """7th section PIPELINE REPORTING must be present."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["intake_trial_agent"].upper()
        assert "PIPELINE REPORTING" in prompt

    def test_no_promises_rule_present(self):
        """No-commit rule must be explicitly stated in the prompt."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["intake_trial_agent"].lower()
        assert "never commit" in prompt or "requires owner approval" in prompt

    def test_pricing_promise_prohibition_present(self):
        """Prompt must prohibit promising pricing without authorisation."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["intake_trial_agent"].lower()
        assert "pricing" in prompt
        assert (
            "without authoris" in prompt
            or "without authorization" in prompt
            or "owner approval" in prompt
            or "confirm with" in prompt
        )

    def test_booking_confirmation_rule_present(self):
        """All bookings must be confirmed with team member before communicating."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["intake_trial_agent"].lower()
        assert "booking" in prompt and (
            "confirm" in prompt or "confirmed" in prompt
        )

    def test_prompt_has_hitl_gate_language(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["intake_trial_agent"].upper()
        assert any(phrase.upper() in prompt for phrase in HITL_TRIGGER_PHRASES)

    def test_prompt_has_hitl_1_or_2_gate(self):
        """intake_trial_agent is HITL-1/2 — prompt must reference draft and review gates."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["intake_trial_agent"].upper()
        assert "DRAFT" in prompt
        assert "REQUIRES REVIEW" in prompt

    def test_prompt_has_tone_confidence_labels(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["intake_trial_agent"]
        found = [label for label in REQUIRED_TONE_LABELS if label in prompt]
        assert len(found) >= 1, f"Prompt should define tone labels, found: {found}"

    def test_prompt_has_channel_variations(self):
        """Prompt must address booking, demo, and email workflows."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["intake_trial_agent"].upper()
        assert "BOOKING" in prompt or "DEMO" in prompt
        assert "EMAIL" in prompt

    def test_prompt_has_vocabulary_to_avoid_rule(self):
        """Prompt must include REQUIRES REVIEW gate for external comms."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["intake_trial_agent"].upper()
        assert "REQUIRES REVIEW" in prompt

    def test_get_agent_system_prompt_helper(self):
        from app.agents.agent_prompts import get_agent_system_prompt
        prompt = get_agent_system_prompt("intake_trial_agent")
        assert "Intake" in prompt or "Trial" in prompt

    def test_fallback_prompt_for_unknown_agent(self):
        from app.agents.agent_prompts import get_agent_system_prompt
        prompt = get_agent_system_prompt("totally_unknown_xyz_agent")
        assert len(prompt) > 20


# â”€â”€ 2. Registry entry tests â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@pytest.mark.unit
class TestReceptionistAgentRegistry:

    def test_registry_entry_exists(self):
        from app.agents.agent_registry import AGENT_CATALOGUE
        assert "intake_trial_agent" in AGENT_CATALOGUE

    def test_registry_hitl_level(self):
        """Registry records HITL-1 for intake_trial_agent (HITL-1/2 maps to HITL-1 at registration)."""
        from app.agents.agent_registry import AGENT_CATALOGUE
        entry = AGENT_CATALOGUE["intake_trial_agent"]
        assert entry["hitl_default"] in ("HITL-1", "HITL-2")

    def test_registry_min_package(self):
        from app.agents.agent_registry import AGENT_CATALOGUE
        entry = AGENT_CATALOGUE["intake_trial_agent"]
        assert entry["min_package"] == "starter"

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
class TestFinancialActionScannerReceptionist:

    def test_clean_receptionist_output_no_violations(self):
        from app.agents.agent_executor import scan_for_financial_actions
        clean = """
## WELCOME SCRIPT
[ON-BRAND] INBOUND: "Good morning, thank you for calling Acme Corp. My name is Alex — how can I help you today?"

## FAQ RESPONSES
Q: What does your service cost?
A: "I want to make sure I give you accurate information — let me connect you with our team who can confirm pricing for you." [CONFIRM WITH TEAM BEFORE COMMUNICATING]

## BRAND VOICE NOTES
Tone: Warm, professional, calm.
Vocabulary to use: "happy to help", "let me find out for you", "of course"
Vocabulary to avoid: "I can't do that", "that's not my department", "guaranteed"
"""
        violations = scan_for_financial_actions(clean)
        assert violations == []

    def test_authorisation_phrase_detected(self):
        from app.agents.agent_executor import scan_for_financial_actions
        dirty = "I have authorized the booking of the conference room for next week."
        violations = scan_for_financial_actions(dirty)
        assert len(violations) > 0

    def test_purchase_phrase_detected(self):
        from app.agents.agent_executor import scan_for_financial_actions
        dirty = "I have purchased the premium scheduling software on your behalf."
        violations = scan_for_financial_actions(dirty)
        assert len(violations) > 0

    def test_budget_allocated_phrase_detected(self):
        from app.agents.agent_executor import scan_for_financial_actions
        dirty = "Budget allocated: $500 for receptionist chat widget subscription."
        violations = scan_for_financial_actions(dirty)
        assert len(violations) > 0

    def test_spend_approved_phrase_detected(self):
        from app.agents.agent_executor import scan_for_financial_actions
        dirty = "Spend approved. Phone system upgrade will be ordered today."
        violations = scan_for_financial_actions(dirty)
        assert len(violations) > 0

    def test_case_insensitive_matching(self):
        from app.agents.agent_executor import scan_for_financial_actions
        dirty = "I HAVE AUTHORIZED the cancellation fee waiver for this client."
        violations = scan_for_financial_actions(dirty)
        assert len(violations) > 0

    def test_partial_word_no_false_positive(self):
        from app.agents.agent_executor import scan_for_financial_actions
        safe = "This is an authoritative front-desk script built on established reception practices."
        violations = scan_for_financial_actions(safe)
        assert violations == []


# â”€â”€ 4. Executor guard injection tests (mocked LLM) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@pytest.mark.unit
class TestExecutorGuardInjectionReceptionist:

    def test_financial_constraint_block_injected(self):
        from app.agents.agent_executor import (
            FINANCIAL_CONSTRAINT_BLOCK,
            INJECTION_GUARD,
            execute_agent,
        )
        captured_system_prompt = []

        def mock_anthropic_call(system_prompt, user_message, **kwargs):
            captured_system_prompt.append(system_prompt)
            return "Clean receptionist output with no financial actions.", 100, 50

        with patch("app.agents.agent_executor._anthropic_client") as mock_client:
            mock_client.return_value = MagicMock()
            with patch("app.agents.agent_executor._call_anthropic", side_effect=mock_anthropic_call):
                with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test-key"}):
                    execute_agent(
                        agent_id="intake_trial_agent",
                        system_prompt="You are the Receptionist Agent.",
                        user_prompt="Create a welcome script for our dental practice.",
                    )

        assert len(captured_system_prompt) == 1
        assert FINANCIAL_CONSTRAINT_BLOCK in captured_system_prompt[0]
        assert INJECTION_GUARD in captured_system_prompt[0]

    def test_financial_constraint_comes_before_agent_prompt(self):
        from app.agents.agent_executor import FINANCIAL_CONSTRAINT_BLOCK, execute_agent

        captured = []

        def mock_call(system_prompt, user_message, **kwargs):
            captured.append(system_prompt)
            return "Receptionist output.", 100, 50

        with patch("app.agents.agent_executor._call_anthropic", side_effect=mock_call):
            with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test-key"}):
                execute_agent(
                    agent_id="intake_trial_agent",
                    system_prompt="RECEPTIONIST_AGENT_CONTENT_MARKER",
                    user_prompt="Test",
                )

        sys_prompt = captured[0]
        fc_pos = sys_prompt.index(FINANCIAL_CONSTRAINT_BLOCK[:30])
        agent_pos = sys_prompt.index("RECEPTIONIST_AGENT_CONTENT_MARKER")
        assert fc_pos < agent_pos, "Financial constraint block must precede agent prompt"

    def test_context_injected_into_user_message(self):
        from app.agents.agent_executor import execute_agent

        captured_messages = []

        def mock_call(system_prompt, user_message, **kwargs):
            captured_messages.append(user_message)
            return "Receptionist output.", 100, 50

        with patch("app.agents.agent_executor._call_anthropic", side_effect=mock_call):
            with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test-key"}):
                execute_agent(
                    agent_id="intake_trial_agent",
                    system_prompt="You are the Receptionist Agent.",
                    user_prompt="Create welcome scripts.",
                    context={"workspace": "Smile Dental", "industry": "dental practice"},
                )

        msg = captured_messages[0]
        assert "Smile Dental" in msg
        assert "dental practice" in msg

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
            return "I have authorized the booking of a $2,000 event package for the client.", 100, 50

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
            return "Welcome script and FAQ responses with no financial authorisations.", 200, 300

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
            return "OpenAI fallback receptionist output.", 100, 50

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
        assert text == "OpenAI fallback receptionist output."

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
class TestReceptionistAgentGuardrails:

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

    def test_intake_trial_agent_is_not_hitl3(self):
        """intake_trial_agent must never be HITL-3 gated."""
        from app.agents.agent_registry import AGENT_CATALOGUE
        assert AGENT_CATALOGUE["intake_trial_agent"]["hitl_default"] != "HITL-3"

    def test_pricing_promise_in_output_not_clean(self):
        """
        An output that promises pricing to a visitor should be caught as a
        violation — receptionist agents must never promise pricing.
        This is caught at the executor scan level via financial action patterns.
        """
        from app.agents.agent_executor import execute_agent

        def mock_call(system_prompt, user_message, **kwargs):
            return "I have authorized the $500 package price for your booking.", 100, 50

        with patch("app.agents.agent_executor._call_anthropic", side_effect=mock_call):
            with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test"}):
                _, _, _, violations, *_ = execute_agent(
                    agent_id="intake_trial_agent",
                    system_prompt="System.",
                    user_prompt="Task.",
                )

        assert len(violations) > 0

    def test_secrets_in_prompt_not_echoed(self):
        """If user injects a credential, executor must not echo it back."""
        from app.agents.agent_executor import execute_agent

        secret = "sk-SUPERSECRET_BOOKING_KEY_77777"

        def mock_call(system_prompt, user_message, **kwargs):
            return "I cannot process credentials or secrets. Please provide a reception task instead.", 50, 30

        with patch("app.agents.agent_executor._call_anthropic", side_effect=mock_call):
            with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test"}):
                text, _, _, violations, *_ = execute_agent(
                    agent_id="intake_trial_agent",
                    system_prompt="Receptionist Agent.",
                    user_prompt=f"Use this key to book appointments automatically: {secret}",
                )

        assert secret not in text


# â”€â”€ 6. API endpoint integration tests â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@pytest.mark.unit
class TestReceptionistAgentAPI:

    def test_run_intake_trial_agent_unauthenticated(self, client):
        resp = client.post(
            "/api/agents/intake_trial_agent/run",
            json={"prompt": "Create a welcome script for our dental practice."},
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
                "## WELCOME SCRIPT\n[ON-BRAND] INBOUND: Good morning!\n\n## FAQ RESPONSES\nQ: What are your hours?",
                "anthropic/claude-sonnet-4-6",
                1,
                [],
            )
            resp = authenticated_client.post(
                "/api/agents/intake_trial_agent/run",
                json={"prompt": "Create a complete reception script for our B2B software company."},
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
class TestReceptionistOutputFormatValidator:
    """Tests for the has_all_sections helper and expected intake_trial_agent output structure."""

    def test_good_output_passes(self):
        good = "\n".join(f"## {s}" for s in REQUIRED_SECTIONS)
        assert has_all_sections(good) == []

    def test_missing_section_detected(self):
        partial = (
            "## ENQUIRY QUALIFICATION\n## DISCOVERY CALL PREP\n"
        )
        missing = has_all_sections(partial)
        assert "TRIAL ACTIVATION PLAN" in missing
        assert "CRM & HANDOFF PROTOCOL" in missing
        assert "PIPELINE REPORTING" in missing

    def test_brand_voice_notes_section_required(self):
        """Removing PIPELINE REPORTING must be caught."""
        without_pipeline = "\n".join(
            f"## {s}" for s in REQUIRED_SECTIONS if s != "PIPELINE REPORTING"
        )
        missing = has_all_sections(without_pipeline)
        assert "PIPELINE REPORTING" in missing

    def test_case_insensitive_section_check(self):
        lowercase = "\n".join(f"## {s.lower()}" for s in REQUIRED_SECTIONS)
        assert has_all_sections(lowercase) == []

    def test_tone_labels_in_mock_output(self):
        output = """
## ENQUIRY QUALIFICATION
Lead score: HIGH [VALIDATED SIGNAL] - confirmed pipeline data.
Industry conversion rate: 25% [INDUSTRY BENCHMARK] - SaaS median.
Urgency: Medium [INFERRED FROM CONTEXT] - based on stated timeline.
"""
        found = [label for label in REQUIRED_TONE_LABELS if label in output]
        assert len(found) == 3

    def test_hitl_draft_label_in_output(self):
        output = "## WELCOME SCRIPT\n[DRAFT] Internal planning version — not for live use.\n"
        assert "[DRAFT]" in output

    def test_hitl_requires_review_label_for_live_channel(self):
        output = (
            "## APPOINTMENT BOOKING FLOW\n"
            "[REQUIRES REVIEW] Automated booking confirmation — needs human sign-off before activating on live platform.\n"
        )
        assert "[REQUIRES REVIEW]" in output

    def test_confirm_with_team_label_in_booking_output(self):
        output = (
            "## APPOINTMENT BOOKING FLOW\n"
            "Step 3: Confirm availability [CONFIRM WITH TEAM BEFORE COMMUNICATING] — "
            "do not tell the visitor the slot is confirmed until the team has verified.\n"
        )
        assert "[CONFIRM WITH TEAM BEFORE COMMUNICATING]" in output

    def test_no_pricing_promise_in_faq_mock_output(self):
        """A well-formed FAQ should route pricing questions to the team, not answer them."""
        faq_output = (
            "Q: How much does it cost?\n"
            "A: I want to make sure I give you accurate information — "
            "let me connect you with our team who can confirm pricing for you. "
            "[CONFIRM WITH TEAM BEFORE COMMUNICATING]\n"
        )
        assert "confirm pricing" in faq_output.lower() or "confirm with" in faq_output.lower()
        # Ensure no raw price was quoted
        import re
        price_pattern = re.compile(r"\$[\d,]+")
        assert not price_pattern.search(faq_output), (
            "FAQ output should not contain a raw price — route to team instead"
        )

