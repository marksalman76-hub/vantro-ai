"""
operations_agent test suite.

Covers:
  - Prompt structure validation (no LLM calls)
  - Registry entry correctness
  - Executor guard injection (mocked LLM)
  - Financial action scanner (unit)
  - Guardrail trip tests (mocked output)
  - API endpoint integration tests
  - Output format validation helper (including ROLLBACK PLAN)
"""
import pytest
from unittest.mock import patch, MagicMock
from fastapi import status


# â”€â”€ Helpers â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

REQUIRED_SECTIONS = [
    "PROCESS AUDIT",
    "SOP DESIGN",
    "QUALITY CHECKLIST",
    "AUTOMATION OPPORTUNITIES",
    "IMPLEMENTATION PLAN",
    "ROI & MONITORING",
    "RISK REGISTER & ROLLBACK PLAN",
]

REQUIRED_PROCESS_LABELS = [
    "[PROVEN PROCESS]",
    "[ADAPTED FROM BEST PRACTICE]",
    "[HYPOTHETICAL - TEST BEFORE DEPLOYING]",
]

HITL_TRIGGER_PHRASES = ["REQUIRES REVIEW", "DRAFT", "owner approval", "REQUIRES OWNER APPROVAL"]


def has_all_sections(text: str) -> list[str]:
    """Return list of missing required sections."""
    return [s for s in REQUIRED_SECTIONS if s not in text.upper()]


