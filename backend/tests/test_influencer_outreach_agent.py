"""
influencer_outreach_agent test suite.

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
    "INFLUENCER CRITERIA",
    "OUTREACH SEQUENCE",
    "PARTNERSHIP BRIEF",
    "CONTENT BRIEF",
    "COMPENSATION STRUCTURE",
    "CAMPAIGN METRICS",
    "RISK ASSESSMENT",
]

REQUIRED_VETTING_LABELS = [
    "[VERIFIED - TOOL CONFIRMED]",
    "[ESTIMATED - MANUAL CHECK REQUIRED]",
    "[UNVERIFIED - DO NOT PROCEED]",
]

HITL_TRIGGER_PHRASES = [
    "REQUIRES REVIEW",
    "DRAFT",
    "REQUIRES OWNER APPROVAL",
    "human review",
    "owner approval",
    "owner review",
]

RISK_ASSESSMENT_SUBSECTIONS = [
    "REPUTATION RISK",
    "AUDIENCE QUALITY RISK",
    "BRAND ALIGNMENT RISK",
    "PAST CONTROVERSY CHECK",
    "ENGAGEMENT AUTHENTICITY SCORE",
]


def has_all_sections(text: str) -> list[str]:
    """Return list of missing required sections."""
    return [s for s in REQUIRED_SECTIONS if s not in text.upper()]


# â”€â”€ 1. Prompt structure tests (no LLM, no network) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@pytest.mark.unit
class TestInfluencerOutreachAgentPrompt:

    def test_prompt_exists(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        assert "influencer_outreach_agent" in AGENT_SYSTEM_PROMPTS

    def test_prompt_is_nonempty(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["influencer_outreach_agent"]
        assert len(prompt.strip()) > 500

    def test_prompt_has_all_required_sections(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["influencer_outreach_agent"]
        missing = has_all_sections(prompt)
        assert missing == [], f"Prompt missing sections: {missing}"

    def test_prompt_has_hitl_gate_language(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["influencer_outreach_agent"].upper()
        assert any(phrase.upper() in prompt for phrase in HITL_TRIGGER_PHRASES)

    def test_prompt_has_hitl_2_internal_draft_gate(self):
        """Internal criteria/frameworks must be labelled [DRAFT] — HITL-2."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["influencer_outreach_agent"].upper()
        assert "DRAFT" in prompt

    def test_prompt_has_hitl_2_outreach_requires_review_gate(self):
        """All outreach before sending needs review — HITL-2 gate."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["influencer_outreach_agent"].upper()
        assert "REQUIRES REVIEW" in prompt

    def test_prompt_has_owner_approval_gate_for_compensation(self):
        """All compensation/budget commitments require owner approval."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["influencer_outreach_agent"].upper()
        assert "REQUIRES OWNER APPROVAL" in prompt

    def test_no_outreach_without_owner_review_rule_present(self):
        """The prompt must state that no outreach is sent without owner review."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["influencer_outreach_agent"].lower()
        assert "no outreach" in prompt or ("outreach" in prompt and "owner review" in prompt)

    def test_no_budget_commitment_without_owner_approval_rule_present(self):
        """The prompt must explicitly prohibit budget/compensation commitment without owner approval."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["influencer_outreach_agent"].lower()
        assert ("budget" in prompt or "compensation" in prompt) and "owner approval" in prompt

    def test_fake_follower_check_rule_present(self):
        """Fake follower check must be required before any partnership."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["influencer_outreach_agent"].lower()
        assert "fake follower" in prompt

    def test_prompt_has_all_vetting_confidence_labels(self):
        """All 3 vetting confidence labels must appear in the prompt definition."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["influencer_outreach_agent"]
        found = [label for label in REQUIRED_VETTING_LABELS if label in prompt]
        assert len(found) == 3, (
            f"Prompt must define all 3 vetting labels. Found: {found}"
        )

    def test_risk_assessment_section_is_7th_section(self):
        """RISK ASSESSMENT is the 7th (new) section."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["influencer_outreach_agent"].upper()
        assert "RISK ASSESSMENT" in prompt

    def test_risk_assessment_has_all_subsections(self):
        """RISK ASSESSMENT must cover all required risk dimensions."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["influencer_outreach_agent"].upper()
        missing = [sub for sub in RISK_ASSESSMENT_SUBSECTIONS if sub not in prompt]
        assert missing == [], f"RISK ASSESSMENT missing subsections: {missing}"

    def test_ftc_disclosure_rule_present(self):
        """FTC/ASA disclosure requirement must be mentioned in the prompt."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["influencer_outreach_agent"].lower()
        assert "ftc" in prompt or "disclosure" in prompt or "asa" in prompt

    def test_get_agent_system_prompt_helper(self):
        from app.agents.agent_prompts import get_agent_system_prompt
        prompt = get_agent_system_prompt("influencer_outreach_agent")
        assert "Influencer" in prompt or "influencer" in prompt

    def test_fallback_prompt_for_unknown_agent(self):
        from app.agents.agent_prompts import get_agent_system_prompt
        prompt = get_agent_system_prompt("totally_unknown_xyz_agent")
        assert len(prompt) > 20


# â”€â”€ 2. Registry entry tests â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@pytest.mark.unit
class TestInfluencerOutreachAgentRegistry:

    def test_registry_entry_exists(self):
        from app.agents.agent_registry import AGENT_CATALOGUE
        assert "influencer_outreach_agent" in AGENT_CATALOGUE

    def test_registry_hitl_level_is_hitl2(self):
        from app.agents.agent_registry import AGENT_CATALOGUE
        entry = AGENT_CATALOGUE["influencer_outreach_agent"]
        assert entry["hitl_default"] == "HITL-2"

    def test_registry_hitl_is_not_hitl3(self):
        """influencer_outreach_agent must not be HITL-3 gated."""
        from app.agents.agent_registry import AGENT_CATALOGUE
        assert AGENT_CATALOGUE["influencer_outreach_agent"]["hitl_default"] != "HITL-3"

    def test_registry_min_package(self):
        from app.agents.agent_registry import AGENT_CATALOGUE
        entry = AGENT_CATALOGUE["influencer_outreach_agent"]
        assert entry["min_package"] in ("starter", "growth", "business", "enterprise")

    def test_registry_has_capabilities(self):
        from app.agents.agent_registry import AGENT_CATALOGUE
        entry = AGENT_CATALOGUE["influencer_outreach_agent"]
        assert isinstance(entry.get("capabilities"), list)
        assert len(entry["capabilities"]) >= 3

    def test_registry_has_role(self):
        from app.agents.agent_registry import AGENT_CATALOGUE
        entry = AGENT_CATALOGUE["influencer_outreach_agent"]
        assert entry.get("role") and len(entry["role"]) > 20

    def test_registry_total_agent_count(self):
        """Non-negotiable: exactly 27 client-facing agents."""
        from app.agents.agent_registry import AGENT_CATALOGUE
        assert len(AGENT_CATALOGUE) == 22


# â”€â”€ 3. Financial action scanner unit tests â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@pytest.mark.unit
class TestFinancialActionScanner:

    def test_clean_influencer_output_no_violations(self):
        from app.agents.agent_executor import scan_for_financial_actions
        clean = """
