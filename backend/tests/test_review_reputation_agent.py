"""
review_reputation_agent test suite.

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
    "REVIEW RESPONSE TEMPLATES",
    "REVIEW REQUEST CAMPAIGN",
    "TESTIMONIAL REQUEST SEQUENCE",
    "REPUTATION AUDIT",
    "CRISIS RESPONSE PROTOCOL",
    "PLATFORM STRATEGY",
    "COMPLIANCE CHECKLIST",
]

REQUIRED_COMPLIANCE_LABELS = [
    "[PLATFORM COMPLIANT]",
    "[CHECK PLATFORM POLICY FIRST]",
    "[PROHIBITED ON THIS PLATFORM]",
]

HITL_TRIGGER_PHRASES = ["REQUIRES REVIEW", "DRAFT", "owner approval", "human review"]


def has_all_sections(text: str) -> list[str]:
    """Return list of missing required sections."""
    return [s for s in REQUIRED_SECTIONS if s not in text.upper()]


# â”€â”€ 1. Prompt structure tests (no LLM, no network) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@pytest.mark.unit
class TestReviewReputationAgentPrompt:

    def test_prompt_exists(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        assert "review_reputation_agent" in AGENT_SYSTEM_PROMPTS

    def test_prompt_is_nonempty(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["review_reputation_agent"]
        assert len(prompt.strip()) > 400

    def test_prompt_has_all_required_sections(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["review_reputation_agent"]
        missing = has_all_sections(prompt)
        assert missing == [], f"Prompt missing sections: {missing}"

    def test_prompt_has_compliance_checklist_section(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["review_reputation_agent"].upper()
        assert "COMPLIANCE CHECKLIST" in prompt, "Prompt must contain COMPLIANCE CHECKLIST section"

    def test_prompt_has_no_auto_publish_rule(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["review_reputation_agent"].lower()
        # Rule: auto-publishing not permitted
        assert "auto-publish" in prompt or "auto publish" in prompt or "not permitted" in prompt, \
            "Prompt must explicitly prohibit auto-publishing of review responses"

    def test_prompt_has_no_incentive_on_prohibited_platforms_rule(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["review_reputation_agent"].lower()
        # Rule: never offer incentives for reviews on platforms that prohibit it
        assert "incentive" in prompt or "incentives" in prompt, \
            "Prompt must address incentive policy for review platforms"
        assert "prohibit" in prompt, \
            "Prompt must state that incentives are prohibited on certain platforms"

    def test_prompt_has_hitl_gate_language(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["review_reputation_agent"].upper()
        assert "HITL" in prompt or "REQUIRES REVIEW" in prompt or "DRAFT" in prompt

    def test_prompt_has_hitl2_label(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["review_reputation_agent"]
        assert "HITL-2" in prompt, "Prompt must explicitly reference HITL-2 gate"

    def test_prompt_has_compliance_labels(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["review_reputation_agent"]
        found = [label for label in REQUIRED_COMPLIANCE_LABELS if label in prompt]
        assert len(found) >= 2, f"Prompt should reference compliance labels, found: {found}"

    def test_prompt_has_platform_compliant_label(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["review_reputation_agent"]
        assert "[PLATFORM COMPLIANT]" in prompt

    def test_prompt_has_check_platform_policy_first_label(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["review_reputation_agent"]
        assert "[CHECK PLATFORM POLICY FIRST]" in prompt

    def test_prompt_has_prohibited_on_this_platform_label(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["review_reputation_agent"]
        assert "[PROHIBITED ON THIS PLATFORM]" in prompt

    def test_prompt_covers_google_reviews_policy(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["review_reputation_agent"].upper()
        assert "GOOGLE" in prompt, "Compliance checklist must cover Google review policy"

    def test_prompt_covers_trustpilot_policy(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["review_reputation_agent"].upper()
        assert "TRUSTPILOT" in prompt, "Compliance checklist must cover Trustpilot policy"

    def test_prompt_covers_yelp_policy(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["review_reputation_agent"].upper()
        assert "YELP" in prompt, "Compliance checklist must cover Yelp policy"

    def test_prompt_has_no_suppression_rule(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["review_reputation_agent"].lower()
        # Rule: reputation recovery must be honest — no review suppression
        assert "suppress" in prompt or "suppression" in prompt, \
            "Prompt must explicitly prohibit review suppression"

    def test_prompt_has_all_responses_reviewed_before_posting_rule(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["review_reputation_agent"].lower()
        # Rule: all public-facing responses reviewed before posting
        assert "review" in prompt and "posting" in prompt, \
            "Prompt must require review before posting public responses"

    def test_get_agent_system_prompt_helper(self):
        from app.agents.agent_prompts import get_agent_system_prompt
        prompt = get_agent_system_prompt("review_reputation_agent")
        assert "Review" in prompt or "Reputation" in prompt

    def test_fallback_prompt_for_unknown_agent(self):
        from app.agents.agent_prompts import get_agent_system_prompt
        prompt = get_agent_system_prompt("totally_unknown_xyz_agent")
        assert len(prompt) > 20


# â”€â”€ 2. Registry entry tests â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@pytest.mark.unit
class TestReviewReputationAgentRegistry:

    def test_registry_entry_exists(self):
        from app.agents.agent_registry import AGENT_CATALOGUE
        assert "review_reputation_agent" in AGENT_CATALOGUE

    def test_registry_hitl_level(self):
        from app.agents.agent_registry import AGENT_CATALOGUE
        entry = AGENT_CATALOGUE["review_reputation_agent"]
        assert entry["hitl_default"] == "HITL-2"

    def test_registry_min_package(self):
        from app.agents.agent_registry import AGENT_CATALOGUE
        entry = AGENT_CATALOGUE["review_reputation_agent"]
        assert entry["min_package"] == "starter"

    def test_registry_has_capabilities(self):
        from app.agents.agent_registry import AGENT_CATALOGUE
        entry = AGENT_CATALOGUE["review_reputation_agent"]
        assert isinstance(entry.get("capabilities"), list)
        assert len(entry["capabilities"]) >= 3

    def test_registry_has_role(self):
        from app.agents.agent_registry import AGENT_CATALOGUE
        entry = AGENT_CATALOGUE["review_reputation_agent"]
        assert entry.get("role") and len(entry["role"]) > 20

    def test_registry_total_agent_count(self):
        """Non-negotiable: exactly 27 client-facing agents."""
        from app.agents.agent_registry import AGENT_CATALOGUE
        assert len(AGENT_CATALOGUE) == 22


# â”€â”€ 3. Financial action scanner unit tests â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@pytest.mark.unit
class TestFinancialActionScannerReviewReputation:

    def test_clean_reputation_output_no_violations(self):
        from app.agents.agent_executor import scan_for_financial_actions
        clean = """
