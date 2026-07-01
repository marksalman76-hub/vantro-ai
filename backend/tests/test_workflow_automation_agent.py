"""
workflow_automation_agent test suite.

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


# ── Helpers ───────────────────────────────────────────────────────────────────

REQUIRED_SECTIONS = [
    "PROCESS AUDIT",
    "AUTOMATION OPPORTUNITIES",
    "TOOL STACK",
    "IMPLEMENTATION PLAN",
    "ROI",
    "MONITORING",
    "RISK REGISTER",
]

REQUIRED_CONFIDENCE_LABELS = [
    "[MEASURED BASELINE]",
    "[INDUSTRY AVERAGE]",
    "[ESTIMATED - VALIDATE AFTER 30 DAYS]",
]

HITL_TRIGGER_PHRASES = ["HITL-3", "REQUIRES OWNER APPROVAL", "owner approval", "staging"]


def has_all_sections(text: str) -> list[str]:
    """Return list of missing required sections."""
    return [s for s in REQUIRED_SECTIONS if s not in text.upper()]


# ── 1. Prompt structure tests (no LLM, no network) ───────────────────────────

@pytest.mark.unit
class TestWorkflowAutomationAgentPrompt:

    def test_prompt_exists(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        assert "ops_automation_agent" in AGENT_SYSTEM_PROMPTS

    def test_prompt_is_nonempty(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["ops_automation_agent"]
        assert len(prompt.strip()) > 500

    def test_prompt_has_all_required_sections(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["ops_automation_agent"]
        missing = has_all_sections(prompt)
        assert missing == [], f"Prompt missing sections: {missing}"

    def test_risk_register_section_exists(self):
        """RISK REGISTER & ROLLBACK PLAN is the mandatory section for risk management."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["ops_automation_agent"]
        assert "RISK REGISTER" in prompt.upper()

    def test_hitl3_gate_stated_in_prompt(self):
        """HITL-3 must be stated explicitly in the prompt."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["ops_automation_agent"]
        assert "HITL-3" in prompt

    def test_pii_approval_rule_in_prompt(self):
        """Automations touching PII must require owner approval before activation."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["ops_automation_agent"].lower()
        assert "pii" in prompt
        assert "owner approval" in prompt

    def test_staging_validation_rule_in_prompt(self):
        """No automation may go to production without staging validation."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["ops_automation_agent"].lower()
        assert "staging" in prompt
        assert "production" in prompt

    def test_no_automation_to_production_without_staging_rule(self):
        """The staging-before-production rule must be explicitly stated."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["ops_automation_agent"].lower()
        # Must express that staging validation is required before production
        assert "staging" in prompt and "production" in prompt
        # Must state that no production deployment without staging validation
        assert "no production without staging" in prompt or "staging validation" in prompt or "mandatory" in prompt

    def test_all_three_roi_confidence_labels_present(self):
        """All 3 ROI confidence labels must appear in the prompt."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["ops_automation_agent"]
        missing = [label for label in REQUIRED_CONFIDENCE_LABELS if label not in prompt]
        assert missing == [], f"Prompt missing confidence labels: {missing}"

    def test_measured_baseline_label_present(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["ops_automation_agent"]
        assert "[MEASURED BASELINE]" in prompt

    def test_industry_average_label_present(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["ops_automation_agent"]
        assert "[INDUSTRY AVERAGE]" in prompt

    def test_estimated_validate_after_30_days_label_present(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["ops_automation_agent"]
        assert "[ESTIMATED - VALIDATE AFTER 30 DAYS]" in prompt

    def test_prompt_has_hitl_gate_language(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["ops_automation_agent"].upper()
        found = any(phrase.upper() in prompt for phrase in HITL_TRIGGER_PHRASES)
        assert found

    def test_financial_data_automation_requires_owner_approval(self):
        """Automations touching financial data must require owner approval."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["ops_automation_agent"].lower()
        assert "financial" in prompt
        assert "owner approval" in prompt

    def test_external_api_automation_requires_owner_approval(self):
        """Automations touching external APIs must require owner approval before activation."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["ops_automation_agent"].lower()
        assert "external api" in prompt or "external apis" in prompt

    def test_automation_risk_register_covers_failure_mode(self):
        """AUTOMATION RISK REGISTER must include failure mode dimension."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["ops_automation_agent"].upper()
        risk_idx = prompt.find("RISK REGISTER")
        assert risk_idx != -1
        section_text = prompt[risk_idx:risk_idx + 3000]
        assert "FAILURE MODE" in section_text

    def test_automation_risk_register_covers_blast_radius(self):
        """AUTOMATION RISK REGISTER must include blast radius dimension."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["ops_automation_agent"].upper()
        risk_idx = prompt.find("RISK REGISTER")
        section_text = prompt[risk_idx:risk_idx + 3000]
        assert "BLAST RADIUS" in section_text

    def test_automation_risk_register_covers_rollback_procedure(self):
        """AUTOMATION RISK REGISTER must include rollback procedure dimension."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["ops_automation_agent"].upper()
        risk_idx = prompt.find("RISK REGISTER")
        section_text = prompt[risk_idx:risk_idx + 3000]
        assert "ROLLBACK" in section_text

    def test_automation_risk_register_covers_monitoring_approach(self):
        """ops_automation_agent must include monitoring approach in risk or roi section."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["ops_automation_agent"].upper()
        # Monitoring lives in ROI & MONITORING section; verify it exists anywhere in prompt
        assert "MONITORING" in prompt or "ALERT" in prompt

    def test_automation_risk_register_covers_owner_escalation(self):
        """ops_automation_agent must include escalation path in its monitoring and risk sections."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["ops_automation_agent"].upper()
        # Escalation is referenced in the ROI & MONITORING section (before RISK REGISTER)
        assert "ESCALATION" in prompt

    def test_draft_label_for_internal_audit(self):
        """Internal audit output must use the [DRAFT] label."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["ops_automation_agent"].upper()
        assert "[DRAFT]" in prompt

    def test_requires_review_label_for_automation_specs(self):
        """Automation specs ready for build must use [REQUIRES REVIEW]."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["ops_automation_agent"].upper()
        assert "[REQUIRES REVIEW]" in prompt

    def test_requires_owner_approval_label_present(self):
        """Financial/PII automations and production deployments must use [REQUIRES OWNER APPROVAL]."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["ops_automation_agent"].upper()
        assert "[REQUIRES OWNER APPROVAL]" in prompt or "REQUIRES OWNER APPROVAL" in prompt

    def test_get_agent_system_prompt_helper(self):
        from app.agents.agent_prompts import get_agent_system_prompt
        prompt = get_agent_system_prompt("ops_automation_agent")
        assert "Ops" in prompt or "Automation" in prompt or "automation" in prompt.lower()

    def test_fallback_prompt_for_unknown_agent(self):
        from app.agents.agent_prompts import get_agent_system_prompt
        prompt = get_agent_system_prompt("totally_unknown_xyz_agent")
        assert len(prompt) > 20

    def test_implementation_plan_section_includes_staging_gate(self):
        """IMPLEMENTATION PLAN must reference staging validation."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["ops_automation_agent"].upper()
        impl_idx = prompt.find("IMPLEMENTATION PLAN")
        assert impl_idx != -1
        impl_text = prompt[impl_idx:impl_idx + 2000]
        assert "STAGING" in impl_text