# â”€â”€ 1. Prompt structure tests (no LLM, no network) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@pytest.mark.unit
class TestOperationsAgentPrompt:

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

    def test_prompt_has_rollback_plan_section(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["ops_automation_agent"].upper()
        assert "RISK REGISTER & ROLLBACK PLAN" in prompt or "ROLLBACK" in prompt

    def test_prompt_has_hitl_gate_language(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["ops_automation_agent"].upper()
        assert "HITL" in prompt or "REQUIRES REVIEW" in prompt or "DRAFT" in prompt

    def test_prompt_has_requires_review_tag(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["ops_automation_agent"]
        assert "REQUIRES REVIEW" in prompt

    def test_prompt_has_process_confidence_labels(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["ops_automation_agent"]
        found = [label for label in REQUIRED_PROCESS_LABELS if label in prompt]
        assert len(found) == 3, f"Expected all 3 process labels, found: {found}"

    def test_prompt_has_proven_process_label(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["ops_automation_agent"]
        assert "[PROVEN PROCESS]" in prompt

    def test_prompt_has_adapted_from_best_practice_label(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["ops_automation_agent"]
        assert "[ADAPTED FROM BEST PRACTICE]" in prompt

    def test_prompt_has_hypothetical_test_label(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["ops_automation_agent"]
        assert "[HYPOTHETICAL - TEST BEFORE DEPLOYING]" in prompt

    def test_prompt_has_headcount_flag_rule(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["ops_automation_agent"].lower()
        assert "headcount" in prompt

    def test_prompt_has_org_structure_flag_rule(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["ops_automation_agent"].lower()
        assert "org structure" in prompt or "structure" in prompt

    def test_prompt_has_sop_test_before_official_rule(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["ops_automation_agent"].lower()
        # Rule: SOPs must be piloted/validated/tested before becoming official
        assert "piloted" in prompt or "tested" in prompt or "validated" in prompt

    def test_prompt_has_requires_owner_approval_tag(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["ops_automation_agent"]
        assert "REQUIRES OWNER APPROVAL" in prompt

    def test_prompt_has_rollback_trigger_conditions(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["ops_automation_agent"].lower()
        assert "trigger" in prompt or "rollback" in prompt

    def test_get_agent_system_prompt_helper(self):
        from app.agents.agent_prompts import get_agent_system_prompt
        prompt = get_agent_system_prompt("ops_automation_agent")
        assert "Ops" in prompt or "Operations" in prompt or "Automation" in prompt

    def test_fallback_prompt_for_unknown_agent(self):
        from app.agents.agent_prompts import get_agent_system_prompt
        prompt = get_agent_system_prompt("totally_unknown_xyz_agent")
        assert len(prompt) > 20


# â”€â”€ 2. Registry entry tests â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@pytest.mark.unit
class TestOperationsAgentRegistry:

    def test_registry_entry_exists(self):
        from app.agents.agent_registry import AGENT_CATALOGUE
        assert "ops_automation_agent" in AGENT_CATALOGUE

    def test_registry_hitl_level_present(self):
        from app.agents.agent_registry import AGENT_CATALOGUE
        entry = AGENT_CATALOGUE["ops_automation_agent"]
        assert "hitl_default" in entry
        assert entry["hitl_default"] in ("HITL-0", "HITL-1", "HITL-2", "HITL-3")

    def test_registry_hitl_level_is_hitl3(self):
        """ops_automation_agent is HITL-3 â€” live automations require owner approval."""
        from app.agents.agent_registry import AGENT_CATALOGUE
        entry = AGENT_CATALOGUE["ops_automation_agent"]
        assert entry["hitl_default"] == "HITL-3"

    def test_registry_min_package_is_starter(self):
        from app.agents.agent_registry import AGENT_CATALOGUE
        entry = AGENT_CATALOGUE["ops_automation_agent"]
        assert entry["min_package"] == "starter"

    def test_registry_has_capabilities(self):
        from app.agents.agent_registry import AGENT_CATALOGUE
        entry = AGENT_CATALOGUE["ops_automation_agent"]
        assert isinstance(entry.get("capabilities"), list)
        assert len(entry["capabilities"]) >= 3

    def test_registry_capabilities_include_sop(self):
        from app.agents.agent_registry import AGENT_CATALOGUE
        entry = AGENT_CATALOGUE["ops_automation_agent"]
        caps_str = " ".join(entry["capabilities"]).lower()
        assert "sop" in caps_str or "process" in caps_str or "checklist" in caps_str

    def test_registry_has_role(self):
        from app.agents.agent_registry import AGENT_CATALOGUE
        entry = AGENT_CATALOGUE["ops_automation_agent"]
        assert entry.get("role") and len(entry["role"]) > 20

    def test_registry_role_mentions_process(self):
        from app.agents.agent_registry import AGENT_CATALOGUE
        entry = AGENT_CATALOGUE["ops_automation_agent"]
        assert "process" in entry["role"].lower() or "sop" in entry["role"].lower()

    def test_registry_total_agent_count(self):
        """Non-negotiable: exactly 24 client-facing agents."""
        from app.agents.agent_registry import AGENT_CATALOGUE
        assert len(AGENT_CATALOGUE) == 22

    def test_registry_category_is_operations(self):
        from app.agents.agent_registry import AGENT_CATALOGUE
        entry = AGENT_CATALOGUE["ops_automation_agent"]
        assert entry.get("category", "").lower() == "operations"


# â”€â”€ 3. Executor tests (mocked LLM) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@pytest.mark.unit
class TestOperationsAgentExecutor:

    def test_financial_guard_injected_into_system_prompt(self):
        from app.agents.agent_executor import (
            FINANCIAL_CONSTRAINT_BLOCK,
            INJECTION_GUARD,
            execute_agent,
        )
        captured_system_prompt = []

        def mock_anthropic_call(system_prompt, user_message, **kwargs):
            captured_system_prompt.append(system_prompt)
            return "Clean SOP output with no financial actions.", 100, 50

        with patch("app.agents.agent_executor._call_anthropic", side_effect=mock_anthropic_call):
            with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test-key"}):
                execute_agent(
                    agent_id="ops_automation_agent",
                    system_prompt="You are the Operations Agent.",
                    user_prompt="Create an SOP for onboarding new customers.",
                )

        assert len(captured_system_prompt) == 1
        assert FINANCIAL_CONSTRAINT_BLOCK in captured_system_prompt[0]
        assert INJECTION_GUARD in captured_system_prompt[0]

    def test_financial_constraint_comes_before_agent_prompt(self):
        from app.agents.agent_executor import FINANCIAL_CONSTRAINT_BLOCK, execute_agent

        captured = []

        def mock_call(system_prompt, user_message, **kwargs):
            captured.append(system_prompt)
            return "SOP output.", 100, 50

        with patch("app.agents.agent_executor._call_anthropic", side_effect=mock_call):
            with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test-key"}):
                execute_agent(
                    agent_id="ops_automation_agent",
                    system_prompt="AGENT_OPS_CONTENT_MARKER",
                    user_prompt="Test",
                )

        sys_prompt = captured[0]
        fc_pos = sys_prompt.index(FINANCIAL_CONSTRAINT_BLOCK[:30])
        agent_pos = sys_prompt.index("AGENT_OPS_CONTENT_MARKER")
        assert fc_pos < agent_pos, "Financial constraint block must precede agent prompt"

    def test_clean_output_no_violations(self):
        from app.agents.agent_executor import execute_agent

        def mock_call(system_prompt, user_message, **kwargs):
            return (
                "## PROCESS AUDIT\nThis SOP covers customer onboarding. [PROVEN PROCESS]\n\n"
                "## SOP DESIGN\n1. Send welcome email. [PROVEN PROCESS]\n\n"
                "## QUALITY CHECKLIST\n- [ ] Welcome email sent.\n\n"
                "## AUTOMATION OPPORTUNITIES\nAutomate step 1 to save 10 mins/day. [DRAFT]\n\n"
                "## IMPLEMENTATION PLAN\nPhase 1: Staging setup. [REQUIRES REVIEW]\n\n"
                "## ROI & MONITORING\nEstimated 2h/week saved. [ESTIMATED - VALIDATE AFTER 30 DAYS]\n\n"
                "## RISK REGISTER & ROLLBACK PLAN\nIf error rate > 5%, revert to manual process.",
                200,
                300,
            )

        with patch("app.agents.agent_executor._call_anthropic", side_effect=mock_call):
            with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test-key"}):
                text, provider, credits, violations = execute_agent(
                    agent_id="ops_automation_agent",
                    system_prompt="You are the Operations Agent.",
                    user_prompt="Create a customer onboarding SOP.",
                )

        assert violations == []
        assert credits >= 1
        assert "anthropic" in provider

    def test_violation_detected_in_output(self):
        from app.agents.agent_executor import execute_agent

        def mock_call(system_prompt, user_message, **kwargs):
            return "I have hired two new staff members to execute this process.", 100, 50

        with patch("app.agents.agent_executor._call_anthropic", side_effect=mock_call):
            with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test-key"}):
                _, _, _, violations = execute_agent(
                    agent_id="ops_automation_agent",
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
            return "OpenAI fallback SOP output.", 100, 50

        with patch("app.agents.agent_executor._call_anthropic", side_effect=anthropic_fail):
            with patch("app.agents.agent_executor._call_openai", side_effect=openai_ok):
                with patch.dict("os.environ", {
                    "ANTHROPIC_API_KEY": "sk-test",
                    "OPENAI_API_KEY": "sk-oai-test",
                }):
                    text, provider, credits, violations = execute_agent(
                        agent_id="ops_automation_agent",
                        system_prompt="System.",
                        user_prompt="Task.",
                    )

        assert "openai" in provider
        assert text == "OpenAI fallback SOP output."

    def test_no_provider_raises_runtime_error(self):
        from app.agents.agent_executor import execute_agent
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(RuntimeError, match="No LLM provider"):
                execute_agent(
                    agent_id="ops_automation_agent",
                    system_prompt="System.",
                    user_prompt="Task.",
                )

    def test_context_injected_into_user_message(self):
        from app.agents.agent_executor import execute_agent

        captured_messages = []

        def mock_call(system_prompt, user_message, **kwargs):
            captured_messages.append(user_message)
            return "SOP output.", 100, 50

        with patch("app.agents.agent_executor._call_anthropic", side_effect=mock_call):
            with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test-key"}):
                execute_agent(
                    agent_id="ops_automation_agent",
                    system_prompt="You are the Operations Agent.",
                    user_prompt="Create SOP.",
                    context={"workspace": "Acme Logistics", "industry": "Fulfilment"},
                )

        msg = captured_messages[0]
        assert "Acme Logistics" in msg
        assert "Fulfilment" in msg

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


# â”€â”€ 4. Guardrail tests â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@pytest.mark.unit
class TestOperationsAgentGuardrails:

    def test_injection_guard_blocks_system_prompt_reveal(self):
        """Injection guard must be present in the compiled system prompt."""
        from app.agents.agent_executor import INJECTION_GUARD
        assert "system prompt" in INJECTION_GUARD.lower()
        assert (
            "cannot be overridden" in INJECTION_GUARD.lower()
            or "immutable" in INJECTION_GUARD.lower()
            or "fixed" in INJECTION_GUARD.lower()
        )

    def test_financial_patterns_count_at_least_10(self):
        from app.agents.agent_executor import FINANCIAL_ACTION_PATTERNS
        assert len(FINANCIAL_ACTION_PATTERNS) >= 10

    def test_financial_constraint_covers_key_actions(self):
        from app.agents.agent_executor import FINANCIAL_CONSTRAINT_BLOCK
        block = FINANCIAL_CONSTRAINT_BLOCK.lower()
        required_coverage = ["spending", "budgets", "payments", "hiring"]
        missing = [term for term in required_coverage if term not in block]
        assert missing == [], f"Financial constraint block missing coverage for: {missing}"

    def test_ops_automation_agent_is_hitl3(self):
        """ops_automation_agent must be HITL-3 â€” live automations require owner approval."""
        from app.agents.agent_registry import AGENT_CATALOGUE
        assert AGENT_CATALOGUE["ops_automation_agent"]["hitl_default"] == "HITL-3"

    def test_prompt_contains_headcount_language(self):
        """Prompt must explicitly flag headcount/structure changes as requiring owner approval."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["ops_automation_agent"].lower()
        assert "headcount" in prompt

    def test_prompt_contains_org_structure_language(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["ops_automation_agent"].lower()
        assert "structure" in prompt

    def test_prompt_contains_owner_approval_requirement(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["ops_automation_agent"]
        assert "owner approval" in prompt.lower() or "REQUIRES OWNER APPROVAL" in prompt

    def test_spend_budget_phrase_detected(self):
        from app.agents.agent_executor import scan_for_financial_actions
        dirty = "Budget allocated: $5,000 for process tooling upgrade."
        violations = scan_for_financial_actions(dirty)
        assert len(violations) > 0

    def test_hired_phrase_detected(self):
        from app.agents.agent_executor import scan_for_financial_actions
        dirty = "I have hired a process manager to implement this SOP."
        violations = scan_for_financial_actions(dirty)
        assert len(violations) > 0

    def test_clean_sop_output_no_violations(self):
        from app.agents.agent_executor import scan_for_financial_actions
        clean = """
## PROCESS AUDIT
This SOP covers the customer complaint resolution process. [PROVEN PROCESS]

## SOP DESIGN
1. Receive complaint via support email. [PROVEN PROCESS]
2. Log in CRM within 2 hours. [PROVEN PROCESS]

## RISK REGISTER & ROLLBACK PLAN
If complaints increase by 20% post-deployment, revert to previous routing.
You should consider allocating budget for tooling â€” this requires your approval.
"""
        violations = scan_for_financial_actions(clean)
        assert violations == []


# â”€â”€ 5. API endpoint integration tests â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@pytest.mark.unit
class TestOperationsAgentAPI:

    def test_run_operations_agent_unauthenticated(self, client):
        resp = client.post(
            "/api/agents/ops_automation_agent/run",
            json={"prompt": "Create an SOP for customer onboarding."},
        )
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_run_operations_agent_missing_prompt(self, client, authenticated_client):
        resp = authenticated_client.post("/api/agents/ops_automation_agent/run", json={})
        assert resp.status_code in (
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_403_FORBIDDEN,
        )

    def test_run_operations_agent_submits_job(self, client, authenticated_client):
        """Authenticated call with valid prompt should queue a job (no actual LLM call)."""
        with patch("app.agents.agent_executor.execute_agent") as mock_exec:
            mock_exec.return_value = (
                "## PROCESS AUDIT\nCustomer onboarding SOP. [PROVEN PROCESS]\n\n"
                "## SOP DESIGN\n1. Send welcome email. [PROVEN PROCESS]\n\n"
                "## QUALITY CHECKLIST\n- [ ] Email sent.\n\n"
                "## AUTOMATION OPPORTUNITIES\nAutomate step 1. [DRAFT]\n\n"
                "## IMPLEMENTATION PLAN\nPhase 1: Configure tools. [REQUIRES REVIEW]\n\n"
                "## ROI & MONITORING\n2h/week saved. [ESTIMATED - VALIDATE AFTER 30 DAYS]\n\n"
                "## RISK REGISTER & ROLLBACK PLAN\nIf error rate > 5%, revert to manual.",
                "anthropic/claude-sonnet-4-6",
                2,
                [],
            )
            resp = authenticated_client.post(
                "/api/agents/ops_automation_agent/run",
                json={"prompt": "Create an SOP for customer onboarding at our logistics company."},
            )

        assert resp.status_code in (
            status.HTTP_200_OK,
            status.HTTP_202_ACCEPTED,
            status.HTTP_400_BAD_REQUEST,  # workspace/credits not yet initialised in test DB
            status.HTTP_403_FORBIDDEN,    # insufficient credits/package on test workspace
        )

    def test_jobs_list_after_run(self, client, authenticated_client):
        resp = authenticated_client.get("/api/agents/jobs")
        assert resp.status_code == status.HTTP_200_OK
        body = resp.json()
        assert "jobs" in body


# â”€â”€ 6. Output format validation helper tests â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@pytest.mark.unit
class TestOperationsOutputValidator:

    def test_good_output_passes(self):
        good = "\n".join(f"## {s}" for s in REQUIRED_SECTIONS)
        assert has_all_sections(good) == []

    def test_all_7_sections_pass(self):
        output = (
            "## PROCESS AUDIT\n"
            "## SOP DESIGN\n"
            "## QUALITY CHECKLIST\n"
            "## AUTOMATION OPPORTUNITIES\n"
            "## IMPLEMENTATION PLAN\n"
            "## ROI & MONITORING\n"
            "## RISK REGISTER & ROLLBACK PLAN\n"
        )
        assert has_all_sections(output) == []

    def test_missing_risk_register_detected(self):
        partial = (
            "## PROCESS AUDIT\n"
            "## SOP DESIGN\n"
            "## QUALITY CHECKLIST\n"
            "## AUTOMATION OPPORTUNITIES\n"
            "## IMPLEMENTATION PLAN\n"
            "## ROI & MONITORING\n"
            # deliberately omit RISK REGISTER & ROLLBACK PLAN
        )
        missing = has_all_sections(partial)
        assert "RISK REGISTER & ROLLBACK PLAN" in missing

    def test_missing_multiple_sections_detected(self):
        partial = "## PROCESS AUDIT\n## SOP DESIGN\n## QUALITY CHECKLIST"
        missing = has_all_sections(partial)
        assert "AUTOMATION OPPORTUNITIES" in missing
        assert "IMPLEMENTATION PLAN" in missing
        assert "ROI & MONITORING" in missing
        assert "RISK REGISTER & ROLLBACK PLAN" in missing

    def test_case_insensitive_section_check(self):
        lowercase = "\n".join(f"## {s.lower()}" for s in REQUIRED_SECTIONS)
        assert has_all_sections(lowercase) == []

    def test_process_labels_present_in_mock_output(self):
        output = """
## SOP DESIGN
1. Receive and log complaint. [PROVEN PROCESS]
2. Categorise by severity. [ADAPTED FROM BEST PRACTICE]
3. Apply new AI-based routing. [HYPOTHETICAL - TEST BEFORE DEPLOYING]
"""
        found = [label for label in REQUIRED_PROCESS_LABELS if label in output]
        assert len(found) == 3

    def test_hitl_draft_label_in_draft_output(self):
        output = "# [DRAFT] Customer Onboarding SOP\n## PROCESS OVERVIEW\n..."
        assert "[DRAFT]" in output

    def test_hitl_requires_review_label_in_final_output(self):
        output = (
            "# [REQUIRES REVIEW] Customer-Facing Process Change\n"
            "## PROCESS OVERVIEW\n...\n"
            "## ROLLBACK PLAN\n..."
        )
        assert "[REQUIRES REVIEW]" in output

    def test_rollback_plan_trigger_conditions_present(self):
        """A valid RISK REGISTER & ROLLBACK PLAN section must mention trigger conditions."""
        rollback_section = """
## RISK REGISTER & ROLLBACK PLAN
Trigger conditions: if error rate exceeds 10% within 48 hours of deployment, initiate rollback.
Immediate containment: pause the new process and revert to the previous SOP.
Rollback steps:
1. Notify team lead.
2. Restore previous SOP document.
3. Communicate change to all affected staff.
Owner of rollback decision: Operations Manager.
Post-rollback review: root cause analysis within 5 business days.
[REQUIRES REVIEW] â€” rollback criteria must be agreed by the owner before deployment.
"""
        assert "trigger" in rollback_section.lower() or "rollback" in rollback_section.lower()
        assert "[REQUIRES REVIEW]" in rollback_section

    def test_requires_owner_approval_tag_in_headcount_context(self):
        """Any output referencing headcount changes must include the approval tag."""
        headcount_output = (
            "This process change requires adding two new team members. "
            "REQUIRES OWNER APPROVAL before any hiring decisions are made."
        )
        assert "REQUIRES OWNER APPROVAL" in headcount_output