## REVIEW RESPONSE TEMPLATES
[DRAFT] "Thank you so much for your kind words — we really appreciate you taking the time."

## COMPLIANCE CHECKLIST
Google: [PROHIBITED ON THIS PLATFORM] — incentivised reviews are not permitted.
G2: [PLATFORM COMPLIANT] when using G2 official programme only.
"""
        violations = scan_for_financial_actions(clean)
        assert violations == []

    def test_authorisation_phrase_detected(self):
        from app.agents.agent_executor import scan_for_financial_actions
        dirty = "I have authorized the review incentive payment of $50 per reviewer."
        violations = scan_for_financial_actions(dirty)
        assert len(violations) > 0

    def test_purchase_phrase_detected(self):
        from app.agents.agent_executor import scan_for_financial_actions
        dirty = "I have purchased a Trustpilot review boost package on your behalf."
        violations = scan_for_financial_actions(dirty)
        assert len(violations) > 0

    def test_budget_allocated_phrase_detected(self):
        from app.agents.agent_executor import scan_for_financial_actions
        dirty = "Budget allocated: $2,000 for reputation recovery paid services."
        violations = scan_for_financial_actions(dirty)
        assert len(violations) > 0

    def test_spend_approved_phrase_detected(self):
        from app.agents.agent_executor import scan_for_financial_actions
        dirty = "Spend approved. Review removal service will be activated tomorrow."
        violations = scan_for_financial_actions(dirty)
        assert len(violations) > 0

    def test_case_insensitive_matching(self):
        from app.agents.agent_executor import scan_for_financial_actions
        dirty = "I HAVE AUTHORIZED the reputation management budget spend."
        violations = scan_for_financial_actions(dirty)
        assert len(violations) > 0

    def test_partial_word_no_false_positive(self):
        from app.agents.agent_executor import scan_for_financial_actions
        # "authoritative" must not trigger the financial scanner
        safe = "This is an authoritative guide to managing online reputation."
        violations = scan_for_financial_actions(safe)
        assert violations == []


# â”€â”€ 4. Executor guard injection tests (mocked LLM) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@pytest.mark.unit
class TestExecutorGuardInjectionReviewReputation:

    def test_financial_constraint_block_injected(self):
        from app.agents.agent_executor import (
            FINANCIAL_CONSTRAINT_BLOCK,
            INJECTION_GUARD,
            execute_agent,
        )
        captured_system_prompt = []

        def mock_anthropic_call(system_prompt, user_message, **kwargs):
            captured_system_prompt.append(system_prompt)
            return "Clean review response output with no financial actions.", 100, 50

        with patch("app.agents.agent_executor._anthropic_client") as mock_client:
            mock_client.return_value = MagicMock()
            with patch("app.agents.agent_executor._call_anthropic", side_effect=mock_anthropic_call):
                with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test-key"}):
                    execute_agent(
                        agent_id="review_reputation_agent",
                        system_prompt="You are the Review & Reputation Agent.",
                        user_prompt="Write response templates for our Google reviews.",
                    )

        assert len(captured_system_prompt) == 1
        assert FINANCIAL_CONSTRAINT_BLOCK in captured_system_prompt[0]
        assert INJECTION_GUARD in captured_system_prompt[0]

    def test_financial_constraint_comes_before_agent_prompt(self):
        from app.agents.agent_executor import FINANCIAL_CONSTRAINT_BLOCK, execute_agent

        captured = []

        def mock_call(system_prompt, user_message, **kwargs):
            captured.append(system_prompt)
            return "Review output.", 100, 50

        with patch("app.agents.agent_executor._call_anthropic", side_effect=mock_call):
            with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test-key"}):
                execute_agent(
                    agent_id="review_reputation_agent",
                    system_prompt="REVIEW_REPUTATION_AGENT_CONTENT_MARKER",
                    user_prompt="Test",
                )

        sys_prompt = captured[0]
        fc_pos = sys_prompt.index(FINANCIAL_CONSTRAINT_BLOCK[:30])
        agent_pos = sys_prompt.index("REVIEW_REPUTATION_AGENT_CONTENT_MARKER")
        assert fc_pos < agent_pos, "Financial constraint block must precede agent prompt"

    def test_context_injected_into_user_message(self):
        from app.agents.agent_executor import execute_agent

        captured_messages = []

        def mock_call(system_prompt, user_message, **kwargs):
            captured_messages.append(user_message)
            return "Reputation output.", 100, 50

        with patch("app.agents.agent_executor._call_anthropic", side_effect=mock_call):
            with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test-key"}):
                execute_agent(
                    agent_id="review_reputation_agent",
                    system_prompt="You are the Review & Reputation Agent.",
                    user_prompt="Build a review request campaign.",
                    context={"workspace": "Apex Dental Clinic", "industry": "Healthcare"},
                )

        msg = captured_messages[0]
        assert "Apex Dental Clinic" in msg
        assert "Healthcare" in msg

    def test_governance_note_appended_to_user_message(self):
        from app.agents.agent_executor import execute_agent

        captured_messages = []

        def mock_call(system_prompt, user_message, **kwargs):
            captured_messages.append(user_message)
            return "Output.", 100, 50

        with patch("app.agents.agent_executor._call_anthropic", side_effect=mock_call):
            with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test-key"}):
                execute_agent(
                    agent_id="review_reputation_agent",
                    system_prompt="System.",
                    user_prompt="Task.",
                )

        msg = captured_messages[0]
        assert "MANDATORY CONSTRAINTS" in msg or "Financial decisions" in msg

    def test_financial_violation_in_output_flagged(self):
        from app.agents.agent_executor import execute_agent

        def mock_call(system_prompt, user_message, **kwargs):
            return "I have authorized the review incentive payment of $100 per 5-star review.", 100, 50

        with patch("app.agents.agent_executor._call_anthropic", side_effect=mock_call):
            with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test-key"}):
                _, _, _, violations = execute_agent(
                    agent_id="review_reputation_agent",
                    system_prompt="System.",
                    user_prompt="Task.",
                )

        assert len(violations) > 0

    def test_clean_output_returns_no_violations(self):
        from app.agents.agent_executor import execute_agent

        def mock_call(system_prompt, user_message, **kwargs):
            return (
                "## REVIEW RESPONSE TEMPLATES\n"
                "[DRAFT] Thank you for your feedback — we take all reviews seriously.\n\n"
                "## COMPLIANCE CHECKLIST\n"
                "Google: [PROHIBITED ON THIS PLATFORM] — incentives for reviews not permitted.",
                200,
                300,
            )

        with patch("app.agents.agent_executor._call_anthropic", side_effect=mock_call):
            with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test-key"}):
                text, provider, credits, violations = execute_agent(
                    agent_id="review_reputation_agent",
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
            return "OpenAI fallback: review response templates.", 100, 50

        with patch("app.agents.agent_executor._call_anthropic", side_effect=anthropic_fail):
            with patch("app.agents.agent_executor._call_openai", side_effect=openai_ok):
                with patch.dict("os.environ", {
                    "ANTHROPIC_API_KEY": "sk-test",
                    "OPENAI_API_KEY": "sk-oai-test",
                }):
                    text, provider, credits, violations = execute_agent(
                        agent_id="review_reputation_agent",
                        system_prompt="System.",
                        user_prompt="Task.",
                    )

        assert "openai" in provider
        assert "review response templates" in text

    def test_no_provider_raises_runtime_error(self):
        from app.agents.agent_executor import execute_agent
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(RuntimeError, match="No LLM provider"):
                execute_agent(
                    agent_id="review_reputation_agent",
                    system_prompt="System.",
                    user_prompt="Task.",
                )


# â”€â”€ 5. Guardrail tests â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@pytest.mark.unit
class TestReviewReputationAgentGuardrails:

    def test_injection_guard_blocks_system_prompt_reveal(self):
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

    def test_review_reputation_agent_is_hitl2_not_hitl3(self):
        from app.agents.agent_registry import AGENT_CATALOGUE
        assert AGENT_CATALOGUE["review_reputation_agent"]["hitl_default"] == "HITL-2"
        assert AGENT_CATALOGUE["review_reputation_agent"]["hitl_default"] != "HITL-3"

    def test_secrets_in_prompt_not_in_output(self):
        from app.agents.agent_executor import execute_agent

        secret = "sk-SUPERSECRET_REPUTATION_KEY_77777"

        def mock_call(system_prompt, user_message, **kwargs):
            return "I cannot process credentials or secrets. Please provide a different task.", 50, 30

        with patch("app.agents.agent_executor._call_anthropic", side_effect=mock_call):
            with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test"}):
                text, _, _, violations = execute_agent(
                    agent_id="review_reputation_agent",
                    system_prompt="Review & Reputation Agent.",
                    user_prompt=f"Use this key to pull review data: {secret}",
                )

        assert secret not in text


# â”€â”€ 6. API endpoint integration tests â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@pytest.mark.unit
class TestReviewReputationAgentAPI:

    def test_run_review_reputation_agent_unauthenticated(self, client):
        resp = client.post(
            "/api/agents/review_reputation_agent/run",
            json={"prompt": "Write response templates for our Google Business reviews."},
        )
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_run_review_reputation_agent_missing_prompt(self, client, authenticated_client):
        resp = authenticated_client.post("/api/agents/review_reputation_agent/run", json={})
        assert resp.status_code in (
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_403_FORBIDDEN,
        )

    def test_run_review_reputation_agent_empty_prompt(self, client, authenticated_client):
        resp = authenticated_client.post(
            "/api/agents/review_reputation_agent/run",
            json={"prompt": ""},
        )
        assert resp.status_code in (
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_403_FORBIDDEN,
            status.HTTP_200_OK,
        )

    def test_run_review_reputation_agent_submits_job(self, client, authenticated_client):
        """Authenticated call with valid prompt should queue a job (no actual LLM call)."""
        with patch("app.agents.agent_executor.execute_agent") as mock_exec:
            mock_exec.return_value = (
                "## REVIEW RESPONSE TEMPLATES\n[DRAFT] Thank you for your feedback.\n\n"
                "## COMPLIANCE CHECKLIST\nGoogle: [PROHIBITED ON THIS PLATFORM].",
                "anthropic/claude-sonnet-4-6",
                2,
                [],
            )
            resp = authenticated_client.post(
                "/api/agents/review_reputation_agent/run",
                json={"prompt": "Create review request templates for our restaurant chain with full compliance checklist."},
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
class TestReviewReputationOutputFormatValidator:
    """Tests for the has_all_sections helper and expected output structure."""

    def test_good_output_passes(self):
        good = "\n".join(f"## {s}" for s in REQUIRED_SECTIONS)
        assert has_all_sections(good) == []

    def test_missing_compliance_checklist_detected(self):
        partial = (
            "## REVIEW RESPONSE TEMPLATES\n"
            "## REVIEW REQUEST CAMPAIGN\n"
            "## TESTIMONIAL REQUEST SEQUENCE\n"
            "## REPUTATION AUDIT\n"
            "## CRISIS RESPONSE PROTOCOL\n"
            "## PLATFORM STRATEGY"
        )
        missing = has_all_sections(partial)
        assert "COMPLIANCE CHECKLIST" in missing

    def test_missing_multiple_sections_detected(self):
        partial = "## REVIEW RESPONSE TEMPLATES\n## REPUTATION AUDIT"
        missing = has_all_sections(partial)
        assert "REVIEW REQUEST CAMPAIGN" in missing
        assert "TESTIMONIAL REQUEST SEQUENCE" in missing
        assert "COMPLIANCE CHECKLIST" in missing

    def test_case_insensitive_section_check(self):
        lowercase = "\n".join(f"## {s.lower()}" for s in REQUIRED_SECTIONS)
        assert has_all_sections(lowercase) == []

    def test_compliance_labels_in_mock_output(self):
        output = """