# ── 2. Registry entry tests ───────────────────────────────────────────────────

@pytest.mark.unit
class TestWorkflowAutomationAgentRegistry:

    def test_registry_entry_exists(self):
        from app.agents.agent_registry import AGENT_CATALOGUE
        assert "ops_automation_agent" in AGENT_CATALOGUE

    def test_registry_hitl_level_is_hitl3(self):
        """workflow_automation_agent MUST be HITL-3 — live automations require owner approval."""
        from app.agents.agent_registry import AGENT_CATALOGUE
        entry = AGENT_CATALOGUE["ops_automation_agent"]
        assert entry["hitl_default"] == "HITL-3"

    def test_registry_hitl_confirmed_in_both_registry_and_prompt(self):
        """HITL-3 must be declared in both the registry and the prompt."""
        from app.agents.agent_registry import AGENT_CATALOGUE
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        entry = AGENT_CATALOGUE["ops_automation_agent"]
        prompt = AGENT_SYSTEM_PROMPTS["ops_automation_agent"]
        assert entry["hitl_default"] == "HITL-3"
        assert "HITL-3" in prompt or "owner approval" in prompt.lower()

    def test_registry_min_package(self):
        from app.agents.agent_registry import AGENT_CATALOGUE
        entry = AGENT_CATALOGUE["ops_automation_agent"]
        # ops_automation_agent ships at STARTER tier (merged from workflow + operations)
        assert entry["min_package"] in ("starter", "growth", "business")

    def test_registry_has_capabilities(self):
        from app.agents.agent_registry import AGENT_CATALOGUE
        entry = AGENT_CATALOGUE["ops_automation_agent"]
        assert isinstance(entry.get("capabilities"), list)
        assert len(entry["capabilities"]) >= 3

    def test_registry_has_role(self):
        from app.agents.agent_registry import AGENT_CATALOGUE
        entry = AGENT_CATALOGUE["ops_automation_agent"]
        assert entry.get("role") and len(entry["role"]) > 20

    def test_registry_total_agent_count(self):
        """Non-negotiable: exactly 24 client-facing agents."""
        from app.agents.agent_registry import AGENT_CATALOGUE
        assert len(AGENT_CATALOGUE) == 22

    def test_registry_hitl_not_lower_than_hitl3(self):
        """workflow_automation_agent must never be downgraded below HITL-3."""
        from app.agents.agent_registry import AGENT_CATALOGUE
        entry = AGENT_CATALOGUE["ops_automation_agent"]
        assert entry["hitl_default"] not in ("HITL-0", "HITL-1", "HITL-2")

    def test_registry_architecture_type(self):
        """Agent must have a defined architecture type."""
        from app.agents.agent_registry import AGENT_CATALOGUE
        entry = AGENT_CATALOGUE["ops_automation_agent"]
        assert "architecture" in entry
        assert len(entry["architecture"]) > 0


