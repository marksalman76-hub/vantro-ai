"use client";

import { useEffect, useMemo, useState } from "react";

type AgentOption = {
  key: string;
  name: string;
  category?: string;
  enterprise_only?: boolean;
};

type SelectionOptions = {
  status?: string;
  plan: string;
  max_selectable_agents: number;
  available_agents: AgentOption[];
  available_count: number;
  head_agent_available?: boolean;
};

type ValidationResult = {
  valid: boolean;
  selected_count: number;
  max_selectable_agents: number;
  invalid_agent_keys: string[];
  enterprise_blocked_agent_keys: string[];
  over_limit: boolean;
  activation_allowed: boolean;
};

const planOptions = ["starter", "growth", "business", "enterprise"];

function prettyPlan(plan: string) {
  return plan.charAt(0).toUpperCase() + plan.slice(1);
}

export default function SignupAgentSelectionBridge() {
  const [plan, setPlan] = useState("starter");
  const [options, setOptions] = useState<SelectionOptions | null>(null);
  const [selectedAgents, setSelectedAgents] = useState<string[]>([]);
  const [validation, setValidation] = useState<ValidationResult | null>(null);
  const [loading, setLoading] = useState(false);

  const selectedSet = useMemo(() => new Set(selectedAgents), [selectedAgents]);
  const max = options?.max_selectable_agents ?? 0;

  useEffect(() => {
    let active = true;

    async function loadOptions() {
      setLoading(true);
      setValidation(null);

      try {
        const response = await fetch(`/api/signup-agent-selection/options/${plan}`, {
          cache: "no-store",
        });
        const data = await response.json();

        if (!active) return;

        setOptions(data);
        setSelectedAgents((current) =>
          current.filter((key) => data.available_agents?.some((agent: AgentOption) => agent.key === key))
        );
      } catch {
        if (!active) return;
        setOptions(null);
      } finally {
        if (active) setLoading(false);
      }
    }

    loadOptions();

    return () => {
      active = false;
    };
  }, [plan]);

  useEffect(() => {
    let active = true;

    async function validateSelection() {
      try {
        const response = await fetch("/api/signup-agent-selection/validate", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          cache: "no-store",
          body: JSON.stringify({
            plan,
            selected_agent_keys: selectedAgents,
          }),
        });
        const data = await response.json();

        if (active) setValidation(data);
      } catch {
        if (active) setValidation(null);
      }
    }

    validateSelection();

    return () => {
      active = false;
    };
  }, [plan, selectedAgents]);

  function toggleAgent(agentKey: string) {
    setSelectedAgents((current) => {
      if (current.includes(agentKey)) {
        return current.filter((key) => key !== agentKey);
      }

      if (current.length >= max) {
        return current;
      }

      return [...current, agentKey];
    });
  }

  return (
    <section className="mt-8 rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-indigo-600">
            Agent selection
          </p>
          <h2 className="mt-1 text-xl font-semibold text-slate-950">
            Choose your active agents
          </h2>
          <p className="mt-1 max-w-2xl text-sm text-slate-600">
            Select the agents included in your package. Your full catalogue is installed securely,
            but only selected paid agents are activated in the client workspace.
          </p>
        </div>

        <label className="text-sm font-medium text-slate-700">
          Package
          <select
            value={plan}
            onChange={(event) => {
              setPlan(event.target.value);
              setSelectedAgents([]);
            }}
            className="mt-1 block rounded-2xl border border-slate-200 bg-white px-3 py-2 text-sm text-slate-900 shadow-sm outline-none focus:border-indigo-500"
          >
            {planOptions.map((item) => (
              <option key={item} value={item}>
                {prettyPlan(item)}
              </option>
            ))}
          </select>
        </label>
      </div>

      <div className="mt-4 flex flex-wrap gap-2 text-xs">
        <span className="rounded-full bg-slate-100 px-3 py-1 font-medium text-slate-700">
          {selectedAgents.length}/{max || 0} selected
        </span>
        <span className="rounded-full bg-slate-100 px-3 py-1 font-medium text-slate-700">
          {options?.available_count ?? 0} available
        </span>
        {options?.head_agent_available ? (
          <span className="rounded-full bg-indigo-50 px-3 py-1 font-medium text-indigo-700">
            Head Agent available
          </span>
        ) : (
          <span className="rounded-full bg-amber-50 px-3 py-1 font-medium text-amber-700">
            Head Agent reserved for Enterprise
          </span>
        )}
      </div>

      {loading ? (
        <div className="mt-5 rounded-2xl bg-slate-50 p-4 text-sm text-slate-600">
          Loading agent catalogue...
        </div>
      ) : null}

      {!loading && options?.available_agents?.length ? (
        <div className="mt-5 grid max-h-80 gap-2 overflow-y-auto pr-1 sm:grid-cols-2 lg:grid-cols-3">
          {options.available_agents.map((agent) => {
            const active = selectedSet.has(agent.key);
            const disabled = !active && selectedAgents.length >= max;

            return (
              <button
                key={agent.key}
                type="button"
                onClick={() => toggleAgent(agent.key)}
                disabled={disabled}
                className={[
                  "rounded-2xl border p-3 text-left transition",
                  active
                    ? "border-indigo-500 bg-indigo-50 shadow-sm"
                    : "border-slate-200 bg-white hover:border-slate-300 hover:bg-slate-50",
                  disabled ? "cursor-not-allowed opacity-50" : "",
                ].join(" ")}
              >
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <p className="text-sm font-semibold text-slate-950">{agent.name}</p>
                    <p className="mt-1 text-xs text-slate-500">
                      {(agent.category || "agent").replaceAll("_", " ")}
                    </p>
                  </div>
                  <span
                    className={[
                      "mt-1 h-3 w-3 rounded-full border",
                      active ? "border-indigo-600 bg-indigo-600" : "border-slate-300 bg-white",
                    ].join(" ")}
                  />
                </div>
              </button>
            );
          })}
        </div>
      ) : null}

      {validation ? (
        <div className="mt-4 rounded-2xl bg-slate-50 p-4 text-sm">
          {validation.activation_allowed ? (
            <p className="font-medium text-emerald-700">
              Selection valid. These agents can be activated after signup.
            </p>
          ) : (
            <p className="font-medium text-amber-700">
              Selection needs adjustment before activation.
            </p>
          )}

          {validation.over_limit ? (
            <p className="mt-1 text-slate-600">
              You selected more than the {validation.max_selectable_agents} agents allowed on this package.
            </p>
          ) : null}

          {validation.enterprise_blocked_agent_keys?.length ? (
            <p className="mt-1 text-slate-600">
              Enterprise-only agent selected: {validation.enterprise_blocked_agent_keys.join(", ")}
            </p>
          ) : null}
        </div>
      ) : null}
    </section>
  );
}
