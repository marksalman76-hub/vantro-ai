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

console.log("LIVE_ACTION_RESULT_EXTRACTION_CHECK_PASSED");