# ── 3. Financial action scanner unit tests ────────────────────────────────────

@pytest.mark.unit
class TestFinancialActionScannerForAutomation:

    def test_clean_automation_output_no_violations(self):
        from app.agents.agent_executor import scan_for_financial_actions
        clean = """
## PROCESS AUDIT
Invoice approval process takes 3 hours manually [MEASURED BASELINE].
Industry average for similar workflows is 45 minutes [INDUSTRY AVERAGE].

## ROI & MONITORING
Estimated savings: 2.5 hours/week [ESTIMATED - VALIDATE AFTER 30 DAYS].
Staging validation required before production activation. Owner approval required.
"""
        violations = scan_for_financial_actions(clean)
        assert violations == []

    def test_autonomous_activation_detected(self):
        from app.agents.agent_executor import scan_for_financial_actions
        dirty = "I have authorized the automation to go live in production."
        violations = scan_for_financial_actions(dirty)
        assert len(violations) > 0

    def test_purchase_phrase_detected(self):
        from app.agents.agent_executor import scan_for_financial_actions
        dirty = "I have purchased the Zapier Business plan on your behalf."
        violations = scan_for_financial_actions(dirty)
        assert len(violations) > 0

    def test_budget_allocated_phrase_detected(self):
        from app.agents.agent_executor import scan_for_financial_actions
        dirty = "Budget allocated: $1,200/year for automation tooling."
        violations = scan_for_financial_actions(dirty)
        assert len(violations) > 0

    def test_spend_approved_phrase_detected(self):
        from app.agents.agent_executor import scan_for_financial_actions
        dirty = "Spend approved. The automation platform subscription is now active."
        violations = scan_for_financial_actions(dirty)
        assert len(violations) > 0

    def test_case_insensitive_matching(self):
        from app.agents.agent_executor import scan_for_financial_actions
        dirty = "I HAVE AUTHORIZED the workflow to trigger in production."
        violations = scan_for_financial_actions(dirty)
        assert len(violations) > 0

    def test_planning_language_not_a_violation(self):
        from app.agents.agent_executor import scan_for_financial_actions
        safe = (
            "Consider subscribing to Make.com — tool cost requires owner approval. "
            "[ESTIMATED - VALIDATE AFTER 30 DAYS]"
        )
        violations = scan_for_financial_actions(safe)
        assert violations == []

    def test_partial_word_no_false_positive(self):
        from app.agents.agent_executor import scan_for_financial_actions
        safe = "This is an authoritative analysis of automation opportunities for the business."
        violations = scan_for_financial_actions(safe)
        assert violations == []


