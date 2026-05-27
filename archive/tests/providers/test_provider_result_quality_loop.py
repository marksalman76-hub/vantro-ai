from backend.app.runtime.provider_result_quality_loop import (
    apply_quality_loop_to_provider_result,
    decide_retry_from_quality,
    readiness,
    score_provider_result,
)


def main():
    ready = readiness()

    strong = {
        "success": True,
        "provider_execution_attempted": True,
        "governance_preserved": True,
        "action_type": "marketing_campaign_execution",
        "output_text": (
            "Goal: increase ecommerce conversion using a clear offer and sharper positioning. "
            "Strategy: create three campaign angles for the target audience, each with a hook, "
            "customer pain point, benefit, CTA, and measurable KPI. Execution: launch creative testing, "
            "track analytics, review retention signals, and recommend next step based on performance. "
            "Risk: do not increase spend without approval."
        ),
    }

    weak = {
        "success": True,
        "provider_execution_attempted": True,
        "governance_preserved": True,
        "action_type": "marketing_campaign_execution",
        "output_text": "Generic placeholder campaign copy. Insert here.",
    }

    strong_score = score_provider_result(strong)
    weak_score = score_provider_result(weak)

    strong_loop = apply_quality_loop_to_provider_result(strong)
    weak_loop = apply_quality_loop_to_provider_result(weak)

    retry_decision = decide_retry_from_quality(weak_loop, retry_count=1, max_retries=3)
    manual_decision = decide_retry_from_quality(weak_loop, retry_count=3, max_retries=3)

    print("PROVIDER_RESULT_QUALITY_LOOP_TEST")
    print("readiness_status", ready["status"])
    print("strong_status", strong_score["status"])
    print("strong_score", strong_score["quality_score"])
    print("weak_status", weak_score["status"])
    print("weak_score", weak_score["quality_score"])
    print("weak_low_quality_hits", weak_score["low_quality_hits"])
    print("strong_finalisation", strong_loop["finalisation_status"])
    print("weak_finalisation", weak_loop["finalisation_status"])
    print("retry_decision", retry_decision["decision"])
    print("manual_decision", manual_decision["decision"])
    print("governance", weak_loop["governance_preserved"])

    assert ready["status"] == "provider_result_quality_loop_ready"
    assert strong_score["status"] == "passed_quality_gate"
    assert strong_score["quality_score"] >= 72
    assert weak_score["status"] == "failed_quality_gate"
    assert weak_score["quality_score"] < 72
    assert "placeholder" in weak_score["low_quality_hits"]
    assert strong_loop["quality_gate_passed"] is True
    assert weak_loop["quality_gate_passed"] is False
    assert weak_loop["finalisation_status"] == "requires_retry_or_review"
    assert retry_decision["decision"] == "retry"
    assert manual_decision["decision"] == "manual_review"
    assert weak_loop["governance_preserved"] is True

    print("PROVIDER_RESULT_QUALITY_LOOP_OK")


if __name__ == "__main__":
    main()
