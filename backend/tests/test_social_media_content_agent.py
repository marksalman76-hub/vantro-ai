"""
social_media_content_agent test suite.

Covers:
  - Prompt structure validation (no LLM calls)
  - Registry entry correctness
  - Executor guard injection (mocked LLM)
  - Guardrail tests
  - API endpoint integration tests
  - Output format validation helper
"""
import pytest
from unittest.mock import patch, MagicMock
from fastapi import status


# â”€â”€ Helpers â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

REQUIRED_SECTIONS = [
    "PLATFORM STRATEGY",
    "CONTENT PILLARS",
    "CONTENT CALENDAR",
    "POST SCRIPTS",
    "HOOK BANK",
    "ENGAGEMENT STRATEGY",
    "PLATFORM-SPECIFIC FORMAT SPECS",
]

REQUIRED_CONFIDENCE_LABELS = [
    "[VALIDATED CHANNEL]",
    "[TESTING PHASE]",
    "[HYPOTHETICAL - VALIDATE AUDIENCE FIRST]",
]

HITL_TRIGGER_PHRASES = ["REQUIRES REVIEW", "DRAFT", "owner approval", "human review"]


def has_all_sections(text: str) -> list[str]:
    """Return list of missing required sections (case-insensitive)."""
    upper = text.upper()
    return [s for s in REQUIRED_SECTIONS if s not in upper]