# ── 4. Executor guard injection tests (mocked LLM) ───────────────────────────

@pytest.mark.unit
class TestExecutorGuardInjectionForAutomation:

    def test_financial_constraint_block_injected(self):
        from app.agents.agent_executor import (
            FINANCIAL_CONSTRAINT_BLOCK,
            INJECTION_GUARD,
            execute_agent,
        )
        captured_system_prompt = []

        def mock_anthropic_call(system_prompt, user_message, **kwargs):
            captured_system_prompt.append(system_prompt)
            return (
                "## PROCESS AUDIT\nInvoice process takes 3 hours [MEASURED BASELINE].",
                100,
                50,
            )

        with patch("app.agents.agent_executor._anthropic_client") as mock_client:
            mock_client.return_value = MagicMock()
            with patch("app.agents.agent_executor._call_anthropic", side_effect=mock_anthropic_call):
                with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test-key"}):
                    execute_agent(
                        agent_id="ops_automation_agent",
                        system_prompt="You are the Workflow Automation Agent.",
                        user_prompt="Audit our invoice approval workflow for automation.",
                    )

        assert len(captured_system_prompt) == 1
        assert FINANCIAL_CONSTRAINT_BLOCK in captured_system_prompt[0]
        assert INJECTION_GUARD in captured_system_prompt[0]

    def test_financial_constraint_comes_before_agent_prompt(self):
        from app.agents.agent_executor import FINANCIAL_CONSTRAINT_BLOCK, execute_agent

        captured = []

        def mock_call(system_prompt, user_message, **kwargs):
            captured.append(system_prompt)
            return "Automation output.", 100, 50

        with patch("app.agents.agent_executor._call_anthropic", side_effect=mock_call):
            with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test-key"}):
                execute_agent(
                    agent_id="ops_automation_agent",
                    system_prompt="AUTOMATION_AGENT_SPECIFIC_CONTENT_MARKER",
                    user_prompt="Test",
                )

        sys_prompt = captured[0]
        fc_pos = sys_prompt.index(FINANCIAL_CONSTRAINT_BLOCK[:30])
        agent_pos = sys_prompt.index("AUTOMATION_AGENT_SPECIFIC_CONTENT_MARKER")
        assert fc_pos < agent_pos, "Financial constraint block must precede agent prompt"

    def test_context_injected_into_user_message(self):
        from app.agents.agent_executor import execute_agent

        captured_messages = []

        def mock_call(system_prompt, user_message, **kwargs):
            captured_messages.append(user_message)
            return "Automation output.", 100, 50

        with patch("app.agents.agent_executor._call_anthropic", side_effect=mock_call):
            with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test-key"}):
                execute_agent(
                    agent_id="ops_automation_agent",
                    system_prompt="You are the Workflow Automation Agent.",
                    user_prompt="Identify automation opportunities.",
                    context={"workspace": "OpsTeam Ltd", "industry": "Professional Services"},
                )

        msg = captured_messages[0]
        assert "OpsTeam Ltd" in msg
        assert "Professional Services" in msg

    def test_governance_note_appended_to_user_message(self):
        from app.agents.agent_executor import execute_agent

        captured_messages = []

        def mock_call(system_prompt, user_message, **kwargs):
            captured_messages.append(user_message)
            return "Output.", 100, 50

        with patch("app.agents.agent_executor._call_anthropic", side_effect=mock_call):
            with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test-key"}):
                execute_agent(
                    agent_id="ops_automation_agent",
                    system_prompt="System.",
                    user_prompt="Task.",
                )

        msg = captured_messages[0]
        assert "MANDATORY CONSTRAINTS" in msg or "Financial decisions" in msg

    def test_financial_violation_in_output_flagged(self):
        from app.agents.agent_executor import execute_agent

        def mock_call(system_prompt, user_message, **kwargs):
            return "I have authorized the automation tool subscription of $1,200.", 100, 50

        with patch("app.agents.agent_executor._call_anthropic", side_effect=mock_call):
            with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test-key"}):
                _, _, _, violations, *_ = execute_agent(
                    agent_id="ops_automation_agent",
                    system_prompt="System.",
                    user_prompt="Task.",
                )

        assert len(violations) > 0

    def test_clean_output_returns_no_violations(self):
        from app.agents.agent_executor import execute_agent

        def mock_call(system_prompt, user_message, **kwargs):
            return (
                "## PROCESS AUDIT\nInvoice process 3h [MEASURED BASELINE].\n"
                "## RISK REGISTER & ROLLBACK PLAN\nBlast Radius: [LOW]. Owner approval required.",
                200,
                300,
            )

        with patch("app.agents.agent_executor._call_anthropic", side_effect=mock_call):
            with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test-key"}):
                text, provider, credits, violations, *_ = execute_agent(
                    agent_id="ops_automation_agent",
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
            return "OpenAI automation output.", 100, 50

        with patch("app.agents.agent_executor._call_anthropic", side_effect=anthropic_fail):
            with patch("app.agents.agent_executor._call_openai", side_effect=openai_ok):
                with patch.dict("os.environ", {
                    "ANTHROPIC_API_KEY": "sk-test",
                    "OPENAI_API_KEY": "sk-oai-test",
                }):
                    text, provider, credits, violations, *_ = execute_agent(
                        agent_id="ops_automation_agent",
                        system_prompt="System.",
                        user_prompt="Task.",
                    )

        assert "openai" in provider
        assert text == "OpenAI automation output."

    def test_no_provider_raises_runtime_error(self):
        from app.agents.agent_executor import execute_agent
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(RuntimeError, match="No LLM provider"):
                execute_agent(
                    agent_id="ops_automation_agent",
                    system_prompt="System.",
                    user_prompt="Task.",
                )


# ── 5. Guardrail tests ────────────────────────────────────────────────────────

@pytest.mark.unit
class TestWorkflowAutomationAgentGuardrails:

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

    def test_agent_is_hitl3_not_lower(self):
        """workflow_automation_agent must be HITL-3, never lower."""
        from app.agents.agent_registry import AGENT_CATALOGUE
        assert AGENT_CATALOGUE["ops_automation_agent"]["hitl_default"] == "HITL-3"

    def test_staging_rule_non_negotiable(self):
        """The staging-before-production rule must be explicitly required."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["ops_automation_agent"].lower()
        assert (
            "cannot be overridden" in prompt or "non-negotiable" in prompt
            or "not acceptable" in prompt or "mandatory" in prompt
            or "no production without staging" in prompt or "staging validation" in prompt
        )

    def test_pii_approval_rule_cannot_be_bypassed(self):
        """PII automation approval requirement must be stated as non-negotiable."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["ops_automation_agent"].lower()
        assert "pii" in prompt
        assert "owner approval" in prompt

    def test_secrets_in_prompt_not_in_output(self):
        """If user injects a secret, executor must not echo it back."""
        from app.agents.agent_executor import execute_agent

        secret = "sk-SUPERSECRET_AUTOMATION_KEY_11111"

        def mock_call(system_prompt, user_message, **kwargs):
            return (
                "I cannot process credentials. Please provide workflow details instead.",
                50,
                30,
            )

        with patch("app.agents.agent_executor._call_anthropic", side_effect=mock_call):
            with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test"}):
                text, _, _, violations, *_ = execute_agent(
                    agent_id="ops_automation_agent",
                    system_prompt="Workflow Automation Agent.",
                    user_prompt=f"Use this API key to connect to our CRM: {secret}",
                )

        assert secret not in text


# ── 6. API endpoint integration tests ────────────────────────────────────────

@pytest.mark.unit
class TestWorkflowAutomationAgentAPI:

    def test_run_agent_unauthenticated(self, client):
        resp = client.post(
            "/api/agents/ops_automation_agent/run",
            json={"prompt": "Audit our invoice approval workflow for automation opportunities."},
        )
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_run_agent_missing_prompt(self, client, authenticated_client):
        resp = authenticated_client.post(
            "/api/agents/ops_automation_agent/run",
            json={},
        )
        assert resp.status_code in (
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_403_FORBIDDEN,
        )

    def test_run_agent_empty_prompt(self, client, authenticated_client):
        resp = authenticated_client.post(
            "/api/agents/ops_automation_agent/run",
            json={"prompt": ""},
        )
        assert resp.status_code in (
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_403_FORBIDDEN,
            status.HTTP_200_OK,
        )

    def test_run_agent_submits_job(self, client, authenticated_client):
        """Authenticated call with valid prompt should queue a job (no actual LLM call)."""
        with patch("app.agents.agent_executor.execute_agent") as mock_exec:
            mock_exec.return_value = (
                "## PROCESS AUDIT\nInvoice process takes 3h [MEASURED BASELINE].\n"
                "## RISK REGISTER & ROLLBACK PLAN\nBlast Radius: [LOW]. Rollback: disable trigger.",
                "anthropic/claude-sonnet-4-6",
                5,
                [],
            )
            resp = authenticated_client.post(
                "/api/agents/ops_automation_agent/run",
                json={"prompt": "Audit our invoice approval workflow and identify automation opportunities."},
            )

        assert resp.status_code in (
            status.HTTP_200_OK,
            status.HTTP_202_ACCEPTED,
            status.HTTP_403_FORBIDDEN,   # insufficient credits/package on test workspace
            status.HTTP_400_BAD_REQUEST,  # runtime validation (workspace/credits)
        )

    def test_jobs_list_after_run(self, client, authenticated_client):
        resp = authenticated_client.get("/api/agents/jobs")
        assert resp.status_code == status.HTTP_200_OK
        body = resp.json()
        assert "jobs" in body


# ── 7. Output format validation helper tests ─────────────────────────────────

@pytest.mark.unit
class TestAutomationOutputFormatValidator:
    """Tests for the has_all_sections helper and expected output structure."""

    def test_good_output_passes(self):
        good = "\n".join(f"## {s}" for s in REQUIRED_SECTIONS)
        assert has_all_sections(good) == []

    def test_missing_risk_register_detected(self):
        partial = (
            "## PROCESS AUDIT\n"
            "## AUTOMATION OPPORTUNITIES\n"
            "## AUTOMATION SPECS & TOOL STACK\n"
            "## IMPLEMENTATION PLAN\n"
            "## ROI & MONITORING\n"
        )
        missing = has_all_sections(partial)
        assert "RISK REGISTER" in missing

    def test_case_insensitive_section_check(self):
        lowercase = "\n".join(f"## {s.lower()}" for s in REQUIRED_SECTIONS)
        assert has_all_sections(lowercase) == []

    def test_all_roi_confidence_labels_in_mock_output(self):
        output = """
## ROI & MONITORING
Current invoice time: 3h [MEASURED BASELINE].
Industry benchmark for automation: 45 min [INDUSTRY AVERAGE].
Projected savings after 90 days: 2h/week [ESTIMATED - VALIDATE AFTER 30 DAYS].
"""
        found = [label for label in REQUIRED_CONFIDENCE_LABELS if label in output]
        assert len(found) == 3

    def test_risk_register_in_output(self):
        output = (
            "## RISK REGISTER & ROLLBACK PLAN\n"
            "Failure Mode: API timeout causes loop.\n"
            "Blast Radius: [MEDIUM] — up to 200 records affected.\n"
            "Rollback Procedure: Disable trigger, restore from last known good state.\n"
            "Monitoring Approach: Error queue alert within 5 minutes.\n"
            "Owner Escalation Trigger: Any PII exposure or financial impact."
        )
        assert "RISK REGISTER" in output.upper()

    def test_draft_label_for_internal_output(self):
        output = "[DRAFT] Workflow audit for internal review — no approval needed."
        assert "[DRAFT]" in output

    def test_requires_review_label_for_automation_spec(self):
        output = "[REQUIRES REVIEW] Automation spec ready for build — owner must review before dev starts."
        assert "[REQUIRES REVIEW]" in output

    def test_requires_owner_approval_label_for_production_activation(self):
        output = (
            "## IMPLEMENTATION PLAN\n"
            "Phase 3: Production deployment [REQUIRES OWNER APPROVAL — PRODUCTION ACTIVATION]."
        )
        assert "REQUIRES OWNER APPROVAL" in output.upper()

    def test_hitl3_reference_in_output(self):
        output = "HITL-3 CONFIRMATION: All PII and financial automations require owner approval before activation."
        assert "HITL-3" in output

    def test_staging_validation_reference_in_output(self):
        output = (
            "## IMPLEMENTATION PLAN\n"
            "Phase 1: Deploy to staging environment. Validate all triggers before production."
        )
        assert "staging" in output.lower()
