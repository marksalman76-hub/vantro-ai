from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass
class QualityGateResult:
    passed: bool
    score: int
    issues: List[str]
    recommendation: str


class PremiumQualityGate:
    def review_output(self, output: Dict[str, object]) -> QualityGateResult:
        text = str(output).lower()

        score = 100
        issues: List[str] = []

        premium_signals = [
            "premium",
            "execution",
            "strategy",
            "recommendation",
            "customer",
            "conversion",
            "commercial",
            "audience",
            "offer",
            "next step",
            "action",
            "campaign",
            "positioning",
            "pipeline",
            "growth",
            "optimisation",
            "performance",
            "follow-up",
            "deliverable",
            "implementation",
        ]

        signal_count = sum(1 for signal in premium_signals if signal in text)

        if signal_count < 3:
            score -= 10
            issues.append("Output needs stronger premium/commercial execution signals.")

        if len(text) < 180:
            score -= 10
            issues.append("Output is too short for premium client delivery.")

        blocked_internal_terms = [
            "tenant_id",
            "api_key",
            "secret",
            "password",
            "webhook",
            "stack trace",
            "traceback",
            "raw json",
            "system prompt",
        ]

        exposed_terms = [term for term in blocked_internal_terms if term in text]

        if exposed_terms:
            score -= 30
            issues.append("Output contains sensitive internal or credential-related wording.")

        passed = score >= 75 and not exposed_terms

        return QualityGateResult(
            passed=passed,
            score=max(0, min(score, 100)),
            issues=issues,
            recommendation="approved_for_client_delivery" if passed else "regenerate_or_human_review_required",
        )


def quality_summary(result: QualityGateResult) -> Dict[str, object]:
    return {
        "passed": result.passed,
        "score": result.score,
        "issues": result.issues,
        "recommendation": result.recommendation,
    }
