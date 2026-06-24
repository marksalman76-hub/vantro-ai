"""
Retrieves few-shot quality examples for a given agent.
Returns a formatted string to prepend to the agent's system prompt.
Never raises — failure is silent (returns None).
"""
from typing import Optional
from sqlalchemy.orm import Session


def get_few_shot_examples(
    db: Session,
    agent_id: str,
    max_examples: int = 2,
) -> Optional[str]:
    """
    Return formatted few-shot block for agent, or None if no examples exist.

    Strips to max 1200 chars per example to stay token-efficient.
    Never raises — any DB or import error returns None silently.
    """
    try:
        from app.models.agent_example import AgentExample

        examples = (
            db.query(AgentExample)
            .filter(
                AgentExample.agent_id == agent_id,
                AgentExample.is_active == True,  # noqa: E712
            )
            .order_by(AgentExample.created_at.desc())
            .limit(max_examples)
            .all()
        )

        if not examples:
            return None

        lines = [
            "## QUALITY REFERENCE EXAMPLES",
            "These examples show the standard of output expected. "
            "Match this quality level — do not copy content.\n",
        ]
        for i, ex in enumerate(examples, 1):
            task = ex.task_description[:300]
            output = ex.exemplary_output[:1200]
            lines.append(f"### Example {i}")
            lines.append(f"**Task:** {task}")
            lines.append(f"**Output:**\n{output}")
            if ex.quality_note:
                lines.append(f"**Why this is good:** {ex.quality_note}")
            lines.append("")

        return "\n".join(lines)

    except Exception:
        return None