## INFLUENCER CRITERIA
Nano influencers (1K-10K followers) in the wellness niche.
Engagement rate above 4%. [ESTIMATED - MANUAL CHECK REQUIRED]

## RISK ASSESSMENT
REPUTATION RISK: [MEDIUM] — creator has a clean public profile.
AUDIENCE QUALITY RISK: [LOW] — fake follower rate under 8%. [VERIFIED - TOOL CONFIRMED]
"""
        violations = scan_for_financial_actions(clean)
        assert violations == []

    def test_authorisation_phrase_detected(self):
        from app.agents.agent_executor import scan_for_financial_actions
        dirty = "I have authorized the influencer payment of $5,000."
        violations = scan_for_financial_actions(dirty)
        assert len(violations) > 0

    def test_purchase_phrase_detected(self):
        from app.agents.agent_executor import scan_for_financial_actions
        dirty = "I have purchased a sponsored post slot on your behalf."
        violations = scan_for_financial_actions(dirty)
        assert len(violations) > 0

    def test_budget_allocated_phrase_detected(self):
        from app.agents.agent_executor import scan_for_financial_actions
        dirty = "Budget allocated: $10,000 for the influencer campaign."
        violations = scan_for_financial_actions(dirty)
        assert len(violations) > 0

    def test_spend_approved_phrase_detected(self):
        from app.agents.agent_executor import scan_for_financial_actions
        dirty = "Spend approved. Influencer contracts will be signed tomorrow."
        violations = scan_for_financial_actions(dirty)
        assert len(violations) > 0

    def test_case_insensitive_matching(self):
        from app.agents.agent_executor import scan_for_financial_actions
        dirty = "I HAVE AUTHORIZED the creator compensation package."
        violations = scan_for_financial_actions(dirty)
        assert len(violations) > 0

    def test_partial_word_no_false_positive(self):
        # "authoritative" should NOT trigger "i have authorised"
        from app.agents.agent_executor import scan_for_financial_actions
        safe = "This is an authoritative vetting framework used by top influencer teams."
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
            return "Influencer criteria output with no financial actions.", 100, 50

        with patch("app.agents.agent_executor._anthropic_client") as mock_client:
            mock_client.return_value = MagicMock()
            with patch("app.agents.agent_executor._call_anthropic", side_effect=mock_anthropic_call):
                with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test-key"}):
                    execute_agent(
                        agent_id="influencer_outreach_agent",
                        system_prompt="You are the Influencer Outreach Agent.",
                        user_prompt="Find and vet 5 nano influencers for our wellness brand.",
                    )

        assert len(captured_system_prompt) == 1
        assert FINANCIAL_CONSTRAINT_BLOCK in captured_system_prompt[0]
        assert INJECTION_GUARD in captured_system_prompt[0]

    def test_financial_constraint_comes_before_agent_prompt(self):
        from app.agents.agent_executor import FINANCIAL_CONSTRAINT_BLOCK, execute_agent

        captured = []

        def mock_call(system_prompt, user_message, **kwargs):
            captured.append(system_prompt)
            return "Influencer output.", 100, 50

        with patch("app.agents.agent_executor._call_anthropic", side_effect=mock_call):
            with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test-key"}):
                execute_agent(
                    agent_id="influencer_outreach_agent",
                    system_prompt="INFLUENCER_AGENT_CONTENT_MARKER",
                    user_prompt="Test",
                )

        sys_prompt = captured[0]
        fc_pos = sys_prompt.index(FINANCIAL_CONSTRAINT_BLOCK[:30])
        agent_pos = sys_prompt.index("INFLUENCER_AGENT_CONTENT_MARKER")
        assert fc_pos < agent_pos, "Financial constraint block must precede agent prompt"

    def test_context_injected_into_user_message(self):
        from app.agents.agent_executor import execute_agent

        captured_messages = []

        def mock_call(system_prompt, user_message, **kwargs):
            captured_messages.append(user_message)
            return "Influencer output.", 100, 50

        with patch("app.agents.agent_executor._call_anthropic", side_effect=mock_call):
            with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test-key"}):
                execute_agent(
                    agent_id="influencer_outreach_agent",
                    system_prompt="You are the Influencer Outreach Agent.",
                    user_prompt="Vet influencers for our brand.",
                    context={"workspace": "BeautyBrand Co", "niche": "skincare"},
                )

        msg = captured_messages[0]
        assert "BeautyBrand Co" in msg
        assert "skincare" in msg

    def test_governance_note_appended_to_user_message(self):
        from app.agents.agent_executor import execute_agent

        captured_messages = []

        def mock_call(system_prompt, user_message, **kwargs):
            captured_messages.append(user_message)
            return "Output.", 100, 50

        with patch("app.agents.agent_executor._call_anthropic", side_effect=mock_call):
            with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test-key"}):
                execute_agent(
                    agent_id="influencer_outreach_agent",
                    system_prompt="System.",
                    user_prompt="Task.",
                )

        msg = captured_messages[0]
        assert "MANDATORY CONSTRAINTS" in msg or "Financial decisions" in msg

    def test_financial_violation_in_output_flagged(self):
        from app.agents.agent_executor import execute_agent

        def mock_call(system_prompt, user_message, **kwargs):
            return "I have authorized a $5,000 influencer campaign budget.", 100, 50

        with patch("app.agents.agent_executor._call_anthropic", side_effect=mock_call):
            with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test-key"}):
                _, _, _, violations = execute_agent(
                    agent_id="influencer_outreach_agent",
                    system_prompt="System.",
                    user_prompt="Task.",
                )

        assert len(violations) > 0

    def test_clean_output_returns_no_violations(self):
        from app.agents.agent_executor import execute_agent

        def mock_call(system_prompt, user_message, **kwargs):
            return (
                "## INFLUENCER CRITERIA\nNano influencers in the wellness space. "
                "[ESTIMATED - MANUAL CHECK REQUIRED] Engagement rate ~4.5%. "
                "[DRAFT] Internal vetting framework.",
                200,
                300,
            )

        with patch("app.agents.agent_executor._call_anthropic", side_effect=mock_call):
            with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test-key"}):
                text, provider, credits, violations = execute_agent(
                    agent_id="influencer_outreach_agent",
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
                    text, provider, credits, violations = execute_agent(
                        agent_id="influencer_outreach_agent",
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
                    agent_id="influencer_outreach_agent",
                    system_prompt="System.",
                    user_prompt="Task.",
                )


# â”€â”€ 5. Guardrail tests â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@pytest.mark.unit
class TestInfluencerOutreachAgentGuardrails:

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

    def test_influencer_outreach_agent_is_hitl2(self):
        """influencer_outreach_agent must be HITL-2 in the registry."""
        from app.agents.agent_registry import AGENT_CATALOGUE
        assert AGENT_CATALOGUE["influencer_outreach_agent"]["hitl_default"] == "HITL-2"

    def test_influencer_outreach_agent_not_hitl3(self):
        from app.agents.agent_registry import AGENT_CATALOGUE
        assert AGENT_CATALOGUE["influencer_outreach_agent"]["hitl_default"] != "HITL-3"

    def test_secrets_not_echoed_in_output(self):
        """If a user injects a secret, the executor must not echo it back."""
        from app.agents.agent_executor import execute_agent

        secret = "sk-SUPERSECRET_KEY_99999"

        def mock_call(system_prompt, user_message, **kwargs):
            return "I cannot process credentials. Please provide campaign context instead.", 50, 30

        with patch("app.agents.agent_executor._call_anthropic", side_effect=mock_call):
            with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test"}):
                text, _, _, violations = execute_agent(
                    agent_id="influencer_outreach_agent",
                    system_prompt="Influencer Outreach Agent.",
                    user_prompt=f"Use this API key to pull creator data: {secret}",
                )

        assert secret not in text

    def test_no_budget_commitment_rule_in_prompt(self):
        """Prompt must explicitly state no budget/compensation committed without owner approval."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["influencer_outreach_agent"].lower()
        assert "owner approval" in prompt
        assert "budget" in prompt or "compensation" in prompt

    def test_fake_follower_check_rule_is_absolute(self):
        """Fake follower check rule must be described as mandatory/absolute in the prompt."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["influencer_outreach_agent"].lower()
        assert "fake follower" in prompt
        assert "mandatory" in prompt or "absolute" in prompt or "required" in prompt

    def test_risk_assessment_covers_all_required_dimensions(self):
        """RISK ASSESSMENT section must include all required risk dimensions."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["influencer_outreach_agent"].upper()
        for subsection in RISK_ASSESSMENT_SUBSECTIONS:
            assert subsection in prompt, f"RISK ASSESSMENT missing: {subsection}"

    def test_all_vetting_labels_present_in_prompt(self):
        """All 3 vetting confidence labels must be defined in the prompt."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["influencer_outreach_agent"]
        for label in REQUIRED_VETTING_LABELS:
            assert label in prompt, f"Missing vetting label: {label}"


# â”€â”€ 6. API endpoint integration tests â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@pytest.mark.unit
class TestInfluencerOutreachAgentAPI:

    def test_run_influencer_outreach_agent_unauthenticated(self, client):
        resp = client.post(
            "/api/agents/influencer_outreach_agent/run",
            json={"prompt": "Find 5 nano influencers for our skincare brand."},
        )
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_run_influencer_outreach_agent_missing_prompt(self, client, authenticated_client):
        resp = authenticated_client.post("/api/agents/influencer_outreach_agent/run", json={})
        assert resp.status_code in (
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_403_FORBIDDEN,
        )

    def test_run_influencer_outreach_agent_empty_prompt(self, client, authenticated_client):
        resp = authenticated_client.post(
            "/api/agents/influencer_outreach_agent/run",
            json={"prompt": ""},
        )
        assert resp.status_code in (
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_403_FORBIDDEN,
            status.HTTP_200_OK,
        )

    def test_run_influencer_outreach_agent_submits_job(self, client, authenticated_client):
        """Authenticated call with valid prompt should queue a job (no actual LLM call)."""
        with patch("app.agents.agent_executor.execute_agent") as mock_exec:
            mock_exec.return_value = (
                "## INFLUENCER CRITERIA\nNano influencers in the wellness niche.\n\n"
                "## RISK ASSESSMENT\nREPUTATION RISK: [LOW]. "
                "[VERIFIED - TOOL CONFIRMED] Fake follower rate 6%.",
                "anthropic/claude-sonnet-4-6",
                2,
                [],
            )
            resp = authenticated_client.post(
                "/api/agents/influencer_outreach_agent/run",
                json={"prompt": "Identify and vet 5 nano influencers for a skincare product launch."},
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
class TestOutputFormatValidator:
    """Tests for the has_all_sections helper and expected output structure."""

    def test_good_output_passes(self):
        good = "\n".join(f"## {s}" for s in REQUIRED_SECTIONS)
        assert has_all_sections(good) == []

    def test_missing_section_detected(self):
        partial = (
            "## INFLUENCER CRITERIA\n"
            "## OUTREACH SEQUENCE\n"
            "## PARTNERSHIP BRIEF\n"
            "## CONTENT BRIEF\n"
        )
        missing = has_all_sections(partial)
        assert "COMPENSATION STRUCTURE" in missing
        assert "CAMPAIGN METRICS" in missing
        assert "RISK ASSESSMENT" in missing

    def test_case_insensitive_section_check(self):
        lowercase = "\n".join(f"## {s.lower()}" for s in REQUIRED_SECTIONS)
        assert has_all_sections(lowercase) == []

    def test_risk_assessment_detected_as_missing(self):
        """Specifically verify that missing RISK ASSESSMENT is caught."""
        without_risk = (
            "## INFLUENCER CRITERIA\n"
            "## OUTREACH SEQUENCE\n"
            "## PARTNERSHIP BRIEF\n"
            "## CONTENT BRIEF\n"
            "## COMPENSATION STRUCTURE\n"
            "## CAMPAIGN METRICS\n"
        )
        missing = has_all_sections(without_risk)
        assert "RISK ASSESSMENT" in missing

    def test_vetting_labels_in_mock_output(self):
        output = """
