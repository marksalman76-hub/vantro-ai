"""
Demo / Resale Readiness Runtime

Checks whether the ecommerce AI platform has the minimum foundations
required for demo, resale, and white-label readiness.
"""

from dataclasses import dataclass
from typing import Dict, List


REQUIRED_FOUNDATION_COMPONENTS = [
    "white_label_config",
    "tenant_manager",
    "agent_registry",
    "owner_approval_gateway",
    "premium_quality_gate",
    "ecommerce_workflow_engine",
]


@dataclass
class DemoReadinessResult:
    ready: bool
    score: int
    completed_components: List[str]
    missing_components: List[str]
    blockers: List[str]


class DemoReadinessRuntime:
    def check_readiness(self, available_components: List[str]) -> DemoReadinessResult:
        completed = [
            component
            for component in REQUIRED_FOUNDATION_COMPONENTS
            if component in available_components
        ]

        missing = [
            component
            for component in REQUIRED_FOUNDATION_COMPONENTS
            if component not in available_components
        ]

        score = int((len(completed) / len(REQUIRED_FOUNDATION_COMPONENTS)) * 100)

        blockers: List[str] = []

        if "owner_approval_gateway" not in completed:
            blockers.append("Owner approval gateway is required before resale/demo use.")

        if "white_label_config" not in completed:
            blockers.append("White-label configuration is required before resale/demo use.")

        if "premium_quality_gate" not in completed:
            blockers.append("Premium quality gate is required before client-facing demo use.")

        ready = score == 100 and not blockers

        return DemoReadinessResult(
            ready=ready,
            score=score,
            completed_components=completed,
            missing_components=missing,
            blockers=blockers,
        )


def readiness_summary(result: DemoReadinessResult) -> Dict[str, object]:
    return {
        "ready": result.ready,
        "score": result.score,
        "completed_components": result.completed_components,
        "missing_components": result.missing_components,
        "blockers": result.blockers,
    }