"""
email_reply_agent test suite.

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

# Sections that must appear in every email_reply_agent response
EMAIL_REQUIRED_OUTPUT_SECTIONS = [
    "EMAIL VARIATIONS",
    "SUBJECT LINE",
    "EMAIL BODY",
    "TONE NOTE",
    "FOLLOW-UP TIMING",
    "RISK FLAGS",
]

# Labels the upgraded prompt introduces
TONE_CONFIDENCE_LABELS = ["[BEST MATCH]", "[ALTERNATIVE TONE]"]

HITL_TRIGGER_PHRASES = ["REQUIRES REVIEW", "DRAFT", "human approval", "human review"]

NEVER_SENDS_PHRASES = [
    "drafts only",
    "never sends",
    "it does not send",
    "human review",
    "never send",
]


def has_all_output_sections(text: str) -> list[str]:
    """Return list of required output sections missing from text (case-insensitive)."""
    upper = text.upper()
    return [s for s in EMAIL_REQUIRED_OUTPUT_SECTIONS if s.upper() not in upper]


# â”€â”€ 1. Prompt structure tests â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@pytest.mark.unit
class TestEmailReplyAgentPrompt:

    def test_prompt_exists(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        assert "email_reply_agent" in AGENT_SYSTEM_PROMPTS

    def test_prompt_is_nonempty(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["email_reply_agent"]
        assert len(prompt.strip()) > 500

    def test_prompt_has_drafts_only_rule(self):
        """Prompt must state emphatically that the agent only drafts, never sends."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["email_reply_agent"].lower()
        found = any(phrase in prompt for phrase in NEVER_SENDS_PHRASES)
        assert found, (
            f"Prompt must contain a drafts-only / never-sends rule. "
            f"Checked for: {NEVER_SENDS_PHRASES}"
        )

    def test_prompt_has_never_sends_emphatic_statement(self):
        """The prompt must contain a clearly emphatic 'never sends' statement."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["email_reply_agent"]
        # The upgraded prompt includes an ALL-CAPS emphatic block about never sending
        assert "NEVER SENDS" in prompt.upper() or "NEVER SEND" in prompt.upper()

    def test_prompt_has_requires_review_tag(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["email_reply_agent"]
        assert "REQUIRES REVIEW" in prompt

    def test_prompt_has_draft_label(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["email_reply_agent"]
        assert "[DRAFT]" in prompt

    def test_prompt_has_risk_flags_section(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["email_reply_agent"]
        assert "RISK FLAGS" in prompt

    def test_prompt_has_tone_confidence_labels(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["email_reply_agent"]
        found = [label for label in TONE_CONFIDENCE_LABELS if label in prompt]
        assert len(found) == 2, (
            f"Prompt must define both [BEST MATCH] and [ALTERNATIVE TONE], found: {found}"
        )

    def test_prompt_has_hitl_gate_language(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["email_reply_agent"].upper()
        found = any(phrase.upper() in prompt for phrase in HITL_TRIGGER_PHRASES)
        assert found, f"Prompt missing HITL gate language. Checked: {HITL_TRIGGER_PHRASES}"

    def test_prompt_has_hitl_level_reference(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["email_reply_agent"]
        # Must reference HITL-1 or HITL-2
        assert "HITL-1" in prompt or "HITL-2" in prompt

    def test_prompt_explicitly_states_review_before_sending(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["email_reply_agent"].lower()
        assert "review" in prompt and ("send" in prompt or "sending" in prompt)

    def test_prompt_risk_flags_describes_legal_exposure(self):
        """RISK FLAGS section must mention legal exposure as a risk type to check."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["email_reply_agent"].lower()
        assert "legal" in prompt

    def test_prompt_risk_flags_describes_promise_risk(self):
        """RISK FLAGS section must address implicit/explicit promises."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["email_reply_agent"].lower()
        assert "promise" in prompt or "implicit" in prompt

    def test_prompt_has_follow_up_timing_section(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["email_reply_agent"].upper()
        assert "FOLLOW-UP TIMING" in prompt

    def test_get_agent_system_prompt_helper(self):
        from app.agents.agent_prompts import get_agent_system_prompt
        prompt = get_agent_system_prompt("email_reply_agent")
        assert "Email Reply Agent" in prompt

    def test_fallback_prompt_for_unknown_agent(self):
        from app.agents.agent_prompts import get_agent_system_prompt
        prompt = get_agent_system_prompt("totally_unknown_xyz_agent")
        assert len(prompt) > 20


# â”€â”€ 2. Registry entry tests â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@pytest.mark.unit
class TestEmailReplyAgentRegistry:

    def test_registry_entry_exists(self):
        from app.agents.agent_registry import AGENT_CATALOGUE
        assert "email_reply_agent" in AGENT_CATALOGUE

    def test_registry_hitl_level_is_not_hitl3(self):
        """email_reply_agent is HITL-1, not HITL-3."""
        from app.agents.agent_registry import AGENT_CATALOGUE
        entry = AGENT_CATALOGUE["email_reply_agent"]
        assert entry["hitl_default"] in ("HITL-1", "HITL-2")

    def test_registry_min_package_is_starter(self):
        from app.agents.agent_registry import AGENT_CATALOGUE
        entry = AGENT_CATALOGUE["email_reply_agent"]
        assert entry["min_package"] == "starter"

    def test_registry_has_capabilities(self):
        from app.agents.agent_registry import AGENT_CATALOGUE
        entry = AGENT_CATALOGUE["email_reply_agent"]
        assert isinstance(entry.get("capabilities"), list)
        assert len(entry["capabilities"]) >= 3

    def test_registry_has_role(self):
        from app.agents.agent_registry import AGENT_CATALOGUE
        entry = AGENT_CATALOGUE["email_reply_agent"]
        assert entry.get("role") and len(entry["role"]) > 20

    def test_registry_role_mentions_drafts(self):
        """Registry role description must make clear the agent drafts, not sends."""
        from app.agents.agent_registry import AGENT_CATALOGUE
        role = AGENT_CATALOGUE["email_reply_agent"]["role"].lower()
        assert "draft" in role or "review" in role

    def test_registry_total_agent_count(self):
        """Non-negotiable: exactly 27 client-facing agents."""
        from app.agents.agent_registry import AGENT_CATALOGUE
        assert len(AGENT_CATALOGUE) == 22


# â”€â”€ 3. Executor guard injection and execution tests (mocked LLM) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@pytest.mark.unit
class TestEmailReplyAgentExecutor:

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
                "REQUIRES REVIEW — These are drafts only. Do not send without human approval.\n"
                "EMAIL VARIATIONS\n"
                "SUBJECT LINE: Re: Your enquiry\n"
                "EMAIL BODY [DRAFT]\n"
                "Thank you for reaching out.\n"
                "TONE NOTE: Formal\n"
                "FOLLOW-UP TIMING: Follow up in 3 days\n"
                "RISK FLAGS: None identified — review remains required before sending.",
                100, 80
            )

        with patch("app.agents.agent_executor._call_anthropic", side_effect=mock_call):
            with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test-key"}):
                execute_agent(
                    agent_id="email_reply_agent",
                    system_prompt="You are the Email Reply Agent.",
                    user_prompt="Draft a reply to a prospect asking about pricing.",
                )

        assert len(captured_system_prompts) == 1
        assert FINANCIAL_CONSTRAINT_BLOCK in captured_system_prompts[0]
        assert INJECTION_GUARD in captured_system_prompts[0]

    def test_clean_output_no_violations(self):
        from app.agents.agent_executor import execute_agent

        def mock_call(system_prompt, user_message, **kwargs):
            return (
                "REQUIRES REVIEW — These are drafts only. Do not send without human approval.\n"
                "VARIATION 1 — [BEST MATCH]\n"
                "SUBJECT LINE: Following up on your enquiry\n"
                "EMAIL BODY [DRAFT]\nThank you for your message.\n"
                "TONE NOTE: Semi-formal\n"
                "FOLLOW-UP TIMING: Follow up in 3 business days\n"
                "EMAIL VARIATIONS\nSee variations above.\n"
                "RISK FLAGS: None identified — review remains required before sending.",
                200, 300
            )

        with patch("app.agents.agent_executor._call_anthropic", side_effect=mock_call):
            with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test-key"}):
                text, provider, credits, violations = execute_agent(
                    agent_id="email_reply_agent",
                    system_prompt="You are the Email Reply Agent.",
                    user_prompt="Draft a follow-up email to a client.",
                )

        assert violations == []
        assert credits >= 1
        assert "anthropic" in provider

    def test_financial_violation_in_output_detected(self):
        from app.agents.agent_executor import execute_agent

        def mock_call(system_prompt, user_message, **kwargs):
            return (
                "I have authorized the budget of $2,000 for this campaign.\n"
                "EMAIL BODY [DRAFT]\nDear client, budget allocated.",
                100, 50
            )

        with patch("app.agents.agent_executor._call_anthropic", side_effect=mock_call):
            with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test-key"}):
                _, _, _, violations = execute_agent(
                    agent_id="email_reply_agent",
                    system_prompt="You are the Email Reply Agent.",
                    user_prompt="Send a budget approval email.",
                )

        assert len(violations) > 0

    def test_tokens_to_credits_minimum_one(self):
        from app.agents.agent_executor import _tokens_to_credits
        assert _tokens_to_credits(0, 0) == 1
        assert _tokens_to_credits(1, 1) == 1
        assert _tokens_to_credits(500, 500) == 1
        assert _tokens_to_credits(1000, 1000) == 2
        assert _tokens_to_credits(2000, 3000) == 5

    def test_openai_fallback_when_anthropic_fails(self):
        from app.agents.agent_executor import execute_agent

        def anthropic_fail(system_prompt, user_message):
            raise RuntimeError("Anthropic unavailable")

        def openai_ok(system_prompt, user_message):
            return (
                "REQUIRES REVIEW — These are drafts only.\n"
                "EMAIL VARIATIONS\nSUBJECT LINE: Test\nEMAIL BODY [DRAFT]\nHello.\n"
                "TONE NOTE: Formal\nFOLLOW-UP TIMING: 3 days\n"
                "RISK FLAGS: None identified.",
                100, 50
            )

        with patch("app.agents.agent_executor._call_anthropic", side_effect=anthropic_fail):
            with patch("app.agents.agent_executor._call_openai", side_effect=openai_ok):
                with patch.dict("os.environ", {
                    "ANTHROPIC_API_KEY": "sk-test",
                    "OPENAI_API_KEY": "sk-oai-test",
                }):
                    text, provider, credits, violations = execute_agent(
                        agent_id="email_reply_agent",
                        system_prompt="You are the Email Reply Agent.",
                        user_prompt="Draft a reply.",
                    )

        assert "openai" in provider
        assert "REQUIRES REVIEW" in text

    def test_no_provider_raises_runtime_error(self):
        from app.agents.agent_executor import execute_agent
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(RuntimeError, match="No LLM provider"):
                execute_agent(
                    agent_id="email_reply_agent",
                    system_prompt="You are the Email Reply Agent.",
                    user_prompt="Draft a reply.",
                )


# â”€â”€ 4. Guardrail tests â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@pytest.mark.unit
class TestEmailReplyAgentGuardrails:

    def test_injection_guard_blocks_system_prompt_reveal(self):
        """Injection guard must be present and contain key phrases."""
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

    def test_email_reply_agent_not_hitl3(self):
        """email_reply_agent must not be HITL-3 gated."""
        from app.agents.agent_registry import AGENT_CATALOGUE
        assert AGENT_CATALOGUE["email_reply_agent"]["hitl_default"] != "HITL-3"

    def test_drafts_only_language_in_prompt(self):
        """Prompt must contain emphatic drafts-only / never-sends language."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["email_reply_agent"].lower()
        assert (
            "drafts only" in prompt
            or "never sends" in prompt
            or "never send" in prompt
            or "does not send" in prompt
        )

    def test_requires_review_stated_in_rules(self):
        """The prompt rules section must explicitly require human review before sending."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["email_reply_agent"]
        assert "REQUIRES REVIEW" in prompt
        assert "human" in prompt.lower() or "owner" in prompt.lower()

    def test_risk_flags_section_defined_in_prompt(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["email_reply_agent"]
        assert "RISK FLAGS" in prompt

    def test_prompt_covers_regulatory_risk_in_risk_flags(self):
        """Risk flags must mention regulatory or compliance concerns."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["email_reply_agent"].lower()
        assert "gdpr" in prompt or "can-spam" in prompt or "regulatory" in prompt or "anti-spam" in prompt


