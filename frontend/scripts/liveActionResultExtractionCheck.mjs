import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { Buffer } from "node:buffer";

const helperPath = new URL("../src/lib/liveActionResultExtraction.js", import.meta.url);
const helperSource = await readFile(helperPath, "utf-8");
const helperModule = await import(`data:text/javascript;base64,${Buffer.from(helperSource).toString("base64")}`);

const sample = {
  success: true,
  message: "Live provider execution response received.",
  data: {
    execution: {
      adapter_result: {
        normalised_response: {
          generated_output: "Final live ad copy: Launch offer headline and three polished variations.",
          message: "Wrapper normalised message.",
        },
        audit_asset: {
          output: "Audit fallback output.",
        },
      },
    },
  },
};

const extracted = helperModule.extractLiveActionDeliverable(sample);

assert.equal(extracted.text, "Final live ad copy: Launch offer headline and three polished variations.");
assert.equal(extracted.source, "adapter_result.normalised_response.generated_output");
assert.equal(extracted.usedMessageFallback, false);
assert.equal(extracted.credential_values_exposed, false);

const queuedCreativeMediaJob = {
  success: true,
  message: "Live provider execution response received.",
  data: {
    execution: {
      adapter_result: {
        normalised_response: {
          output: {
            workflow_status: "queued",
            execution_status: "media_job_queued",
            media_job_id: "media_job_ugc_123",
            media_job_status: "queued",
            media_asset_count: 0,
            playable_asset_count: 0,
            agent_id: "ugc_creative_agent",
            customer_safe: true,
            debug_trace: "must not be shown",
            provider_token: "must_not_leak",
          },
        },
      },
    },
  },
};

const queued = helperModule.extractLiveActionDeliverable(queuedCreativeMediaJob);

assert.match(queued.text, /Creative media job queued/);
assert.match(queued.text, /Status: Queued/);
assert.match(queued.text, /Agent: Ugc Creative Agent/);
assert.match(queued.text, /Job ID: media_job_ugc_123/);
assert.match(queued.text, /Generated assets: 0/);
assert.match(queued.text, /Playable assets: 0/);
assert.match(queued.text, /Customer-safe: Yes/);
assert.doesNotMatch(queued.text, /[{}`"]/);
assert.doesNotMatch(queued.text, /workflow_status/);
assert.doesNotMatch(queued.text, /execution_status/);
assert.doesNotMatch(queued.text, /debug_trace/);
assert.doesNotMatch(queued.text, /provider_token/);
assert.doesNotMatch(queued.text, /must_not_leak/);

console.log("LIVE_ACTION_RESULT_EXTRACTION_CHECK_PASSED");
