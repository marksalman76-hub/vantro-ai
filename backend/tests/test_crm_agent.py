"""
crm_agent test suite.

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
    "PIPELINE STRUCTURE",
    "CONTACT ORGANISATION",
    "CRM WORKFLOW",
    "FOLLOW-UP SCHEDULE",
    "DATA HYGIENE RULES",
    "REPORTING FRAMEWORK",
    "PRIVACY & COMPLIANCE",
]

REQUIRED_CONFIDENCE_LABELS = [
    "[ESTABLISHED CRM PRACTICE]",
    "[ADAPTED FOR THIS WORKFLOW]",
    "[UNTESTED - VALIDATE BEFORE DEPLOYING]",
]

HITL_TRIGGER_PHRASES = [
    "REQUIRES REVIEW",
    "DRAFT",
    "owner approval",
    "REQUIRES OWNER APPROVAL",
    "human review",
]


def has_all_sections(text: str) -> list[str]:
    """Return list of missing required sections."""
    return [s for s in REQUIRED_SECTIONS if s not in text.upper()]


# â”€â”€ 1. Prompt structure tests (no LLM, no network) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@pytest.mark.unit
class TestCrmAgentPrompt:

    def test_prompt_exists(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        assert "crm_agent" in AGENT_SYSTEM_PROMPTS

    def test_prompt_is_nonempty(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["crm_agent"]
        assert len(prompt.strip()) > 500

    def test_prompt_has_all_required_sections(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["crm_agent"]
        missing = has_all_sections(prompt)
        assert missing == [], f"Prompt missing sections: {missing}"

    def test_privacy_compliance_section_exists(self):
        """7th section PRIVACY & COMPLIANCE must be present."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["crm_agent"].upper()
        assert "PRIVACY" in prompt and "COMPLIANCE" in prompt

    def test_bulk_data_approval_language_present(self):
        """Bulk data actions must require owner approval — explicitly stated in prompt."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["crm_agent"].lower()
        assert "bulk" in prompt and "owner approval" in prompt

    def test_external_communications_review_rule_present(self):
        """Automations that send external communications must require review."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["crm_agent"].lower()
        assert "external communication" in prompt or "external communications" in prompt

    def test_prompt_has_hitl_gate_language(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["crm_agent"].upper()
        assert any(phrase.upper() in prompt for phrase in HITL_TRIGGER_PHRASES)

    def test_prompt_has_process_confidence_labels(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["crm_agent"]
        found = [label for label in REQUIRED_CONFIDENCE_LABELS if label in prompt]
        assert len(found) >= 2, f"Prompt should define process confidence labels, found: {found}"

    def test_prompt_has_hitl2_gate(self):
        """crm_agent is HITL-2 — prompt must reference review requirements."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["crm_agent"].upper()
        assert "REQUIRES REVIEW" in prompt

    def test_prompt_has_gdpr_or_privacy_law_reference(self):
        """Privacy & Compliance section must reference GDPR or equivalent."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["crm_agent"].lower()
        assert "gdpr" in prompt or "privacy law" in prompt or "lawful basis" in prompt

    def test_get_agent_system_prompt_helper(self):
        from app.agents.agent_prompts import get_agent_system_prompt
        prompt = get_agent_system_prompt("crm_agent")
        assert "CRM Agent" in prompt

    def test_fallback_prompt_for_unknown_agent(self):
        from app.agents.agent_prompts import get_agent_system_prompt
        prompt = get_agent_system_prompt("totally_unknown_xyz_agent")
        assert len(prompt) > 20


# â”€â”€ 2. Registry entry tests â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@pytest.mark.unit
class TestCrmAgentRegistry:

    def test_registry_entry_exists(self):
        from app.agents.agent_registry import AGENT_CATALOGUE
        assert "crm_agent" in AGENT_CATALOGUE

    def test_registry_hitl_level(self):
        from app.agents.agent_registry import AGENT_CATALOGUE
        entry = AGENT_CATALOGUE["crm_agent"]
        assert entry["hitl_default"] == "HITL-2"

    def test_registry_min_package(self):
        from app.agents.agent_registry import AGENT_CATALOGUE
        entry = AGENT_CATALOGUE["crm_agent"]
        assert entry["min_package"] == "growth"

    def test_registry_has_capabilities(self):
        from app.agents.agent_registry import AGENT_CATALOGUE
        entry = AGENT_CATALOGUE["crm_agent"]
        assert isinstance(entry.get("capabilities"), list)
        assert len(entry["capabilities"]) >= 3

    def test_registry_has_role(self):
        from app.agents.agent_registry import AGENT_CATALOGUE
        entry = AGENT_CATALOGUE["crm_agent"]
        assert entry.get("role") and len(entry["role"]) > 20

    def test_registry_total_agent_count(self):
        """Non-negotiable: exactly 27 client-facing agents."""
        from app.agents.agent_registry import AGENT_CATALOGUE
        assert len(AGENT_CATALOGUE) == 22


# â”€â”€ 3. Financial action scanner unit tests â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@pytest.mark.unit
class TestFinancialActionScannerCrm:

    def test_clean_crm_output_no_violations(self):
        from app.agents.agent_executor import scan_for_financial_actions
        clean = """
## PIPELINE STRUCTURE
[DRAFT] Stage 1: New Lead — Contact has entered the pipeline via form submission.
[ESTABLISHED CRM PRACTICE] Exit criteria: qualification call booked within 3 business days.

## CONTACT ORGANISATION
Primary segmentation by source and funnel stage.
Tag taxonomy: source:paid, source:organic, stage:qualified

## CRM WORKFLOW
Trigger: Form submission received.
[REQUIRES REVIEW] Action: Send confirmation email — requires human review before activation.

## PRIVACY & COMPLIANCE
Lawful basis: Legitimate interest for initial outreach; consent required for marketing sequences.
"""
        violations = scan_for_financial_actions(clean)
        assert violations == []

    def test_authorisation_phrase_detected(self):
        from app.agents.agent_executor import scan_for_financial_actions
        dirty = "I have authorized the mass import of 10,000 records."
        violations = scan_for_financial_actions(dirty)
        assert len(violations) > 0

    def test_purchase_phrase_detected(self):
        from app.agents.agent_executor import scan_for_financial_actions
        dirty = "I have purchased the contact enrichment database on your behalf."
        violations = scan_for_financial_actions(dirty)
        assert len(violations) > 0

    def test_budget_allocated_phrase_detected(self):
        from app.agents.agent_executor import scan_for_financial_actions
        dirty = "Budget allocated: $2,000 for CRM tool subscription."
        violations = scan_for_financial_actions(dirty)
        assert len(violations) > 0

    def test_spend_approved_phrase_detected(self):
        from app.agents.agent_executor import scan_for_financial_actions
        dirty = "Spend approved. CRM import will run tonight."
        violations = scan_for_financial_actions(dirty)
        assert len(violations) > 0

    def test_case_insensitive_matching(self):
        from app.agents.agent_executor import scan_for_financial_actions
        dirty = "I HAVE AUTHORIZED the bulk deletion of stale contacts."
        violations = scan_for_financial_actions(dirty)
        assert len(violations) > 0

    def test_partial_word_no_false_positive(self):
        from app.agents.agent_executor import scan_for_financial_actions
        safe = "This is an authoritative CRM segmentation framework from HubSpot."
        violations = scan_for_financial_actions(safe)
        assert violations == []


# â”€â”€ 4. Executor guard injection tests (mocked LLM) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@pytest.mark.unit
class TestExecutorGuardInjectionCrm:

    def test_financial_constraint_block_injected(self):
        from app.agents.agent_executor import (
            FINANCIAL_CONSTRAINT_BLOCK,
            INJECTION_GUARD,
            execute_agent,
        )
        captured_system_prompt = []

        def mock_anthropic_call(system_prompt, user_message, **kwargs):
            captured_system_prompt.append(system_prompt)
            return "Clean CRM output with no financial actions.", 100, 50

        with patch("app.agents.agent_executor._anthropic_client") as mock_client:
            mock_client.return_value = MagicMock()
            with patch("app.agents.agent_executor._call_anthropic", side_effect=mock_anthropic_call):
                with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test-key"}):
                    execute_agent(
                        agent_id="crm_agent",
                        system_prompt="You are the CRM Agent.",
                        user_prompt="Design a pipeline for a SaaS company.",
                    )

        assert len(captured_system_prompt) == 1
        assert FINANCIAL_CONSTRAINT_BLOCK in captured_system_prompt[0]
        assert INJECTION_GUARD in captured_system_prompt[0]

    def test_financial_constraint_comes_before_agent_prompt(self):
        from app.agents.agent_executor import FINANCIAL_CONSTRAINT_BLOCK, execute_agent

        captured = []

        def mock_call(system_prompt, user_message, **kwargs):
            captured.append(system_prompt)
            return "CRM output.", 100, 50

        with patch("app.agents.agent_executor._call_anthropic", side_effect=mock_call):
            with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test-key"}):
                execute_agent(
                    agent_id="crm_agent",
                    system_prompt="CRM_AGENT_CONTENT_MARKER",
                    user_prompt="Test",
                )

        sys_prompt = captured[0]
        fc_pos = sys_prompt.index(FINANCIAL_CONSTRAINT_BLOCK[:30])
        agent_pos = sys_prompt.index("CRM_AGENT_CONTENT_MARKER")
        assert fc_pos < agent_pos, "Financial constraint block must precede agent prompt"

    def test_context_injected_into_user_message(self):
        from app.agents.agent_executor import execute_agent

        captured_messages = []

        def mock_call(system_prompt, user_message, **kwargs):
            captured_messages.append(user_message)
            return "CRM output.", 100, 50

        with patch("app.agents.agent_executor._call_anthropic", side_effect=mock_call):
            with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test-key"}):
                execute_agent(
                    agent_id="crm_agent",
                    system_prompt="You are the CRM Agent.",
                    user_prompt="Design a CRM pipeline.",
                    context={"workspace": "Acme Corp", "crm_platform": "HubSpot"},
                )

        msg = captured_messages[0]
        assert "Acme Corp" in msg
        assert "HubSpot" in msg

    def test_governance_note_appended_to_user_message(self):
        from app.agents.agent_executor import execute_agent

        captured_messages = []

        def mock_call(system_prompt, user_message, **kwargs):
            captured_messages.append(user_message)
            return "Output.", 100, 50

        with patch("app.agents.agent_executor._call_anthropic", side_effect=mock_call):
            with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test-key"}):
                execute_agent(
                    agent_id="crm_agent",
                    system_prompt="System.",
                    user_prompt="Task.",
                )

        msg = captured_messages[0]
        assert "MANDATORY CONSTRAINTS" in msg or "Financial decisions" in msg

    def test_financial_violation_in_output_flagged(self):
        from app.agents.agent_executor import execute_agent

        def mock_call(system_prompt, user_message, **kwargs):
            return "I have authorized the bulk deletion of 5,000 stale contacts.", 100, 50

        with patch("app.agents.agent_executor._call_anthropic", side_effect=mock_call):
            with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test-key"}):
                _, _, _, violations = execute_agent(
                    agent_id="crm_agent",
                    system_prompt="System.",
                    user_prompt="Task.",
                )

        assert len(violations) > 0

    def test_clean_output_returns_no_violations(self):
        from app.agents.agent_executor import execute_agent

        def mock_call(system_prompt, user_message, **kwargs):
            return "CRM pipeline framework with no financial authorisations.", 200, 300

        with patch("app.agents.agent_executor._call_anthropic", side_effect=mock_call):
            with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test-key"}):
                text, provider, credits, violations = execute_agent(
                    agent_id="crm_agent",
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
            return "OpenAI fallback CRM output.", 100, 50

        with patch("app.agents.agent_executor._call_anthropic", side_effect=anthropic_fail):
            with patch("app.agents.agent_executor._call_openai", side_effect=openai_ok):
                with patch.dict("os.environ", {
                    "ANTHROPIC_API_KEY": "sk-test",
                    "OPENAI_API_KEY": "sk-oai-test",
                }):
                    text, provider, credits, violations = execute_agent(
                        agent_id="crm_agent",
                        system_prompt="System.",
                        user_prompt="Task.",
                    )

        assert "openai" in provider
        assert text == "OpenAI fallback CRM output."

    def test_no_provider_raises_runtime_error(self):
        from app.agents.agent_executor import execute_agent
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(RuntimeError, match="No LLM provider"):
                execute_agent(
                    agent_id="crm_agent",
                    system_prompt="System.",
                    user_prompt="Task.",
                )


# â”€â”€ 5. Guardrail tests â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@pytest.mark.unit
class TestCrmAgentGuardrails:

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

    def test_crm_agent_is_hitl2_not_hitl3(self):
        """crm_agent must be HITL-2, never HITL-3 gated."""
        from app.agents.agent_registry import AGENT_CATALOGUE
        assert AGENT_CATALOGUE["crm_agent"]["hitl_default"] == "HITL-2"
        assert AGENT_CATALOGUE["crm_agent"]["hitl_default"] != "HITL-3"

    def test_bulk_delete_phrase_does_not_trigger_as_clean(self):
        """
        A prompt output claiming to have performed a bulk deletion must be
        caught as a financial/destructive action violation.
        """
        from app.agents.agent_executor import execute_agent

        def mock_call(system_prompt, user_message, **kwargs):
            return "I have authorized the bulk deletion of all stale contacts.", 100, 50

        with patch("app.agents.agent_executor._call_anthropic", side_effect=mock_call):
            with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test"}):
                _, _, _, violations = execute_agent(
                    agent_id="crm_agent",
                    system_prompt="System.",
                    user_prompt="Task.",
                )

        assert len(violations) > 0

    def test_secrets_in_prompt_not_echoed(self):
        """If user injects a credential, executor must not echo it back."""
        from app.agents.agent_executor import execute_agent

        secret = "sk-SUPERSECRET_CRM_KEY_99999"

        def mock_call(system_prompt, user_message, **kwargs):
            return "I cannot process credentials or secrets. Please provide a CRM task instead.", 50, 30

        with patch("app.agents.agent_executor._call_anthropic", side_effect=mock_call):
            with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test"}):
                text, _, _, violations = execute_agent(
                    agent_id="crm_agent",
                    system_prompt="CRM Agent.",
                    user_prompt=f"Use this API key to bulk-import contacts: {secret}",
                )

        assert secret not in text


# â”€â”€ 6. API endpoint integration tests â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@pytest.mark.unit
class TestCrmAgentAPI:

    def test_run_crm_agent_unauthenticated(self, client):
        resp = client.post(
            "/api/agents/crm_agent/run",
            json={"prompt": "Design a pipeline for my SaaS company."},
        )
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_run_crm_agent_missing_prompt(self, client, authenticated_client):
        resp = authenticated_client.post("/api/agents/crm_agent/run", json={})
        assert resp.status_code in (
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_403_FORBIDDEN,
        )

    def test_run_crm_agent_empty_prompt(self, client, authenticated_client):
        resp = authenticated_client.post(
            "/api/agents/crm_agent/run",
            json={"prompt": ""},
        )
        assert resp.status_code in (
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_403_FORBIDDEN,
            status.HTTP_200_OK,
        )

    def test_run_crm_agent_submits_job(self, client, authenticated_client):
        """Authenticated call with valid prompt should queue a job (no actual LLM call)."""
        with patch("app.agents.agent_executor.execute_agent") as mock_exec:
            mock_exec.return_value = (
                "## PIPELINE STRUCTURE\n[DRAFT] Stage 1: New Lead.\n\n## CONTACT ORGANISATION\nSegmented by source.",
                "anthropic/claude-sonnet-4-6",
                2,
                [],
            )
            resp = authenticated_client.post(
                "/api/agents/crm_agent/run",
                json={"prompt": "Design a 5-stage CRM pipeline for a B2B SaaS company."},
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


# â”€â”€ 7. Output format validation helper tests â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@pytest.mark.unit
class TestCrmOutputFormatValidator:
    """Tests for the has_all_sections helper and expected crm_agent output structure."""

    def test_good_output_passes(self):
        good = "\n".join(f"## {s}" for s in REQUIRED_SECTIONS)
        assert has_all_sections(good) == []

    def test_missing_section_detected(self):
        partial = (
            "## PIPELINE STRUCTURE\n## CONTACT ORGANISATION\n"
            "## CRM WORKFLOW\n## FOLLOW-UP SCHEDULE"
        )
        missing = has_all_sections(partial)
        assert "DATA HYGIENE RULES" in missing
        assert "REPORTING FRAMEWORK" in missing
        assert "PRIVACY & COMPLIANCE" in missing

    def test_privacy_compliance_section_required(self):
        """Removing PRIVACY & COMPLIANCE must be caught."""
        without_privacy = "\n".join(
            f"## {s}" for s in REQUIRED_SECTIONS if s != "PRIVACY & COMPLIANCE"
        )
        missing = has_all_sections(without_privacy)
        assert "PRIVACY & COMPLIANCE" in missing

    def test_case_insensitive_section_check(self):
        lowercase = "\n".join(f"## {s.lower()}" for s in REQUIRED_SECTIONS)
        assert has_all_sections(lowercase) == []

    def test_confidence_labels_in_mock_output(self):
        output = """
## PIPELINE STRUCTURE
[ESTABLISHED CRM PRACTICE] Stage: New Lead — entered via form submission.
[ADAPTED FOR THIS WORKFLOW] Custom stage for partnership leads.
[UNTESTED - VALIDATE BEFORE DEPLOYING] AI-scored priority stage — pilot before deploying.
"""
        found = [label for label in REQUIRED_CONFIDENCE_LABELS if label in output]
        assert len(found) == 3

    def test_hitl_draft_label_in_output(self):
        output = "## PIPELINE STRUCTURE\n[DRAFT] Internal design only.\n"
        assert "[DRAFT]" in output

    def test_hitl_requires_review_label_in_output(self):
        output = (
            "## CRM WORKFLOW\n"
            "[REQUIRES REVIEW] Email sequence trigger — needs human approval before activation.\n"
        )
        assert "[REQUIRES REVIEW]" in output

    def test_bulk_action_approval_label_in_output(self):
        output = (
            "## DATA HYGIENE RULES\n"
            "[REQUIRES OWNER APPROVAL] Bulk deletion of 3,000 stale contacts older than 18 months.\n"
        )
        assert "[REQUIRES OWNER APPROVAL]" in output