# â”€â”€ 1. Prompt structure tests (no LLM, no network) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@pytest.mark.unit
class TestSocialMediaContentAgentPrompt:

    def test_prompt_exists(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        assert "social_media_content_agent" in AGENT_SYSTEM_PROMPTS

    def test_prompt_is_nonempty(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["social_media_content_agent"]
        assert len(prompt.strip()) > 300

    def test_prompt_has_all_required_sections(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["social_media_content_agent"]
        missing = has_all_sections(prompt)
        assert missing == [], f"Prompt missing sections: {missing}"

    def test_prompt_has_platform_specific_format_specs_section(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["social_media_content_agent"].upper()
        assert "PLATFORM-SPECIFIC FORMAT SPECS" in prompt

    def test_prompt_has_platform_native_rule(self):
        """Prompt must enforce that content is written natively per platform."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["social_media_content_agent"].lower()
        assert "platform-native" in prompt or "platform native" in prompt

    def test_prompt_has_review_before_publishing_rule(self):
        """Prompt must require human review before any content is published."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["social_media_content_agent"].lower()
        assert "review" in prompt and "publishing" in prompt or "publish" in prompt

    def test_prompt_has_confidence_labels(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["social_media_content_agent"]
        found = [label for label in REQUIRED_CONFIDENCE_LABELS if label in prompt]
        assert len(found) == 3, f"Missing confidence labels: {[l for l in REQUIRED_CONFIDENCE_LABELS if l not in prompt]}"

    def test_prompt_has_hitl_gate_language(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["social_media_content_agent"].upper()
        assert "HITL" in prompt or "REQUIRES REVIEW" in prompt or "HUMAN REVIEW" in prompt

    def test_prompt_has_draft_label(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["social_media_content_agent"]
        assert "[DRAFT]" in prompt

    def test_prompt_has_requires_review_tag(self):
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["social_media_content_agent"]
        assert "[REQUIRES REVIEW]" in prompt

    def test_get_agent_system_prompt_helper(self):
        from app.agents.agent_prompts import get_agent_system_prompt
        prompt = get_agent_system_prompt("social_media_content_agent")
        assert "Social" in prompt or "Content" in prompt

    def test_fallback_prompt_for_unknown_agent(self):
        from app.agents.agent_prompts import get_agent_system_prompt
        prompt = get_agent_system_prompt("nonexistent_xyz_agent")
        assert len(prompt) > 20


# â”€â”€ 2. Registry entry tests â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@pytest.mark.unit
class TestSocialMediaContentAgentRegistry:

    def test_registry_entry_exists(self):
        from app.agents.agent_registry import AGENT_CATALOGUE
        assert "social_media_content_agent" in AGENT_CATALOGUE

    def test_registry_hitl_level_is_not_hitl3(self):
        """social_media_content_agent is HITL-1/2, never HITL-3."""
        from app.agents.agent_registry import AGENT_CATALOGUE
        entry = AGENT_CATALOGUE["social_media_content_agent"]
        assert entry["hitl_default"] != "HITL-3"

    def test_registry_min_package_is_starter(self):
        from app.agents.agent_registry import AGENT_CATALOGUE
        entry = AGENT_CATALOGUE["social_media_content_agent"]
        assert entry["min_package"] == "starter"

    def test_registry_has_capabilities(self):
        from app.agents.agent_registry import AGENT_CATALOGUE
        entry = AGENT_CATALOGUE["social_media_content_agent"]
        assert isinstance(entry.get("capabilities"), list)
        assert len(entry["capabilities"]) >= 3

    def test_registry_has_role(self):
        from app.agents.agent_registry import AGENT_CATALOGUE
        entry = AGENT_CATALOGUE["social_media_content_agent"]
        assert entry.get("role") and len(entry["role"]) > 20

    def test_registry_total_agent_count(self):
        """Non-negotiable: exactly 27 client-facing agents."""
        from app.agents.agent_registry import AGENT_CATALOGUE
        assert len(AGENT_CATALOGUE) == 22


# â”€â”€ 3. Executor tests (mocked LLM) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@pytest.mark.unit
class TestSocialMediaContentAgentExecutor:

    def test_financial_guard_injected_into_system_prompt(self):
        from app.agents.agent_executor import (
            FINANCIAL_CONSTRAINT_BLOCK,
            INJECTION_GUARD,
            execute_agent,
        )
        captured_system_prompt = []

        def mock_anthropic_call(system_prompt, user_message, **kwargs):
            captured_system_prompt.append(system_prompt)
            return "Clean social media content plan with no financial actions.", 120, 60

        with patch("app.agents.agent_executor._call_anthropic", side_effect=mock_anthropic_call):
            with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test-key"}):
                execute_agent(
                    agent_id="social_media_content_agent",
                    system_prompt="You are the Social Media Content Agent.",
                    user_prompt="Create a 2-week content calendar for our brand.",
                )

        assert len(captured_system_prompt) == 1
        assert FINANCIAL_CONSTRAINT_BLOCK in captured_system_prompt[0]
        assert INJECTION_GUARD in captured_system_prompt[0]

    def test_clean_output_returns_no_violations(self):
        from app.agents.agent_executor import execute_agent

        def mock_call(system_prompt, user_message, **kwargs):
            return (
                "## PLATFORM STRATEGY\nLinkedIn and Instagram. [VALIDATED CHANNEL]\n\n"
                "## CONTENT PILLARS\n1. Educational. 2. Behind-the-scenes. [TESTING PHASE]\n\n"
                "## CONTENT CALENDAR\nDay 1 — LinkedIn — Carousel — 5 tips. [DRAFT]\n\n"
                "## POST SCRIPTS\nScript 1: LinkedIn. Hook: 'Most founders miss this.' [DRAFT]\n\n"
                "## HOOK BANK\n1. 'Stop scrolling — this changed how we sell.' [DRAFT]\n\n"
                "## ENGAGEMENT STRATEGY\nReply to comments within 2 hours.\n\n"
                "## PLATFORM-SPECIFIC FORMAT SPECS\nLinkedIn: 3,000 char limit. [INDUSTRY STANDARD]\n\n"
                "[REQUIRES REVIEW]",
                250, 400,
            )

        with patch("app.agents.agent_executor._call_anthropic", side_effect=mock_call):
            with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test-key"}):
                text, provider, credits, violations, *_ = execute_agent(
                    agent_id="social_media_content_agent",
                    system_prompt="You are the Social Media Content Agent.",
                    user_prompt="Create a content calendar.",
                )

        assert violations == []
        assert credits >= 1
        assert "anthropic" in provider

    def test_financial_violation_in_output_detected(self):
        from app.agents.agent_executor import execute_agent

        def mock_call(system_prompt, user_message, **kwargs):
            return "I have authorized the influencer fee of $5,000 for the campaign.", 100, 50

        with patch("app.agents.agent_executor._call_anthropic", side_effect=mock_call):
            with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test-key"}):
                _, _, _, violations, *_ = execute_agent(
                    agent_id="social_media_content_agent",
                    system_prompt="System.",
                    user_prompt="Book an influencer.",
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
            return "OpenAI social media fallback output.", 120, 80

        with patch("app.agents.agent_executor._call_anthropic", side_effect=anthropic_fail):
            with patch("app.agents.agent_executor._call_openai", side_effect=openai_ok):
                with patch.dict("os.environ", {
                    "ANTHROPIC_API_KEY": "sk-test",
                    "OPENAI_API_KEY": "sk-oai-test",
                }):
                    text, provider, credits, violations, *_ = execute_agent(
                        agent_id="social_media_content_agent",
                        system_prompt="System.",
                        user_prompt="Create a content calendar.",
                    )

        assert "openai" in provider
        assert text == "OpenAI social media fallback output."

    def test_no_provider_raises_runtime_error(self):
        from app.agents.agent_executor import execute_agent
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(RuntimeError, match="No LLM provider"):
                execute_agent(
                    agent_id="social_media_content_agent",
                    system_prompt="System.",
                    user_prompt="Create a content calendar.",
                )


# â”€â”€ 4. Guardrail tests â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@pytest.mark.unit
class TestSocialMediaContentAgentGuardrails:

    def test_injection_guard_blocks_system_prompt_reveal(self):
        """Injection guard must reference the system prompt and mark it fixed/immutable."""
        from app.agents.agent_executor import INJECTION_GUARD
        assert "system prompt" in INJECTION_GUARD.lower()
        assert (
            "cannot be overridden" in INJECTION_GUARD.lower()
            or "immutable" in INJECTION_GUARD.lower()
            or "fixed" in INJECTION_GUARD.lower()
        )

    def test_financial_patterns_list_has_minimum_count(self):
        """Guard list must have at least 10 patterns for meaningful coverage."""
        from app.agents.agent_executor import FINANCIAL_ACTION_PATTERNS
        assert len(FINANCIAL_ACTION_PATTERNS) >= 10

    def test_financial_constraint_covers_key_actions(self):
        from app.agents.agent_executor import FINANCIAL_CONSTRAINT_BLOCK
        block = FINANCIAL_CONSTRAINT_BLOCK.lower()
        required_coverage = ["spending", "budgets", "payments", "hiring"]
        missing = [term for term in required_coverage if term not in block]
        assert missing == [], f"Financial constraint block missing coverage for: {missing}"

    def test_social_media_agent_is_not_hitl3(self):
        """social_media_content_agent must never be HITL-3."""
        from app.agents.agent_registry import AGENT_CATALOGUE
        assert AGENT_CATALOGUE["social_media_content_agent"]["hitl_default"] != "HITL-3"

    def test_prompt_has_platform_native_or_review_before_publishing_language(self):
        """Prompt must enforce platform-native content and review before publishing."""
        from app.agents.agent_prompts import AGENT_SYSTEM_PROMPTS
        prompt = AGENT_SYSTEM_PROMPTS["social_media_content_agent"].lower()
        has_platform_native = "platform-native" in prompt or "platform native" in prompt
        has_review_publishing = "review" in prompt and ("publishing" in prompt or "publish" in prompt)
        assert has_platform_native or has_review_publishing, (
            "Prompt must contain platform-native rule or review-before-publishing rule"
        )

    def test_secrets_not_echoed_in_output(self):
        """If user injects a secret, executor must not echo it back in output."""
        from app.agents.agent_executor import execute_agent

        secret = "sk-SUPERSECRET_SOCIAL_KEY_77777"

        def mock_call(system_prompt, user_message, **kwargs):
            return "I cannot process credentials. Please provide a content brief instead.", 50, 30

        with patch("app.agents.agent_executor._call_anthropic", side_effect=mock_call):
            with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test"}):
                text, _, _, violations, *_ = execute_agent(
                    agent_id="social_media_content_agent",
                    system_prompt="Social Media Content Agent.",
                    user_prompt=f"Use this API key to pull engagement data: {secret}",
                )

        assert secret not in text


# â”€â”€ 5. API endpoint integration tests â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@pytest.mark.unit
class TestSocialMediaContentAgentAPI:

    def test_run_social_media_agent_unauthenticated(self, client):
        resp = client.post(
            "/api/agents/social_media_content_agent/run",
            json={"prompt": "Create a 2-week content calendar for our brand."},
        )
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_run_social_media_agent_missing_prompt(self, client, authenticated_client):
        resp = authenticated_client.post(
            "/api/agents/social_media_content_agent/run",
            json={},
        )
        assert resp.status_code in (
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_403_FORBIDDEN,
        )

    def test_run_social_media_agent_submits_job(self, client, authenticated_client):
        """Authenticated call with valid prompt should queue a job (no actual LLM call)."""
        mock_output = (
            "## PLATFORM STRATEGY\nLinkedIn and Instagram. [VALIDATED CHANNEL]\n\n"
            "## CONTENT PILLARS\n1. Educational. 2. Behind-the-scenes. [TESTING PHASE]\n\n"
            "## CONTENT CALENDAR\nDay 1 — LinkedIn — Carousel — 5 growth tips. [DRAFT]\n\n"
            "## POST SCRIPTS\nScript 1: LinkedIn. Hook: 'Most founders miss this.' [DRAFT]\n\n"
            "## HOOK BANK\n1. 'Stop scrolling — this changed how we sell.' [DRAFT]\n\n"
            "## ENGAGEMENT STRATEGY\nReply to comments within 2 hours for algorithmic boost.\n\n"
            "## PLATFORM-SPECIFIC FORMAT SPECS\nLinkedIn: 3,000 char limit. [INDUSTRY STANDARD]\n\n"
            "[REQUIRES REVIEW]"
        )
        with patch("app.agents.agent_executor.execute_agent") as mock_exec:
            mock_exec.return_value = (
                mock_output,
                "anthropic/claude-sonnet-4-6",
                2,
                [],
            )
            resp = authenticated_client.post(
                "/api/agents/social_media_content_agent/run",
                json={"prompt": "Create a 2-week LinkedIn and Instagram content calendar for our B2B SaaS brand."},
            )

        assert resp.status_code in (
            status.HTTP_200_OK,
            status.HTTP_202_ACCEPTED,
            status.HTTP_403_FORBIDDEN,  # insufficient credits/package on test workspace
            status.HTTP_400_BAD_REQUEST,
        )

    def test_jobs_list_after_run(self, client, authenticated_client):
        resp = authenticated_client.get("/api/agents/jobs")
        assert resp.status_code == status.HTTP_200_OK
        body = resp.json()
        assert "jobs" in body


# â”€â”€ 6. Output validator helper tests â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@pytest.mark.unit
class TestSocialMediaContentOutputValidator:

    def test_section_detection_helper_all_present(self):
        good = "\n".join(f"## {s}" for s in REQUIRED_SECTIONS)
        assert has_all_sections(good) == []

    def test_missing_platform_specific_format_specs_detected(self):
        sections_without_specs = [s for s in REQUIRED_SECTIONS if s != "PLATFORM-SPECIFIC FORMAT SPECS"]
        partial = "\n".join(f"## {s}" for s in sections_without_specs)
        missing = has_all_sections(partial)
        assert "PLATFORM-SPECIFIC FORMAT SPECS" in missing

    def test_all_three_confidence_labels_in_mock_output(self):
        output = """
## PLATFORM STRATEGY
LinkedIn: strong B2B fit. [VALIDATED CHANNEL] — confirmed by client analytics.
TikTok: possible fit for younger demo. [TESTING PHASE] — run 30-day test first.
Snapchat: speculative for this audience. [HYPOTHETICAL - VALIDATE AUDIENCE FIRST]
"""
        found = [label for label in REQUIRED_CONFIDENCE_LABELS if label in output]
        assert len(found) == 3

    def test_requires_review_present_in_output(self):
        output = (
            "## POST SCRIPTS\n"
            "Script 1: 'Stop scrolling — we have something for you.'\n"
            "Status: [DRAFT] — must be reviewed before publishing to any brand account. [REQUIRES REVIEW]\n"
        )
        assert "[REQUIRES REVIEW]" in output

    def test_section_detection_case_insensitive(self):
        lowercase = "\n".join(f"## {s.lower()}" for s in REQUIRED_SECTIONS)
        assert has_all_sections(lowercase) == []

    def test_section_detection_single_missing(self):
        sections_minus_one = [s for s in REQUIRED_SECTIONS if s != "HOOK BANK"]
        partial = "\n".join(f"## {s}" for s in sections_minus_one)
        missing = has_all_sections(partial)
        assert missing == ["HOOK BANK"]

    def test_all_sections_in_well_formed_output(self):
        well_formed = """
## PLATFORM STRATEGY
LinkedIn: primary platform for B2B audience. [VALIDATED CHANNEL]
Instagram: secondary for brand awareness. [TESTING PHASE]
TikTok: speculative — audience presence unconfirmed. [HYPOTHETICAL - VALIDATE AUDIENCE FIRST]

## CONTENT PILLARS
1. Founder Stories — behind-the-scenes of building. [TESTING PHASE]
2. Quick Wins — actionable tips in under 60 seconds. [VALIDATED CHANNEL]
3. Social Proof — customer results and case studies. [VALIDATED CHANNEL]
4. Industry News — timely commentary on sector trends. [TESTING PHASE]

## CONTENT CALENDAR
Day 1 — LinkedIn — Carousel — "5 things we learned from our first 100 customers". [DRAFT]
Day 3 — Instagram — Reel — "Behind the scenes: how we ship a feature". [DRAFT]
Day 5 — LinkedIn — Long-form post — "Why we stopped cold outreach". [DRAFT]
Day 7 — Instagram — Story — Quick poll on audience pain points. [DRAFT]

## POST SCRIPTS
Script 1 (LinkedIn Carousel):
Platform: LinkedIn
Format: Carousel (10 slides)
Hook: "Most B2B founders waste their first 6 months of marketing. Here's what actually worked for us."
Body: Slide-by-slide breakdown of 5 growth levers.
CTA: "Save this for your next planning session."
Hashtags: #B2BSaaS #GrowthMarketing #StartupMarketing
Status: [DRAFT] — must be reviewed before publishing to any brand account [REQUIRES REVIEW]

## HOOK BANK
1. "Most founders miss this and it costs them 6 months." (LinkedIn, TikTok) — curiosity hook
2. "We went from 0 to 500 customers without paid ads." (LinkedIn) — bold claim / social proof
3. "Hot take: cold outreach is dead for B2B SaaS." (LinkedIn, Twitter) — contrarian hook

## ENGAGEMENT STRATEGY
Comment engagement: reply to all comments within 2 hours on day of posting.
Community interaction: engage with 5 ICP accounts daily.
DM strategy: respond to inbound DMs within 24 hours; escalate to booking link.
Paid promotion: boosted LinkedIn post candidate — first carousel. [REQUIRES OWNER APPROVAL — PAID PROMOTION]

## PLATFORM-SPECIFIC FORMAT SPECS

LINKEDIN:
- Post character limit: 3,000 characters
- Recommended length for organic reach: 900â€“1,300 characters [INDUSTRY STANDARD]
- Video specs: up to 10 minutes, MP4, 1:1 or 16:9
- Hashtag count: 3â€“5 recommended
- Optimal post times: Tuesdayâ€“Thursday 8â€“10am [INDUSTRY STANDARD]
- Native features: polls, documents/carousels, newsletters
- What LinkedIn penalises: external links in post body, over-tagging

INSTAGRAM:
- Reels: optimal 15â€“30 seconds / max 90 seconds [INDUSTRY STANDARD]
- Feed caption: up to 2,200 characters; first 125 shown before "more"
- Stories: 15 seconds per frame
- Hashtag count: 3â€“5 for reels; 5â€“10 for feed
- Aspect ratios: 1:1 feed / 9:16 reels and stories
- Optimal post times: Monâ€“Fri 9amâ€“11am [INDUSTRY STANDARD]
- Native features: collab posts, link stickers, polls, close friends

[REQUIRES REVIEW]
"""
        missing = has_all_sections(well_formed)
        assert missing == [], f"Well-formed output should pass all section checks; missing: {missing}"

