"""
Premium Quality Gate

Rejects weak, generic, unsafe, non-commercial, or non-white-label-safe
agent outputs before they reach clients.
"""

from dataclasses import dataclass
from typing import Dict, List


BLOCKED_TERMS = [
    "as an ai",
    "i cannot",
    "placeholder",
    "lorem ipsum",
    "generic product",
    "insert here",
    "example only",
    "api key",
    "system prompt",
    "internal workflow",
    "backend route",
    "hidden scoring",
]

REQUIRED_COMMERCIAL_SIGNALS = [
    "benefit",
    "audience",
    "offer",
    "conversion",
]


@dataclass
class QualityGateResult:
    passed: bool
    score: int
    issues: List[str]
    recommendation: str


class PremiumQualityGate:
    def review_output(self, output: Dict[str, object]) -> QualityGateResult:
        issues: List[str] = []
        score = 100

        text = str(output).lower()

        for term in BLOCKED_TERMS:
            if term in text:
                issues.append(f"Blocked or low-quality term detected: {term}")
                score -= 25

        if len(text.strip()) < 120:
            issues.append("Output is too short to be considered premium commercial output.")
            score -= 25

        commercial_signal_count = sum(
            1 for signal in REQUIRED_COMMERCIAL_SIGNALS if signal in text
        )

        if commercial_signal_count < 2:
            issues.append("Output does not include enough commercial/conversion signals.")
            score -= 20

        if "tenant_id" in text and "client_safe" not in text:
            issues.append("Output may expose internal tenant information.")
            score -= 20

        score = max(score, 0)
        passed = score >= 75 and not issues

        if passed:
            recommendation = "approved_for_client_delivery"
        else:
            recommendation = "regenerate_or_human_review_required"

        return QualityGateResult(
            passed=passed,
            score=score,
            issues=issues,
            recommendation=recommendation,
        )


def quality_summary(result: QualityGateResult) -> Dict[str, object]:
    return {
        "passed": result.passed,
        "score": result.score,
        "issues": result.issues,
        "recommendation": result.recommendation,
    }