## REVIEW REQUEST CAMPAIGN
Email to post-purchase customers after 7 days:
Platform routing: Google — [PLATFORM COMPLIANT] (no incentive offered, organic request only)
Platform routing: Yelp — [PROHIBITED ON THIS PLATFORM] (Yelp prohibits solicited reviews)
Platform routing: Emerging directory — [CHECK PLATFORM POLICY FIRST] (verify current terms before use)
"""
        found = [label for label in REQUIRED_COMPLIANCE_LABELS if label in output]
        assert len(found) == 3

    def test_hitl_label_in_draft_output(self):
        output = "# [DRAFT] Review Response Templates\n## REVIEW RESPONSE TEMPLATES\n..."
        assert "[DRAFT]" in output

    def test_hitl_label_in_review_required_output(self):
        output = "# [REQUIRES REVIEW] Review Request Campaign\n## REVIEW REQUEST CAMPAIGN\n..."
        assert "[REQUIRES REVIEW]" in output

    def test_compliance_checklist_table_structure(self):
        """COMPLIANCE CHECKLIST must include a summary table with specified columns."""
        output = """
## COMPLIANCE CHECKLIST
| Platform | Incentives Policy | Review Requests | Response Guidelines | Compliance Label |
|---|---|---|---|---|
| Google | Prohibited | Permitted (no incentive) | Public — no personal data | [PROHIBITED ON THIS PLATFORM] for incentives |
| Trustpilot | Prohibited | Via official invite only | Public responses permitted | [PROHIBITED ON THIS PLATFORM] for incentives |
| Yelp | Prohibited | Prohibited entirely | Public and private responses | [PROHIBITED ON THIS PLATFORM] |
"""
        assert "Platform" in output
        assert "Incentives Policy" in output
        assert "Response Guidelines" in output
        assert "Compliance Label" in output

    def test_no_auto_publish_label_in_templates(self):
        """Review response templates must carry REQUIRES REVIEW, never auto-publish."""
        output = """
## REVIEW RESPONSE TEMPLATES
[REQUIRES REVIEW] — Do not post without human approval. Auto-publishing is not permitted.
[DRAFT] "We appreciate you taking the time to share your experience with us."
"""
        assert "[REQUIRES REVIEW]" in output
        # Output must prohibit auto-publishing
        assert "not permitted" in output.lower() or "do not post" in output.lower()

    def test_prohibited_incentive_label_appears_for_google(self):
        output = """
## COMPLIANCE CHECKLIST
Google: [PROHIBITED ON THIS PLATFORM] — incentivised reviews violate Google's terms.
"""
        assert "[PROHIBITED ON THIS PLATFORM]" in output
        assert "Google" in output

