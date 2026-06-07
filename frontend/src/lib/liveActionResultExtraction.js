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

function humanLabel(value, fallback = "") {
  const text = String(value || fallback).trim();
  if (!text) return fallback;
  return text
    .replace(/_/g, " ")
    .replace(/\s+/g, " ")
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function yesNo(value) {
  if (value === true) return "Yes";
  if (value === false) return "No";
  return "";
}

function firstPresent(record, keys) {
  for (const key of keys) {
    const value = record?.[key];
    if (value !== null && value !== undefined && String(value).trim() !== "") return value;
  }
  return "";
}

function safeLine(label, value) {
  const text = String(value ?? "").trim();
  if (!text) return "";
  return `${label}: ${text}`;
}

function hasAnyKey(record, keys) {
  return keys.some((key) => record?.[key] !== null && record?.[key] !== undefined && String(record?.[key]).trim() !== "");
}

function summarizeMediaJob(value) {
  const record = scrubSensitive(value);
  const jobId = firstPresent(record, ["media_job_id", "job_id", "provider_job_id", "execution_id"]);
  const status = firstPresent(record, ["media_job_status", "job_status", "workflow_status", "execution_status", "status"]);
  const agent = firstPresent(record, ["agent_id", "assigned_agent", "requested_agent", "agent"]);
  const generatedAssets = firstPresent(record, ["generated_asset_count", "media_asset_count", "asset_count", "assets_generated"]);
  const playableAssets = firstPresent(record, ["playable_asset_count", "playable_assets", "ready_asset_count"]);
  const customerSafe = yesNo(record.customer_safe);
  const lines = [
    "Creative media job queued",
    safeLine("Status", humanLabel(status, "Queued")),
    safeLine("Agent", humanLabel(agent)),
    safeLine("Job ID", jobId),
    safeLine("Generated assets", generatedAssets || "0"),
    safeLine("Playable assets", playableAssets || "0"),
    safeLine("Customer-safe", customerSafe || "Yes"),
    safeLine("Next step", "Run delegated workforce or wait for generated media assets."),
  ];
  return lines.filter(Boolean).join("\n");
}

function summarizeCompletedAction(value) {
  const record = scrubSensitive(value);
  const status = firstPresent(record, ["execution_status", "workflow_status", "status", "action_status"]);
  const agent = firstPresent(record, ["agent_id", "assigned_agent", "requested_agent", "agent"]);
  const actionType = firstPresent(record, ["action_type", "execution_action", "adapter", "target_system"]);
  const actionId = firstPresent(record, ["action_id", "external_action_id", "record_id", "execution_id"]);
  const performed = yesNo(
    record.performed_actual_action === true ||
      record.external_action_performed === true ||
      record.delegate_execution === "executed"
  );
  const historySaved = yesNo(record.history_persisted);
  const customerSafe = yesNo(record.customer_safe);
  const lines = [
    "Completed action evidence",
    safeLine("Status", humanLabel(status, "Completed")),
    safeLine("Agent", humanLabel(agent)),
    safeLine("Action", humanLabel(actionType)),
    safeLine("Action ID", actionId),
    safeLine("Performed actual action", performed || "Yes"),
    safeLine("Execution history saved", historySaved),
    safeLine("Customer-safe", customerSafe || "Yes"),
  ];
  return lines.filter(Boolean).join("\n");
}

function summarizeObject(value) {
  const record = scrubSensitive(value);

  if (
    hasAnyKey(record, ["media_job_id", "media_job_status", "media_asset_count", "playable_asset_count"]) ||
    String(record?.action_type || "").toLowerCase().includes("media")
  ) {
    return summarizeMediaJob(record);
  }

  if (
    record?.performed_actual_action === true ||
    record?.external_action_performed === true ||
    record?.delegate_execution === "executed" ||
    hasAnyKey(record, ["external_action_id", "external_action_record_count", "completed_output"])
  ) {
    return summarizeCompletedAction(record);
  }

  return "Live action result received. No customer-facing deliverable was attached yet.";
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

    return summarizeObject(value);
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
