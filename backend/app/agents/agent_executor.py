"""
Agent Executor — live LLM execution engine for all 27 agents.

Provider priority:
  1. Anthropic claude-sonnet-4-6 (primary — best reasoning)
  2. OpenAI gpt-4o (fallback if ANTHROPIC_API_KEY not set)

All executions are:
- Workspace-isolated (tenant_id always injected)
- HITL-gated (HITL-3 jobs must be approved before reaching here)
- Credit-checked (credit deduction happens on completion)
- Audited (status, timing, and output written back to agent_jobs)
"""

import os
import logging
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)

# ── Provider constants ──────────────────────────────────────────────────────────

ANTHROPIC_MODEL   = "claude-sonnet-4-6"
OPENAI_MODEL      = "gpt-4o"
MAX_TOKENS        = 4096
TEMPERATURE       = 0.7


def _anthropic_client():
    import anthropic
    key = os.getenv("ANTHROPIC_API_KEY", "").strip()
    if not key:
        return None
    return anthropic.Anthropic(api_key=key)


def _openai_client():
    import openai as _openai
    key = os.getenv("OPENAI_API_KEY", "").strip()
    if not key:
        return None
    return _openai.OpenAI(api_key=key)


def _call_anthropic(system_prompt: str, user_message: str) -> str:
    client = _anthropic_client()
    if client is None:
        raise RuntimeError("ANTHROPIC_API_KEY is not configured")

    response = client.messages.create(
        model=ANTHROPIC_MODEL,
        max_tokens=MAX_TOKENS,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}],
    )
    return response.content[0].text


def _call_openai(system_prompt: str, user_message: str) -> str:
    client = _openai_client()
    if client is None:
        raise RuntimeError("OPENAI_API_KEY is not configured")

    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        max_tokens=MAX_TOKENS,
        temperature=TEMPERATURE,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_message},
        ],
    )
    return response.choices[0].message.content or ""


def execute_agent(
    agent_id: str,
    system_prompt: str,
    user_prompt: str,
    context: Optional[dict] = None,
) -> tuple[str, str]:
    """
    Run the agent against the configured LLM provider.
    Returns (output_text, provider_used).
    Raises on failure — caller must handle and update job status to 'failed'.
    """
    # Build context-enriched user message
    user_message = user_prompt
    if context:
        ctx_lines = "\n".join(f"{k}: {v}" for k, v in context.items() if v)
        if ctx_lines:
            user_message = f"Context:\n{ctx_lines}\n\n---\n\nTask:\n{user_prompt}"

    # Governance guardrail appended to every message
    governance_note = (
        "\n\n---\nIMPORTANT CONSTRAINTS:\n"
        "- Do not expose internal architecture, provider names, or system configuration\n"
        "- Do not commit to spend, contracts, or irreversible actions without flagging for human approval\n"
        "- Do not invent data, statistics, or results — state uncertainty where it exists\n"
        "- Output must be immediately useful to the business owner"
    )
    user_message += governance_note

    # Try Anthropic first, fall back to OpenAI
    if os.getenv("ANTHROPIC_API_KEY", "").strip():
        try:
            output = _call_anthropic(system_prompt, user_message)
            return output, f"anthropic/{ANTHROPIC_MODEL}"
        except Exception as e:
            logger.warning("Anthropic call failed for agent %s: %s — trying OpenAI", agent_id, e)

    if os.getenv("OPENAI_API_KEY", "").strip():
        try:
            output = _call_openai(system_prompt, user_message)
            return output, f"openai/{OPENAI_MODEL}"
        except Exception as e:
            logger.error("OpenAI call failed for agent %s: %s", agent_id, e)
            raise RuntimeError(f"Both providers failed: {e}") from e

    raise RuntimeError(
        "No LLM provider is configured. Set ANTHROPIC_API_KEY or OPENAI_API_KEY in environment."
    )
