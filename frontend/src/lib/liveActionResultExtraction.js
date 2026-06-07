const SENSITIVE_KEY_MARKERS = [
  "secret",
  "token",
  "api_key",
  "apikey",
  "password",
  "credential",
  "authorization",
  "bearer",
  "system_prompt",
  "internal_prompt",
  "raw_payload",
  "debug",
];

const WRAPPER_MESSAGES = new Set([
  "live provider execution response received",
  "execution response received",
  "governed live provider generation completed",
  "live execution completed",
]);

function isRecord(value) {
  return Boolean(value && typeof value === "object" && !Array.isArray(value));
}

function hasSensitiveKey(key) {
  const lowered = String(key || "").toLowerCase();
  return SENSITIVE_KEY_MARKERS.some((marker) => lowered.includes(marker));
}

function scrubSensitive(value) {
  if (Array.isArray(value)) {
    return value.map(scrubSensitive);
  }

  if (!isRecord(value)) {
    return value;
  }

  const safe = {};
  for (const [key, item] of Object.entries(value)) {
    if (hasSensitiveKey(key)) continue;
    safe[key] = scrubSensitive(item);
  }
  return safe;
}

function toText(value) {
  if (value === null || value === undefined) return "";

  if (typeof value === "string") {
    return value.trim();
  }

  if (typeof value === "number" || typeof value === "boolean") {
    return String(value);
  }

  if (Array.isArray(value)) {
    return value.map(toText).filter(Boolean).join("\n\n").trim();
  }

  if (isRecord(value)) {
    const direct =
      value.body ||
      value.generated_output ||
      value.output ||
      value.content ||
      value.text ||
      value.message ||
      value.summary ||
      "";

    if (direct && direct !== value) {
      const directText = toText(direct);
      if (directText) return directText;
    }

    return JSON.stringify(scrubSensitive(value), null, 2);
  }

  return "";
}

function getPath(root, path) {
  let cursor = root;
  for (const key of path) {
    if (!isRecord(cursor) && !Array.isArray(cursor)) return undefined;
    cursor = cursor?.[key];
  }
  return cursor;
}

function addUnique(records, value) {
  if (isRecord(value) && !records.includes(value)) {
    records.push(value);
  }
}

function envelopeRoots(payload) {
  const roots = [];
  addUnique(roots, payload);
  addUnique(roots, payload?.data);
  addUnique(roots, payload?.result);
  addUnique(roots, payload?.output);
  addUnique(roots, payload?.data?.result);
  addUnique(roots, payload?.data?.output);
  return roots;
}

function adapterRoots(payload) {
  const adapters = [];
  for (const root of envelopeRoots(payload)) {
    addUnique(adapters, root?.adapter_result);
    addUnique(adapters, root?.execution?.adapter_result);
    addUnique(adapters, root?.result?.execution?.adapter_result);
    addUnique(adapters, root?.output?.execution?.adapter_result);
  }
  return adapters;
}

function completedResultRoots(payload) {
  const roots = [];
  for (const root of envelopeRoots(payload)) {
    for (const key of ["completed_results", "queued_results", "blocked_results"]) {
      const items = Array.isArray(root?.[key]) ? root[key] : [];
      for (const item of items) addUnique(roots, item);
    }
  }
  return roots;
}

function customerSafeText(text) {
  return String(text || "")
    .split(/\r?\n/)
    .filter((line) => {
      const lowered = line.toLowerCase();
      return !SENSITIVE_KEY_MARKERS.some((marker) => lowered.includes(marker));
    })
    .join("\n")
    .trim();
}

export function extractLiveActionDeliverable(payload, options = {}) {
  const candidates = [];
  const adapters = adapterRoots(payload);

  for (const adapter of adapters) {
    candidates.push(["adapter_result.normalised_response.generated_output", adapter?.normalised_response?.generated_output]);
    candidates.push(["adapter_result.normalised_response.output", adapter?.normalised_response?.output]);
    candidates.push(["adapter_result.normalised_response.content", adapter?.normalised_response?.content]);
    candidates.push(["adapter_result.normalised_response.text", adapter?.normalised_response?.text]);
    candidates.push(["adapter_result.normalised_response.message", adapter?.normalised_response?.message]);
    candidates.push(["adapter_result.audit_asset.generated_output", adapter?.audit_asset?.generated_output]);
    candidates.push(["adapter_result.audit_asset.output", adapter?.audit_asset?.output]);
    candidates.push(["adapter_result.audit_asset.content", adapter?.audit_asset?.content]);
    candidates.push(["adapter_result.output", adapter?.output]);
    candidates.push(["adapter_result.result", adapter?.result]);
    candidates.push(["adapter_result.content", adapter?.content]);
    candidates.push(["adapter_result.deliverable", adapter?.deliverable]);
  }

  for (const root of envelopeRoots(payload)) {
    candidates.push(["generated_output", root?.generated_output]);
    candidates.push(["output", root?.output]);
    candidates.push(["outcome", root?.outcome]);
    candidates.push(["result", root?.result]);
    candidates.push(["content", root?.content]);
    candidates.push(["deliverable", root?.deliverable]);
  }

  for (const item of completedResultRoots(payload)) {
    candidates.push(["completed_results.completed_output", item?.completed_output]);
    candidates.push(["completed_results.deliverable.content.body", getPath(item, ["deliverable", "content", "body"])]);
    candidates.push(["completed_results.deliverable.output", getPath(item, ["deliverable", "output"])]);
    candidates.push(["completed_results.deliverable.generated_output", getPath(item, ["deliverable", "generated_output"])]);
    candidates.push(["completed_results.deliverable.summary", getPath(item, ["deliverable", "summary"])]);
  }

  const messages = [];
  for (const root of envelopeRoots(payload)) {
    messages.push(["message", root?.message]);
    messages.push(["summary", root?.summary]);
  }

  for (const [source, value] of [...candidates, ...messages]) {
    let text = toText(value);
    if (!text) continue;
    if (options.customerSafe) text = customerSafeText(text);
    if (!text) continue;

    const usedMessageFallback = source === "message" || source === "summary";
    const wrapperOnly = WRAPPER_MESSAGES.has(text.trim().toLowerCase());
    if (wrapperOnly && !usedMessageFallback) continue;

    return {
      text,
      source,
      usedMessageFallback,
      credential_values_exposed: false,
      customer_safe: true,
    };
  }

  return {
    text: "",
    source: "",
    usedMessageFallback: false,
    credential_values_exposed: false,
    customer_safe: true,
  };
}

export function extractLiveActionDeliverableText(payload, options = {}) {
  return extractLiveActionDeliverable(payload, options).text;
}
