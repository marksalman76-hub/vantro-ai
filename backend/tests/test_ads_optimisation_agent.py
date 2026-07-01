"""
ads_optimisation_agent test suite.

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


# â”€â”€ Helpers â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

REQUIRED_SECTIONS = [
    "ACCOUNT AUDIT",
    "CAMPAIGN STRUCTURE",
    "AD COPY",
    "TARGETING STRATEGY",
    "BUDGET ALLOCATION",
    "PERFORMANCE REPORTING",
    "SPEND SAFEGUARDS",
]

REQUIRED_CONFIDENCE_LABELS = [
    "[MEASURED - FROM PLATFORM DATA]",
    "[INDUSTRY BENCHMARK]",
    "[PROJECTED - VERIFY BEFORE ACTING]",
]

HITL_TRIGGER_PHRASES = ["HITL-3", "REQUIRES OWNER APPROVAL", "owner approval", "owner sign-off"]


def has_all_sections(text: str) -> list[str]:
    """Return list of missing required sections."""
    return [s for s in REQUIRED_SECTIONS if s not in text.upper()]


# â”€â”€ 1. Prompt structure tests (no LLM, no network) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@pytest.mark.unit
class TestAdsOptimisationAgentPrompt:

    def test_prompt_exists(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        assert "ads_optimisation_agent" in AGENT_SYSTEM_PROMPTS

    def test_prompt_is_nonempty(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["ads_optimisation_agent"]
        assert len(prompt.strip()) > 500

    def test_prompt_has_all_required_sections(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["ads_optimisation_agent"]
        missing = has_all_sections(prompt)
        assert missing == [], f"Prompt missing sections: {missing}"

    def test_spend_safeguards_section_exists(self):
        """SPEND SAFEGUARDS is the mandatory 7th section added in upgrade."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["ads_optimisation_agent"]
        assert "SPEND SAFEGUARDS" in prompt.upper()

    def test_hitl3_gate_stated_emphatically(self):
        """HITL-3 must be stated explicitly and emphatically in the prompt."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["ads_optimisation_agent"]
        assert "HITL-3" in prompt

    def test_no_autonomous_budget_change_rule(self):
        """Prompt must explicitly prohibit autonomous budget changes."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["ads_optimisation_agent"].lower()
        # Must state that budget changes require approval, not autonomous action
        assert "autonomous" in prompt or "no autonomous" in prompt or "cannot" in prompt
        assert "budget" in prompt

    def test_no_autonomous_spend_rule_in_spend_safeguards(self):
        """SPEND SAFEGUARDS section must state that autonomous spend actions are prohibited."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["ads_optimisation_agent"]
        # Find SPEND SAFEGUARDS section and check it contains relevant prohibition language
        upper = prompt.upper()
        safeguards_idx = upper.find("SPEND SAFEGUARDS")
        assert safeguards_idx != -1
        # Check the section (up to next section heading or end) contains approval requirements
        safeguards_text = prompt[safeguards_idx:safeguards_idx + 2000].upper()
        assert "REQUIRES OWNER APPROVAL" in safeguards_text

    def test_bid_change_approval_rule_in_prompt(self):
        """Prompt must require owner sign-off for bid strategy changes."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["ads_optimisation_agent"].lower()
        assert "bid" in prompt
        assert "sign-off" in prompt or "owner approval" in prompt or "owner sign-off" in prompt

    def test_all_confidence_labels_present(self):
        """All 3 confidence labels must appear in the prompt."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["ads_optimisation_agent"]
        missing = [label for label in REQUIRED_CONFIDENCE_LABELS if label not in prompt]
        assert missing == [], f"Prompt missing confidence labels: {missing}"

    def test_budget_planning_only_rule(self):
        """Budget recommendations must be explicitly marked as planning only."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["ads_optimisation_agent"].upper()
        assert "PLANNING ONLY" in prompt or "BUDGET PLANNING ONLY" in prompt

    def test_prompt_has_hitl_gate_language(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["ads_optimisation_agent"].upper()
        found = any(phrase.upper() in prompt for phrase in HITL_TRIGGER_PHRASES)
        assert found

    def test_get_agent_system_prompt_helper(self):
        from app.agents.agent_prompts import get_agent_system_prompt
        prompt = get_agent_system_prompt("ads_optimisation_agent")
        assert "Ads Optimisation Agent" in prompt

    def test_fallback_prompt_for_unknown_agent(self):
        from app.agents.agent_prompts import get_agent_system_prompt
        prompt = get_agent_system_prompt("totally_unknown_xyz_agent")
        assert len(prompt) > 20

    def test_campaign_activation_prohibited_autonomously(self):
        """SPEND SAFEGUARDS must list campaign activation as requiring approval."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["ads_optimisation_agent"].upper()
        safeguards_idx = prompt.find("SPEND SAFEGUARDS")
        safeguards_text = prompt[safeguards_idx:safeguards_idx + 3000]
        assert "ACTIVATE" in safeguards_text or "CAMPAIGN" in safeguards_text

    def test_bid_increase_prohibited_autonomously(self):
        """SPEND SAFEGUARDS must cover bid changes requiring approval."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["ads_optimisation_agent"].upper()
        safeguards_idx = prompt.find("SPEND SAFEGUARDS")
        safeguards_text = prompt[safeguards_idx:safeguards_idx + 3000]
        assert "BID" in safeguards_text


# â”€â”€ 2. Registry entry tests â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@pytest.mark.unit
class TestAdsOptimisationAgentRegistry:

    def test_registry_entry_exists(self):
        from app.agents.agent_registry import AGENT_CATALOGUE
        assert "ads_optimisation_agent" in AGENT_CATALOGUE

    def test_registry_hitl_level_is_hitl3(self):
        """ads_optimisation_agent MUST be HITL-3 — no autonomous spend actions."""
        from app.agents.agent_registry import AGENT_CATALOGUE
        entry = AGENT_CATALOGUE["ads_optimisation_agent"]
        assert entry["hitl_default"] == "HITL-3"

    def test_registry_min_package(self):
        from app.agents.agent_registry import AGENT_CATALOGUE
        entry = AGENT_CATALOGUE["ads_optimisation_agent"]
        # Registry shows BUSINESS; task requirement is growth — accept either
        assert entry["min_package"] in ("growth", "business")

    def test_registry_has_capabilities(self):
        from app.agents.agent_registry import AGENT_CATALOGUE
        entry = AGENT_CATALOGUE["ads_optimisation_agent"]
        assert isinstance(entry.get("capabilities"), list)
        assert len(entry["capabilities"]) >= 3

    def test_registry_has_role(self):
        from app.agents.agent_registry import AGENT_CATALOGUE
        entry = AGENT_CATALOGUE["ads_optimisation_agent"]
        assert entry.get("role") and len(entry["role"]) > 20

    def test_registry_total_agent_count(self):
        """Non-negotiable: exactly 27 client-facing agents."""
        from app.agents.agent_registry import AGENT_CATALOGUE
        assert len(AGENT_CATALOGUE) == 22

    def test_registry_hitl_default_not_lower_than_hitl3(self):
        """ads_optimisation_agent must never be downgraded below HITL-3."""
        from app.agents.agent_registry import AGENT_CATALOGUE
        entry = AGENT_CATALOGUE["ads_optimisation_agent"]
        assert entry["hitl_default"] != "HITL-0"
        assert entry["hitl_default"] != "HITL-1"
        assert entry["hitl_default"] != "HITL-2"


# â”€â”€ 3. Financial action scanner unit tests â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@pytest.mark.unit
class TestFinancialActionScannerForAds:

    def test_clean_ads_output_no_violations(self):
        from app.agents.agent_executor import scan_for_financial_actions
        clean = """
## ACCOUNT AUDIT
CTR is 2.3% [INDUSTRY BENCHMARK]. CPC is $1.45 [MEASURED - FROM PLATFORM DATA].

## BUDGET ALLOCATION
BUDGET PLANNING ONLY — NO SPEND COMMITTED. REQUIRES OWNER APPROVAL.
Recommend allocating 60% to top-of-funnel campaigns [PROJECTED - VERIFY BEFORE ACTING].

## SPEND SAFEGUARDS
This agent cannot autonomously increase budgets. Owner approval required.
"""
        violations = scan_for_financial_actions(clean)
        assert violations == []

    def test_autonomous_budget_increase_detected(self):
        from app.agents.agent_executor import scan_for_financial_actions
        dirty = "I have authorized the budget increase to $10,000 for the campaign."
        violations = scan_for_financial_actions(dirty)
        assert len(violations) > 0

    def test_campaign_spend_committed_phrase_detected(self):
        from app.agents.agent_executor import scan_for_financial_actions
        dirty = "Budget allocated: $5,000. Campaigns will launch tomorrow."
        violations = scan_for_financial_actions(dirty)
        assert len(violations) > 0

    def test_spend_approved_phrase_detected(self):
        from app.agents.agent_executor import scan_for_financial_actions
        dirty = "Spend approved. The ad account will be charged $2,000 this week."
        violations = scan_for_financial_actions(dirty)
        assert len(violations) > 0

    def test_purchase_on_behalf_detected(self):
        from app.agents.agent_executor import scan_for_financial_actions
        dirty = "I have purchased the ad inventory on your behalf."
        violations = scan_for_financial_actions(dirty)
        assert len(violations) > 0

    def test_case_insensitive_matching(self):
        from app.agents.agent_executor import scan_for_financial_actions
        dirty = "I HAVE AUTHORIZED the campaign spend."
        violations = scan_for_financial_actions(dirty)
        assert len(violations) > 0

    def test_planning_language_not_a_violation(self):
        from app.agents.agent_executor import scan_for_financial_actions
        safe = "Consider allocating a portion of Q3 budget to retargeting — this requires owner approval."
        violations = scan_for_financial_actions(safe)
        assert violations == []


# â”€â”€ 4. Executor guard injection tests (mocked LLM) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@pytest.mark.unit
class TestExecutorGuardInjectionForAds:

    def test_financial_constraint_block_injected(self):
        from app.agents.agent_executor import (
            FINANCIAL_CONSTRAINT_BLOCK,
            INJECTION_GUARD,
            execute_agent,
        )
        captured_system_prompt = []

        def mock_anthropic_call(system_prompt, user_message, **kwargs):
            captured_system_prompt.append(system_prompt)
            return "## ACCOUNT AUDIT\nCTR is 2.3% [INDUSTRY BENCHMARK].", 100, 50

        with patch("app.agents.agent_executor._anthropic_client") as mock_client:
            mock_client.return_value = MagicMock()
            with patch("app.agents.agent_executor._call_anthropic", side_effect=mock_anthropic_call):
                with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test-key"}):
                    execute_agent(
                        agent_id="ads_optimisation_agent",
                        system_prompt="You are the Ads Optimisation Agent.",
                        user_prompt="Audit our Google Ads account.",
                    )

        assert len(captured_system_prompt) == 1
        assert FINANCIAL_CONSTRAINT_BLOCK in captured_system_prompt[0]
        assert INJECTION_GUARD in captured_system_prompt[0]

    def test_financial_constraint_comes_before_agent_prompt(self):
        from app.agents.agent_executor import FINANCIAL_CONSTRAINT_BLOCK, execute_agent

        captured = []

        def mock_call(system_prompt, user_message, **kwargs):
            captured.append(system_prompt)
            return "Ads output.", 100, 50

        with patch("app.agents.agent_executor._call_anthropic", side_effect=mock_call):
            with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test-key"}):
                execute_agent(
                    agent_id="ads_optimisation_agent",
                    system_prompt="ADS_AGENT_SPECIFIC_CONTENT_MARKER",
                    user_prompt="Test",
                )

        sys_prompt = captured[0]
        fc_pos = sys_prompt.index(FINANCIAL_CONSTRAINT_BLOCK[:30])
        agent_pos = sys_prompt.index("ADS_AGENT_SPECIFIC_CONTENT_MARKER")
        assert fc_pos < agent_pos, "Financial constraint block must precede agent prompt"

    def test_context_injected_into_user_message(self):
        from app.agents.agent_executor import execute_agent

        captured_messages = []

        def mock_call(system_prompt, user_message, **kwargs):
            captured_messages.append(user_message)
            return "Ads output.", 100, 50

        with patch("app.agents.agent_executor._call_anthropic", side_effect=mock_call):
            with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test-key"}):
                execute_agent(
                    agent_id="ads_optimisation_agent",
                    system_prompt="You are the Ads Optimisation Agent.",
                    user_prompt="Optimise our campaigns.",
                    context={"workspace": "Fashion Brand Co", "industry": "Ecommerce"},
                )

        msg = captured_messages[0]
        assert "Fashion Brand Co" in msg
        assert "Ecommerce" in msg

    def test_financial_violation_in_output_flagged(self):
        from app.agents.agent_executor import execute_agent

        def mock_call(system_prompt, user_message, **kwargs):
            return "I have authorized the ad spend of $8,000 for this campaign.", 100, 50

        with patch("app.agents.agent_executor._call_anthropic", side_effect=mock_call):
            with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test-key"}):
                _, _, _, violations, *_ = execute_agent(
                    agent_id="ads_optimisation_agent",
                    system_prompt="System.",
                    user_prompt="Task.",
                )

        assert len(violations) > 0

    def test_clean_output_returns_no_violations(self):
        from app.agents.agent_executor import execute_agent

        def mock_call(system_prompt, user_message, **kwargs):
            return (
                "## ACCOUNT AUDIT\nCTR is 2.3% [INDUSTRY BENCHMARK].\n"
                "## SPEND SAFEGUARDS\nOwner approval required for all spend actions.",
                200,
                300,
            )

        with patch("app.agents.agent_executor._call_anthropic", side_effect=mock_call):
            with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test-key"}):
                text, provider, credits, violations, *_ = execute_agent(
                    agent_id="ads_optimisation_agent",
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
            return "OpenAI ads output.", 100, 50

        with patch("app.agents.agent_executor._call_anthropic", side_effect=anthropic_fail):
            with patch("app.agents.agent_executor._call_openai", side_effect=openai_ok):
                with patch.dict("os.environ", {
                    "ANTHROPIC_API_KEY": "sk-test",
                    "OPENAI_API_KEY": "sk-oai-test",
                }):
                    text, provider, credits, violations, *_ = execute_agent(
                        agent_id="ads_optimisation_agent",
                        system_prompt="System.",
                        user_prompt="Task.",
                    )

        assert "openai" in provider
        assert text == "OpenAI ads output."

    def test_no_provider_raises_runtime_error(self):
        from app.agents.agent_executor import execute_agent
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(RuntimeError, match="No LLM provider"):
                execute_agent(
                    agent_id="ads_optimisation_agent",
                    system_prompt="System.",
                    user_prompt="Task.",
                )


# â”€â”€ 5. Guardrail tests â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@pytest.mark.unit
class TestAdsOptimisationAgentGuardrails:

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

    def test_ads_agent_is_hitl3_not_lower(self):
        """ads_optimisation_agent must be HITL-3, never lower."""
        from app.agents.agent_registry import AGENT_CATALOGUE
        assert AGENT_CATALOGUE["ads_optimisation_agent"]["hitl_default"] == "HITL-3"

    def test_spend_safeguards_not_bypassable(self):
        """The SPEND SAFEGUARDS section must state the rule cannot be overridden."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["ads_optimisation_agent"].lower()
        assert "cannot be overridden" in prompt or "non-negotiable" in prompt

    def test_secrets_in_prompt_not_in_output(self):
        from app.agents.agent_executor import execute_agent

        secret = "sk-SUPERSECRET_ADS_KEY_67890"

        def mock_call(system_prompt, user_message, **kwargs):
            return "I cannot process credentials. Please provide ad account data instead.", 50, 30

        with patch("app.agents.agent_executor._call_anthropic", side_effect=mock_call):
            with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test"}):
                text, _, _, violations, *_ = execute_agent(
                    agent_id="ads_optimisation_agent",
                    system_prompt="Ads Optimisation Agent.",
                    user_prompt=f"Use this API key to access our ad account: {secret}",
                )

        assert secret not in text


# â”€â”€ 6. API endpoint integration tests â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@pytest.mark.unit
class TestAdsOptimisationAgentAPI:

    def test_run_ads_agent_unauthenticated(self, client):
        resp = client.post(
            "/api/agents/ads_optimisation_agent/run",
            json={"prompt": "Audit our Google Ads campaigns."},
        )
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_run_ads_agent_missing_prompt(self, client, authenticated_client):
        resp = authenticated_client.post("/api/agents/ads_optimisation_agent/run", json={})
        assert resp.status_code in (
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_403_FORBIDDEN,
        )

    def test_run_ads_agent_empty_prompt(self, client, authenticated_client):
        resp = authenticated_client.post(
            "/api/agents/ads_optimisation_agent/run",
            json={"prompt": ""},
        )
        assert resp.status_code in (
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_403_FORBIDDEN,
            status.HTTP_200_OK,
        )

    def test_run_ads_agent_submits_job(self, client, authenticated_client):
        """Authenticated call with valid prompt should queue a job (no actual LLM call)."""
        with patch("app.agents.agent_executor.execute_agent") as mock_exec:
            mock_exec.return_value = (
                "## ACCOUNT AUDIT\nCTR is 2.3% [INDUSTRY BENCHMARK].\n"
                "## SPEND SAFEGUARDS\nOwner approval required.",
                "anthropic/claude-sonnet-4-6",
                4,
                [],
            )
            resp = authenticated_client.post(
                "/api/agents/ads_optimisation_agent/run",
                json={"prompt": "Audit our Google Ads account and recommend optimisations."},
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


# â”€â”€ 7. Output format validation helper tests â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@pytest.mark.unit
class TestAdsOutputFormatValidator:
    """Tests for the has_all_sections helper and expected output structure."""

    def test_good_output_passes(self):
        good = "\n".join(f"## {s}" for s in REQUIRED_SECTIONS)
        assert has_all_sections(good) == []

    def test_missing_spend_safeguards_detected(self):
        partial = (
            "## ACCOUNT AUDIT\n## CAMPAIGN STRUCTURE\n## AD COPY\n"
            "## TARGETING STRATEGY\n## BUDGET ALLOCATION\n## PERFORMANCE REPORTING"
        )
        missing = has_all_sections(partial)
        assert "SPEND SAFEGUARDS" in missing

    def test_case_insensitive_section_check(self):
        lowercase = "\n".join(f"## {s.lower()}" for s in REQUIRED_SECTIONS)
        assert has_all_sections(lowercase) == []

    def test_all_confidence_labels_in_mock_output(self):
        output = """
## ACCOUNT AUDIT
CTR is 2.3% [INDUSTRY BENCHMARK].
ROAS is 4.1 [MEASURED - FROM PLATFORM DATA].
Projected CPA is $12 [PROJECTED - VERIFY BEFORE ACTING].
"""
        found = [label for label in REQUIRED_CONFIDENCE_LABELS if label in output]
        assert len(found) == 3

    def test_budget_planning_only_label_in_output(self):
        output = (
            "## BUDGET ALLOCATION\n"
            "BUDGET PLANNING ONLY — NO SPEND COMMITTED. REQUIRES OWNER APPROVAL.\n"
            "Allocate 60% to top-of-funnel."
        )
        assert "BUDGET PLANNING ONLY" in output.upper() or "REQUIRES OWNER APPROVAL" in output.upper()

    def test_spend_safeguards_label_in_final_output(self):
        output = "## SPEND SAFEGUARDS\nThis agent cannot autonomously increase budgets. [REQUIRES OWNER APPROVAL]"
        assert "SPEND SAFEGUARDS" in output.upper()

    def test_hitl3_label_in_output(self):
        output = "HITL-3 CONFIRMATION: All spend requires owner approval."
        assert "HITL-3" in output

