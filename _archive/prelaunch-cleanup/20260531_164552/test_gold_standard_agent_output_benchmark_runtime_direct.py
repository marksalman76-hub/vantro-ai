from backend.app.runtime.gold_standard_agent_output_benchmark_runtime import (
    evaluate_output_against_gold_standard,
    generate_benchmark_improvement_plan,
    get_gold_standard_benchmark,
    gold_standard_agent_output_benchmark_status,
    score_output_against_gold_standard,
)

status = gold_standard_agent_output_benchmark_status()
assert status["gold_standard_benchmark_ready"] is True

bench = get_gold_standard_benchmark("seo_agent")
assert bench["agent_key"] == "seo_agent"
assert bench["benchmark_count"] >= 1

strong = score_output_against_gold_standard(
    agent_key="seo_agent",
    output_text="""Technical SEO: Fix crawl depth and metadata gaps.
Local SEO: Improve Google Business Profile and suburb landing pages.
Keywords: Prioritise commercial-intent keywords for service pages.
Priority actions: Start with indexation, internal links, and conversion pages.
Measurement: Track rankings, leads, and click-through rate.
Next step: implement the top three fixes this week.""",
    business_context={"business_name": "Urban Blend"},
    task_type="seo_strategy",
)
assert strong["benchmark_score"] >= 84
assert not strong["must_include_missing"]

weak = score_output_against_gold_standard(
    agent_key="seo_agent",
    output_text="Here are some generic SEO tips.",
    business_context={"business_name": "Urban Blend"},
    task_type="seo_strategy",
)
assert weak["benchmark_score"] < 84
assert weak["must_include_missing"]

plan = generate_benchmark_improvement_plan(agent_key="seo_agent", benchmark_score=weak)
assert plan["improvement_required"] is True
assert plan["instructions"]

evaluated = evaluate_output_against_gold_standard(
    agent_key="seo_agent",
    output_text="""Technical SEO: Fix crawl depth and metadata gaps.
Local SEO: Improve Google Business Profile and suburb landing pages.
Keywords: Prioritise commercial-intent keywords for service pages.
Priority actions: Start with indexation, internal links, and conversion pages.
Measurement: Track rankings, leads, and click-through rate.
Next step: implement the top three fixes this week.""",
    business_context={"business_name": "Urban Blend"},
    task_type="seo_strategy",
)
assert evaluated["status"] == "benchmark_evaluated"
assert evaluated["delivery_allowed_by_benchmark"] is True

print("GOLD_STANDARD_AGENT_OUTPUT_BENCHMARK_RUNTIME_DIRECT_TESTS_PASSED")
print("strong_score", strong["benchmark_score"], strong["benchmark_band"])
print("weak_score", weak["benchmark_score"], weak["benchmark_band"])
print("missing", weak["must_include_missing"])
print("delivery_allowed", evaluated["delivery_allowed_by_benchmark"])