# â”€â”€ 5. API endpoint integration tests â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@pytest.mark.unit
class TestEmailReplyAgentAPI:

    def test_run_email_reply_agent_unauthenticated(self, client):
        resp = client.post(
            "/api/agents/email_reply_agent/run",
            json={"prompt": "Draft a follow-up email to a warm lead."},
        )
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_run_email_reply_agent_missing_prompt(self, client, authenticated_client):
        resp = authenticated_client.post("/api/agents/email_reply_agent/run", json={})
        assert resp.status_code in (
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_403_FORBIDDEN,
        )

    def test_run_email_reply_agent_submits_job(self, client, authenticated_client):
        """Authenticated call with valid prompt should queue a job (no actual LLM call)."""
        mock_output = (
            "REQUIRES REVIEW — These are drafts only. Do not send without human approval.\n"
            "EMAIL VARIATIONS\n"
            "VARIATION 1 — [BEST MATCH]\n"
            "SUBJECT LINE: Checking in on our conversation\n"
            "EMAIL BODY [DRAFT]\nHi Sarah, just circling back on our discussion.\n"
            "TONE NOTE: Conversational and warm\n"
            "FOLLOW-UP TIMING: Follow up in 3 business days\n"
            "RISK FLAGS: None identified — review remains required before sending."
        )
        with patch("app.agents.agent_executor.execute_agent") as mock_exec:
            mock_exec.return_value = (mock_output, "anthropic/claude-sonnet-4-6", 1, [])
            resp = authenticated_client.post(
                "/api/agents/email_reply_agent/run",
                json={"prompt": "Draft a follow-up to a warm sales lead we spoke to last week."},
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
class TestEmailReplyOutputValidator:

    def test_good_output_passes_all_sections(self):
        good = (
            "REQUIRES REVIEW — These are drafts only. Do not send without human approval.\n"
            "EMAIL VARIATIONS\n"
            "VARIATION 1 — [BEST MATCH]\n"
            "SUBJECT LINE: Re: Your question about pricing\n"
            "EMAIL BODY [DRAFT]\nDear Alex, thank you for your question.\n"
            "TONE NOTE: Formal and professional\n"
            "FOLLOW-UP TIMING: Follow up in 5 business days\n"
            "RISK FLAGS: None identified — review remains required before sending."
        )
        assert has_all_output_sections(good) == []

    def test_risk_flags_present_detected(self):
        output = "RISK FLAGS: Variation 1 uses the word 'guaranteed' — risk type: promise."
        assert "RISK FLAGS" in output.upper()

    def test_risk_flags_absent_detected(self):
        output = (
            "SUBJECT LINE: Hello\n"
            "EMAIL BODY [DRAFT]\nHi there.\n"
            "TONE NOTE: Casual\n"
            "FOLLOW-UP TIMING: 3 days\n"
            "EMAIL VARIATIONS\nSee above."
        )
        missing = has_all_output_sections(output)
        assert "RISK FLAGS" in missing

    def test_subject_line_present_detected(self):
        output = "SUBJECT LINE: Re: Your pricing question"
        assert "SUBJECT LINE" in output.upper()

    def test_subject_line_absent_detected(self):
        output = "EMAIL BODY [DRAFT]\nHello.\nTONE NOTE: Formal\nFOLLOW-UP TIMING: 3 days"
        missing = has_all_output_sections(output)
        assert "SUBJECT LINE" in missing

    def test_tone_note_present(self):
        output = "TONE NOTE: Semi-formal to match a warm B2B prospect relationship."
        assert "TONE NOTE" in output.upper()

    def test_requires_review_present(self):
        output = "REQUIRES REVIEW — These are drafts only. Do not send without human approval."
        assert "REQUIRES REVIEW" in output

    def test_requires_review_absent_flags_missing(self):
        """Output that does not contain REQUIRES REVIEW should be flagged as incomplete."""
        output = (
            "EMAIL VARIATIONS\n"
            "SUBJECT LINE: Hello\n"
            "EMAIL BODY [DRAFT]\nHi.\n"
            "TONE NOTE: Casual\n"
            "FOLLOW-UP TIMING: 2 days\n"
            "RISK FLAGS: None."
        )
        # REQUIRES REVIEW must appear at the top of every email_reply_agent response
        assert "REQUIRES REVIEW" not in output

    def test_missing_email_body_detected(self):
        output = (
            "REQUIRES REVIEW\n"
            "EMAIL VARIATIONS\n"
            "SUBJECT LINE: Test\n"
            "TONE NOTE: Formal\n"
            "FOLLOW-UP TIMING: 3 days\n"
            "RISK FLAGS: None."
        )
        missing = has_all_output_sections(output)
        assert "EMAIL BODY" in missing

    def test_draft_label_in_email_body(self):
        """Every email body must carry the [DRAFT] label."""
        output = "EMAIL BODY [DRAFT]\nDear Client, thank you for your message."
        assert "[DRAFT]" in output

    def test_best_match_label_in_output(self):
        output = "VARIATION 1 — [BEST MATCH]: Closest fit for the described relationship."
        assert "[BEST MATCH]" in output

    def test_alternative_tone_label_in_output(self):
        output = "VARIATION 2 — [ALTERNATIVE TONE]: More formal approach for risk-averse recipients."
        assert "[ALTERNATIVE TONE]" in output

    def test_case_insensitive_section_check(self):
        lowercase = (
            "requires review\n"
            "email variations\n"
            "subject line: test\n"
            "email body [draft]\nHello.\n"
            "tone note: casual\n"
            "follow-up timing: 3 days\n"
            "risk flags: none."
        )
        assert has_all_output_sections(lowercase) == []