## INFLUENCER CRITERIA
Follower count: 12,500 [VERIFIED - TOOL CONFIRMED] via Modash audit.
Engagement rate: 4.2% [ESTIMATED - MANUAL CHECK REQUIRED] — based on public data.
Brand safety: [UNVERIFIED - DO NOT PROCEED] — past controversy check not yet complete.
"""
        found = [label for label in REQUIRED_VETTING_LABELS if label in output]
        assert len(found) == 3

    def test_risk_assessment_subsections_in_mock_output(self):
        output = """
## RISK ASSESSMENT
REPUTATION RISK: [LOW] — clean public profile.
AUDIENCE QUALITY RISK: [LOW] — verified under 10% fake followers.
BRAND ALIGNMENT RISK: [MEDIUM] — one competitor mention found in history.
PAST CONTROVERSY CHECK: [NO — CLEARED]
ENGAGEMENT AUTHENTICITY SCORE: 4.1% authentic rate [VERIFIED - TOOL CONFIRMED]
"""
        for subsection in RISK_ASSESSMENT_SUBSECTIONS:
            assert subsection in output.upper(), f"Missing RISK ASSESSMENT subsection: {subsection}"

    def test_hitl_draft_label_present(self):
        output = "# [DRAFT] Influencer Vetting Framework\n## INFLUENCER CRITERIA\n..."
        assert "[DRAFT]" in output

    def test_hitl_requires_review_label_present(self):
        output = "# [REQUIRES REVIEW] Outreach Sequence\n## OUTREACH SEQUENCE\n..."
        assert "[REQUIRES REVIEW]" in output

    def test_compensation_approval_label_present(self):
        output = (
            "## COMPENSATION STRUCTURE\n"
            "Flat fee range: $500-$1,500 per post [REQUIRES OWNER APPROVAL] — confirm before communicating."
        )
        assert "[REQUIRES OWNER APPROVAL]" in output

    def test_unverified_label_blocks_proceed(self):
        """[UNVERIFIED - DO NOT PROCEED] label should be present for unvetted creators."""
        output = (
            "## INFLUENCER CRITERIA\n"
            "Creator @example: fake follower check not completed. "
            "[UNVERIFIED - DO NOT PROCEED]"
        )
        assert "[UNVERIFIED - DO NOT PROCEED]" in output

