"use client";

import { useEffect, useState } from "react";

type Account = {
  tenant_id?: string;
  client_id?: string;
  package?: string;
  package_name?: string;
  status?: string;
  package_status?: string;
  active_agents?: string[];
  company_name?: string;
  contact_email?: string;
  credits_remaining?: number;
  credits_monthly?: number;
  credits_used?: number;
};

type ClientIntegration = {
  integration_key: string;
  name: string;
  providers: string[];
  used_by_agents: string[];
  recommended_auth: string;
  high_risk_actions: string[];
  connected: boolean;
  provider?: string;
  status: string;
  last_tested_at?: string;
  credential_hint?: string;
};


const DEFAULT_CLIENT_INTEGRATIONS: ClientIntegration[] = [
  {
    integration_key: "email",
    name: "Email",
    providers: ["Gmail", "Outlook", "IMAP/SMTP", "Brevo"],
    used_by_agents: ["Email Reply Agent", "Sales / Closer Agent", "Customer Support Agent"],
    recommended_auth: "OAuth or scoped provider API key",
    high_risk_actions: ["send email", "bulk send"],
    connected: false,
    status: "not_connected",
  },
  {
    integration_key: "crm",
    name: "CRM",
    providers: ["GoHighLevel", "HubSpot", "Salesforce", "Pipedrive", "Zoho"],
    used_by_agents: ["CRM AI Agent", "Sales / Closer Agent", "Lead Generator / Appointment Setter Agent"],
    recommended_auth: "OAuth or scoped API key",
    high_risk_actions: ["create contact", "update deal", "create opportunity"],
    connected: false,
    status: "not_connected",
  },
  {
    integration_key: "store",
    name: "Ecommerce Store",
    providers: ["Shopify", "WooCommerce", "BigCommerce", "Wix", "Squarespace"],
    used_by_agents: ["Ecommerce Agent", "Product Research Agent", "Product Copywriting Agent", "Analytics Optimisation Agent"],
    recommended_auth: "OAuth or private app token with least privilege",
    high_risk_actions: ["update product", "publish product", "change price"],
    connected: false,
    status: "not_connected",
  },
  {
    integration_key: "website",
    name: "Website / CMS",
    providers: ["WordPress", "Webflow", "Shopify CMS", "Wix", "Squarespace"],
    used_by_agents: ["Website / Landing Page / Apps Agent", "SEO Agent", "Brand Strategy Agent"],
    recommended_auth: "Scoped CMS token or collaborator access",
    high_risk_actions: ["publish page", "deploy site", "update DNS"],
    connected: false,
    status: "not_connected",
  },
  {
    integration_key: "calendar",
    name: "Calendar",
    providers: ["Google Calendar", "Outlook Calendar"],
    used_by_agents: ["Receptionist Agent", "Appointment Setter Agent", "Sales / Closer Agent"],
    recommended_auth: "OAuth calendar scope",
    high_risk_actions: ["book appointment", "cancel appointment"],
    connected: false,
    status: "not_connected",
  },
  {
    integration_key: "sms",
    name: "SMS / Phone",
    providers: ["ClickSend", "Twilio"],
    used_by_agents: ["Receptionist Agent", "Sales / Closer Agent", "Customer Support Agent"],
    recommended_auth: "Scoped provider API key",
    high_risk_actions: ["send SMS", "bulk SMS"],
    connected: false,
    status: "not_connected",
  },
  {
    integration_key: "social",
    name: "Social Media",
    providers: ["Meta", "Instagram", "TikTok", "LinkedIn", "Pinterest"],
    used_by_agents: ["Social Media Manager Agent", "UGC Creative Agent", "Influencer Collaboration Agent"],
    recommended_auth: "OAuth publishing/insights scopes",
    high_risk_actions: ["publish post", "send DM"],
    connected: false,
    status: "not_connected",
  },
  {
    integration_key: "ads",
    name: "Ad Accounts",
    providers: ["Meta Ads", "Google Ads", "TikTok Ads"],
    used_by_agents: ["Paid Ads Agent", "Analytics Optimisation Agent", "Marketing Specialist Agent"],
    recommended_auth: "OAuth ads scope with spending approval controls",
    high_risk_actions: ["launch campaign", "increase budget", "change bid strategy"],
    connected: false,
    status: "not_connected",
  },
  {
    integration_key: "analytics",
    name: "Analytics",
    providers: ["GA4", "Search Console", "Meta Pixel", "Shopify Analytics"],
    used_by_agents: ["Analytics Optimisation Agent", "SEO Agent", "Marketing Specialist Agent"],
    recommended_auth: "Read-only analytics scope where possible",
    high_risk_actions: [],
    connected: false,
    status: "not_connected",
  },
];

type DeliverableAsset = {
  url?: string;
  image_url?: string;
  src?: string;
  title?: string;
  name?: string;
  type?: string;
  mime_type?: string;
  size?: string;
  source?: string;
  created_at?: string;
};

type LiveDeliverable = {
  title?: string;
  summary?: string;
  created_at?: string;
  image_url?: string;
  asset_url?: string;
  preview_url?: string;
  download_url?: string;
  export_url?: string;
  assets?: DeliverableAsset[];
  images?: DeliverableAsset[];
  tags?: string[];
};


type ExecutionTimelineEvent = {
  event_id: string;
  created_at: string;
  agent_id: string;
  event_type: string;
  event_status: string;
  workflow_stage: string;
  action_type: string;
  execution_action?: string;
  approval_status?: string;
  execution_status?: string;
  quality_status?: string;
  title?: string;
  summary?: string;
};


const DEFAULT_AGENTS: string[] = [];
const BACKEND_API_BASE = process.env.NEXT_PUBLIC_BACKEND_URL || process.env.NEXT_PUBLIC_API_BASE_URL || "https://ecommerce-ai-agent-platform-1.onrender.com";

const AGENT_DISPLAY_NAMES: Record<string, string> = {
    product_research_agent: "Product Research Agent",
  competitor_intelligence_agent: "Competitor Intelligence Agent",
  brand_strategy_agent: "Brand Strategy Agent",
  store_builder_agent: "Store Builder Agent",
  website_landing_apps_agent: "Website / Landing Page Agent",
  product_copywriting_agent: "Product Copywriting Agent",
  ugc_creative_agent: "UGC Creative Agent",
  product_image_agent: "Product Image Agent",
  paid_ads_agent: "Paid Ads Agent",
  analytics_optimisation_agent: "Analytics Optimisation Agent",
  email_reply_agent: "Email Reply Agent",
  crm_ai_agent: "CRM AI Agent",
  seo_agent: "SEO Agent",
  social_media_manager_content_creator_agent: "Social Media Manager Agent",
  influencer_collaboration_agent: "Influencer Collaboration Agent",
  lead_generator_appointment_setter_agent: "Lead Generator / Appointment Setter Agent",
  sales_closer_agent: "Sales / Closer Agent",
  receptionist_agent: "Receptionist Agent",
  product_development_agent: "Product Development Agent",
  ecommerce_agent: "Ecommerce Agent",
  customer_support_agent: "Customer Support Agent",
    business_growth_partnerships_agent: "Business Growth & Partnerships Agent",
};

function getAgentDisplayName(agentId: string) {
  return AGENT_DISPLAY_NAMES[agentId] ||
    agentId
      .replace(/_/g, " ")
      .replace(/\b\w/g, (letter) => letter.toUpperCase());
}


export default function ClientPage() {
  const [account, setAccount] = useState<Account | null>(null);
  const [selectedAgents, setSelectedAgents] = useState<string[]>([]);
  const [showRejectModal, setShowRejectModal] = useState(false);
  const [feedbackText, setFeedbackText] = useState("");
  const [feedbackReason, setFeedbackReason] = useState("");
  const [reviewStatus, setReviewStatus] = useState<"pending" | "approved" | "rejected">("pending");
  const [reviewActionLoading, setReviewActionLoading] = useState(false);
  const [liveDeliverable, setLiveDeliverable] = useState<LiveDeliverable | null>(null);
  const [executionState, setExecutionState] = useState<"idle" | "running" | "completed" | "rejected">("idle");
  const [toastMessage, setToastMessage] = useState("");
  const [showDeliverableModal, setShowDeliverableModal] = useState(false);
  const [selectedAssetIndex, setSelectedAssetIndex] = useState(0);

  const [integrations, setIntegrations] = useState<ClientIntegration[]>([]);
  const [executionTimeline, setExecutionTimeline] = useState<ExecutionTimelineEvent[]>([]);
  const [timelineLoading, setTimelineLoading] = useState(false);
  const [integrationMessage, setIntegrationMessage] = useState("");


  const shellStyle = {
    maxWidth: "none",
    width: "100%",
    padding: "clamp(18px,2.4vw,34px) clamp(16px,2.6vw,34px) 60px",
    boxSizing: "border-box" as const,
  };

  const primaryGridStyle = {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit,minmax(min(100%,300px),1fr))",
    gap: 18,
    alignItems: "stretch",
    marginBottom: 16,
  };

  const secondaryGridStyle = {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit,minmax(min(100%,340px),1fr))",
    gap: 18,
    alignItems: "stretch",
  };

  const deliverableCardGridStyle = {
    marginTop: 18,
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit,minmax(min(100%,280px),1fr))",
    gap: 20,
    padding: 18,
    borderRadius: 20,
    border: "1px solid #e5eaf2",
    background: "#fff",
  };

  const modalContentGridStyle = {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit,minmax(min(100%,300px),1fr))",
    gap: 24,
    padding: "clamp(18px,2.4vw,28px)",
  };

  useEffect(() => {
    fetch("/api/client-me")
      .then((r) => r.json())
      .then((data) => {
        const accountData = data?.account || data;
        setAccount(accountData);

        const deployedAgents =
          accountData?.active_agents && Array.isArray(accountData.active_agents)
            ? accountData.active_agents
            : [];

        if (deployedAgents.length > 0) {
          setSelectedAgents(deployedAgents);
        }
      })
      .catch(() => {});

    fetch("/api/client-latest-deliverable", {
      method: "GET",
      credentials: "include",
    })
      .then((r) => r.json())
      .then((data) => {
        if (data?.success && data?.deliverable) {
          setLiveDeliverable(data.deliverable);
          setSelectedAssetIndex(0);
          setExecutionState("completed");
          setReviewStatus("pending");
        }
      })
      .catch(() => {});
  }, []);

  const creditsRemaining = account?.credits_remaining ?? 0;
  const accountPackage = account?.package_name || account?.package || "Active workspace";
  const accountStatus = account?.package_status || account?.status || "Active";
  const directMediaAssets: DeliverableAsset[] = [
    liveDeliverable?.image_url
      ? {
          url: liveDeliverable.image_url,
          title: "Primary generated asset",
          type: "image",
          source: "generated",
        }
      : null,
    liveDeliverable?.asset_url
      ? {
          url: liveDeliverable.asset_url,
          title: "Attached asset",
          type: "asset",
          source: "attached",
        }
      : null,
    liveDeliverable?.preview_url
      ? {
          url: liveDeliverable.preview_url,
          title: "Preview asset",
          type: "preview",
          source: "preview",
        }
      : null,
  ].filter(Boolean) as DeliverableAsset[];

  const attachedAssets = [
    ...directMediaAssets,
    ...(liveDeliverable?.assets || []),
    ...(liveDeliverable?.images || []),
  ].filter((asset, index, list) => {
    const assetUrl = asset?.url || asset?.image_url || asset?.src || "";
    if (!assetUrl) return Boolean(asset?.title || asset?.name);
    return list.findIndex((candidate) => {
      const candidateUrl = candidate?.url || candidate?.image_url || candidate?.src || "";
      return candidateUrl === assetUrl;
    }) === index;
  });

  const selectedAsset = attachedAssets[selectedAssetIndex] || attachedAssets[0] || null;
  const primaryAssetUrl =
    selectedAsset?.url ||
    selectedAsset?.image_url ||
    selectedAsset?.src ||
    "";
  const deliverableDownloadUrl =
    liveDeliverable?.download_url ||
    liveDeliverable?.export_url ||
    primaryAssetUrl ||
    "";

  useEffect(() => {
    loadExecutionTimeline();
  }, []);

  useEffect(() => {
    if (!toastMessage) return;

    const timer = window.setTimeout(() => {
      setToastMessage("");
    }, 3200);

    return () => window.clearTimeout(timer);
  }, [toastMessage]);

  async function recordClientReviewAction(action: "approved" | "rejected", feedback = "", reason = "") {
    setReviewActionLoading(true);

    try {
      const response = await fetch("/api/client-review-action", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        credentials: "include",
        body: JSON.stringify({
          action,
          feedback,
          reason,
          selected_agents: selectedAgents,
          reviewed_item: liveDeliverable?.title || "Latest client deliverable",
          source: "client_workspace",
        }),
      });

      if (!response.ok) {
        throw new Error("Review action failed");
      }

      const data = await response.json();

      if (!data?.success) {
        throw new Error("Review action was not accepted");
      }

      return true;
    } catch {
      setToastMessage("Review action could not be saved. Please try again.");
      return false;
    } finally {
      setReviewActionLoading(false);
    }
  }




  async function loadExecutionTimeline() {
    try {
      setTimelineLoading(true);

      const response = await fetch(
        `${BACKEND_API_BASE}/client/execution-events?tenant_id=client_manual_admin&project_id=live_readiness_matrix&limit=20`,
        {
          cache: "no-store",
          headers: {
            "x-tenant-id": "client_manual_admin",
            "x-actor-role": "customer",
          },
        }
      );

      const data = await response.json();

      if (data?.success && Array.isArray(data.events)) {
        setExecutionTimeline(data.events);
      }
    } catch {
      setExecutionTimeline([]);
    } finally {
      setTimelineLoading(false);
    }
  }

  async function loadIntegrations() {
    try {
      const response = await fetch(`${BACKEND_API_BASE}/client/integrations`, { cache: "no-store", headers: { "x-tenant-id": "client_demo_001", "x-actor-role": "customer" } });
      const data = await response.json();
      if (data?.success && Array.isArray(data.integrations)) {
        setIntegrations(data.integrations);
      }
    } catch {
      setIntegrations(DEFAULT_CLIENT_INTEGRATIONS); setIntegrationMessage("Connection centre loaded. Add credentials to activate live automation.");
    }
  }

  async function connectIntegration(integration: ClientIntegration) {
    const providerOptions = integration.providers?.join(", ") || integration.name;
    const provider =
      window.prompt(`Choose provider for ${integration.name}: ${providerOptions}`, integration.providers?.[0] || integration.name) ||
      "";
    if (!provider.trim()) return;

    const credential =
      window.prompt(`Paste scoped API key or OAuth token for ${provider}. Do not use raw passwords.`) ||
      "";
    if (!credential.trim()) return;

    const response = await fetch(`${BACKEND_API_BASE}/client/integrations/connect`, {
      method: "POST",
      headers: { "Content-Type": "application/json", "x-tenant-id": "client_demo_001", "x-actor-role": "customer" },
      body: JSON.stringify({
        integration_key: integration.integration_key,
        provider,
        credential,
        connection_mode: "scoped_api_key",
      }),
    });

    const data = await response.json();

    if (data?.success) {
      setIntegrationMessage(`${integration.name} connected with ${provider}. Test the connection next.`);
      setIntegrations((previous) =>
        (previous.length ? previous : DEFAULT_CLIENT_INTEGRATIONS).map((item) =>
          item.integration_key === integration.integration_key
            ? {
                ...item,
                connected: true,
                provider,
                status: "connected_pending_test",
                credential_hint: data.credential_hint || "stored credential",
              }
            : item
        )
      );
    } else {
      setIntegrationMessage(`Could not connect ${integration.name}.`);
    }

    await loadIntegrations();
  }

  async function testIntegration(integration: ClientIntegration) {
    const response = await fetch(`${BACKEND_API_BASE}/client/integrations/test`, {
      method: "POST",
      headers: { "Content-Type": "application/json", "x-tenant-id": "client_demo_001", "x-actor-role": "customer" },
      body: JSON.stringify({ integration_key: integration.integration_key }),
    });

    const data = await response.json();
    if (data?.success) {
      setIntegrationMessage(`${integration.name} test passed. Live automation ready.`);
      setIntegrations((previous) =>
        (previous.length ? previous : DEFAULT_CLIENT_INTEGRATIONS).map((item) =>
          item.integration_key === integration.integration_key
            ? { ...item, connected: true, status: "test_passed", last_tested_at: new Date().toISOString() }
            : item
        )
      );
    } else {
      setIntegrationMessage(`${integration.name} is not connected yet.`);
    }
    await loadIntegrations();
  }

  async function disconnectIntegration(integration: ClientIntegration) {
    const response = await fetch(`${BACKEND_API_BASE}/client/integrations/disconnect`, {
      method: "POST",
      headers: { "Content-Type": "application/json", "x-tenant-id": "client_demo_001", "x-actor-role": "customer" },
      body: JSON.stringify({ integration_key: integration.integration_key }),
    });

    const data = await response.json();
    if (data?.success) {
      setIntegrationMessage(`${integration.name} disconnected.`);
      setIntegrations((previous) =>
        (previous.length ? previous : DEFAULT_CLIENT_INTEGRATIONS).map((item) =>
          item.integration_key === integration.integration_key
            ? { ...item, connected: false, status: "disconnected", provider: undefined, credential_hint: undefined }
            : item
        )
      );
    } else {
      setIntegrationMessage(`Could not disconnect ${integration.name}.`);
    }
    await loadIntegrations();
  }

  const toggleAgent = (agent: string) => {
    setSelectedAgents((prev) =>
      prev.includes(agent) ? prev.filter((a) => a !== agent) : [...prev, agent]
    );
  };

  return (
    <main
      style={{
        minHeight: "100vh",
        background: "#f4f7fb",
        color: "#0f172a",
        fontFamily:
          'Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
      }}
    >
      <div style={shellStyle}>
        <header
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "flex-start",
            gap: 28,
            marginBottom: 24,
            flexWrap: "wrap",
          }}
        >
          <div>
            <div
              style={{
                color: "#2563eb",
                fontSize: 13,
                fontWeight: 900,
                letterSpacing: 1.4,
                textTransform: "uppercase",
                marginBottom: 10,
              }}
            >
              Client workspace
            </div>

            <h1
              style={{
                margin: 0,
                fontSize: "clamp(28px,3.3vw,40px)",
                lineHeight: 1.04,
                letterSpacing: -1.8,
                fontWeight: 850,
              }}
            >
              {account?.company_name || account?.contact_email || "Client Workspace"}
            </h1>

            <p
              style={{
                margin: "12px 0 0",
                maxWidth: 700,
                color: "#64748b",
                lineHeight: 1.55,
                fontSize: 13,
              }}
            >
              Run selected AI agents, generate governed outputs, manage
              execution workflows, and produce commercial-grade deliverables.
            </p>
          </div>

          <div style={{ display: "flex", alignItems: "center", gap: 10, flexWrap: "wrap", justifyContent: "flex-end" }}>
            <button
              style={{
                border: "none",
                borderRadius: 14,
                padding: "12px 16px",
                background: "#0f172a",
                color: "#fff",
                fontWeight: 800,
                cursor: "pointer",
                boxShadow: "0 10px 24px rgba(15,23,42,.12)",
              }}
            >
              + New execution
            </button>

            <div
              style={{
                background: "#fff",
                borderRadius: 999,
                padding: "12px 16px",
                border: "1px solid #e5eaf2",
                fontWeight: 800,
                boxShadow: "0 8px 22px rgba(15,23,42,.045)",
              }}
            >
              <span style={{ color: "#2563eb", marginRight: 8 }}>●</span>
              {accountStatus}
            </div>

            <button
              aria-label="Notifications"
              style={{
                width: 44,
                height: 44,
                borderRadius: 999,
                border: "1px solid #e5eaf2",
                background: "#fff",
                boxShadow: "0 8px 22px rgba(15,23,42,.045)",
                cursor: "pointer",
                position: "relative",
              }}
            >
              🔔
              <span
                style={{
                  position: "absolute",
                  top: 7,
                  right: 8,
                  width: 8,
                  height: 8,
                  borderRadius: 999,
                  background: "#2563eb",
                  border: "2px solid #fff",
                }}
              />
            </button>

            <div
              style={{
                width: 44,
                height: 44,
                borderRadius: 999,
                background: "#0f172a",
                color: "#fff",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontWeight: 900,
              }}
            >
              PD
            </div>
          </div>
        </header>

        <section
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit,minmax(220px,1fr))",
            gap: 12,
            alignItems: "stretch",
            marginBottom: 22,
          }}
        >
          {[
            ["Workspace status", "Ready for execution", accountPackage],
            ["Approvals", reviewStatus === "pending" && liveDeliverable ? "1 pending" : "0 pending", liveDeliverable ? "Client review" : "No pending review"],
            ["Workflows", liveDeliverable ? "1 tracked" : "0 tracked", liveDeliverable ? "Latest execution" : "No active workflow"],
            ["Credits", String(creditsRemaining), "Available balance"],
          ].map(([label, value, note]) => (
            <div
              key={label}
              style={{
                background: "rgba(255,255,255,.72)",
                border: "1px solid #edf1f6",
                borderRadius: 18,
                padding: "16px 18px",
                boxShadow: "0 8px 22px rgba(15,23,42,.035)",
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                gap: 18,
              }}
            >
              <div>
                <div
                  style={{
                    color: "#64748b",
                    fontSize: 11,
                    fontWeight: 800,
                    letterSpacing: .4,
                    textTransform: "uppercase",
                    marginBottom: 5,
                  }}
                >
                  {label}
                </div>

                <strong
                  style={{
                    display: "block",
                    fontSize: 17,
                    letterSpacing: -.2,
                    color: "#0f172a",
                  }}
                >
                  {value}
                </strong>

                <div
                  style={{
                    color: "#94a3b8",
                    fontSize: 12,
                    marginTop: 3,
                  }}
                >
                  {note}
                </div>
              </div>

              <span
                style={{
                  width: 10,
                  height: 10,
                  borderRadius: 999,
                  background: label === "Approvals" ? "#f59e0b" : "#2563eb",
                  boxShadow:
                    label === "Approvals"
                      ? "0 0 0 5px rgba(245,158,11,.10)"
                      : "0 0 0 5px rgba(37,99,235,.08)",
                }}
              />
            </div>
          ))}
        </section>

        <section
          style={{
            background: "#fff",
            borderRadius: 26,
            padding: "clamp(20px,2.2vw,30px)",
            boxShadow: "0 14px 34px rgba(15,23,42,.045)",
            marginBottom: 18,
          }}
        >
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              gap: 18,
              alignItems: "flex-start",
              marginBottom: 22,
              flexWrap: "wrap",
            }}
          >
            <div>
              <div
                style={{
                  color: "#2563eb",
                  fontSize: 12,
                  fontWeight: 900,
                  letterSpacing: 1.4,
                  textTransform: "uppercase",
                  marginBottom: 8,
                }}
              >
                Business profile intelligence
              </div>

              <h2 style={{ margin: 0, fontSize: 26, letterSpacing: -0.8 }}>
                Store business context for client-specific outputs
              </h2>

              <p style={{ marginTop: 10, color: "#64748b", maxWidth: 760, lineHeight: 1.55 }}>
                Add business context once so every active AI agent can produce more accurate
                deliverables, assets, copy, positioning, and execution recommendations.
              </p>
            </div>

            <div
              style={{
                background: "#eff6ff",
                color: "#2563eb",
                padding: "10px 14px",
                borderRadius: 999,
                fontWeight: 800,
                fontSize: 13.5,
              }}
            >
              ✓ Applied to execution
            </div>
          </div>

          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit,minmax(210px,1fr))",
              gap: 18,
            }}
          >
            {[
              ["Business niche", "Describe your business niche, product category, and market position"],
              ["Products & services", "Main products, bundles, offers"],
              ["Target audience", "Customer type, location, needs"],
              ["Competitors", "Competitor names, websites, market examples"],
              ["Offers", "Current promotions, bundles, guarantees"],
              ["Brand voice", "Premium, playful, clinical, bold, friendly"],
              ["Positioning", "Why customers should choose you"],
              ["Goals", "Sales, launches, retention, growth"],
            ].map(([label, value]) => (
              <label key={label}>
                <div style={{ color: "#64748b", fontSize: 12, fontWeight: 700, marginBottom: 7 }}>
                  {label}
                </div>
                <textarea
                  defaultValue={value}
                  rows={3}
                  style={{
                    width: "100%",
                    resize: "none",
                    borderRadius: 14,
                    border: "1px solid #e2e8f0",
                    background: "#fff",
                    padding: "16px 16px",
                    fontSize: 13.5,
                    lineHeight: 1.55,
                    color: "#0f172a",
                    outline: "none",
                    boxSizing: "border-box",
                    fontFamily: "inherit",
                  }}
                />
              </label>
            ))}
          </div>
        </section>


        <section style={cardStyle}>
          <StepHeader number="00" title="Connections" />
          <h3 style={cardTitle}>Connect business tools for live automation</h3>
          <p style={{ marginTop: 10, color: "#64748b", lineHeight: 1.6 }}>
            Connect approved business systems so active agents can complete real tasks using your own accounts. Use OAuth or scoped API keys where available. High-risk actions still require owner approval.
          </p>

          {integrationMessage ? (
            <div style={{ marginTop: 14, padding: "12px 14px", borderRadius: 14, background: "#eff6ff", color: "#2563eb", fontWeight: 800 }}>
              {integrationMessage}
            </div>
          ) : null}

          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(240px,1fr))", gap: 12, marginTop: 18 }}>
            {(integrations.length ? integrations : DEFAULT_CLIENT_INTEGRATIONS).map((integration) => (
              <div key={integration.integration_key} style={{ border: "1px solid #e5eaf2", borderRadius: 18, padding: 16, background: "#fff" }}>
                <div style={{ display: "flex", justifyContent: "space-between", gap: 10, alignItems: "flex-start" }}>
                  <div>
                    <div style={{ fontWeight: 900, color: "#0f172a" }}>{integration.name}</div>
                    <div style={{ marginTop: 5, color: "#64748b", fontSize: 12 }}>
                      {integration.connected ? `Connected: ${integration.provider}` : "Not connected"}
                    </div>
                  </div>
                  <span style={{
                    borderRadius: 999,
                    padding: "6px 9px",
                    fontSize: 11,
                    fontWeight: 900,
                    background: integration.connected ? "#dcfce7" : "#f1f5f9",
                    color: integration.connected ? "#16a34a" : "#64748b",
                  }}>
                    {integration.status}
                  </span>
                </div>

                <div style={{ marginTop: 12, color: "#64748b", fontSize: 12, lineHeight: 1.55 }}>
                  Used by: {integration.used_by_agents.slice(0, 3).join(", ")}
                </div>
                <div style={{ marginTop: 8, color: "#64748b", fontSize: 12, lineHeight: 1.55 }}>
                  Providers: {integration.providers.slice(0, 4).join(", ")}
                </div>
                <div style={{ marginTop: 8, color: "#64748b", fontSize: 12, lineHeight: 1.55 }}>
                  Access: {integration.recommended_auth}
                </div>
                {integration.credential_hint ? (
                  <div style={{ marginTop: 8, color: "#16a34a", fontSize: 12, fontWeight: 800 }}>
                    {integration.credential_hint}
                  </div>
                ) : null}

                <div style={{ marginTop: 12, display: "flex", gap: 8, flexWrap: "wrap" }}>
                  <button type="button" onClick={() => connectIntegration(integration)} style={{ border: "1px solid #dbeafe", background: "#eff6ff", color: "#2563eb", borderRadius: 11, padding: "8px 10px", fontWeight: 900, cursor: "pointer" }}>
                    Connect
                  </button>
                  <button type="button" onClick={() => testIntegration(integration)} style={{ border: "1px solid #e5eaf2", background: "#fff", color: "#334155", borderRadius: 11, padding: "8px 10px", fontWeight: 900, cursor: "pointer" }}>
                    Test
                  </button>
                  <button type="button" onClick={() => disconnectIntegration(integration)} style={{ border: "1px solid #fee2e2", background: "#fff", color: "#dc2626", borderRadius: 11, padding: "8px 10px", fontWeight: 900, cursor: "pointer" }}>
                    Disconnect
                  </button>
                </div>
              </div>
            ))}
          </div>
        </section>


        <section style={primaryGridStyle}>
          <div style={cardStyle}>
            <StepHeader number="01" title="Run AI Agent" />
            <h3 style={cardTitle}>Select agents, define task, and execute.</h3>

            <div style={{ display: "grid", gridTemplateColumns: "minmax(260px,360px) minmax(320px,1fr)", gap: 18, marginTop: 18 }}>
              <div>
                <div style={labelStyle}>Active agents</div>
                <div style={{ display: "grid", gap: 7 }}>
                  {(account?.active_agents || DEFAULT_AGENTS).map((agent) => {
                    const active = selectedAgents.includes(agent);
                    return (
                      <button
                        key={getAgentDisplayName(agent)}
                        onClick={() => toggleAgent(agent)}
                        style={{
                          border: active ? "1px solid #bfdbfe" : "1px solid #e5eaf2",
                          background: active ? "#eff6ff" : "#fff",
                          color: active ? "#2563eb" : "#0f172a",
                          padding: "11px 12px",
                          borderRadius: 11,
                          cursor: "pointer",
                          textAlign: "left",
                          fontSize: 12,
                          fontWeight: 800,
                        }}
                      >
                        {active ? "● " : "○ "}
                        {getAgentDisplayName(agent)}
                      </button>
                    );
                  })}
                </div>
              </div>

              <div>
                <div style={labelStyle}>Task</div>
                <textarea
                  defaultValue="Create a client-specific client deliverable using the saved business profile, selected active agents, current offer, target audience, goals, and execution requirements."
                  style={{
                    width: "100%",
                    minHeight: 185,
                    resize: "none",
                    borderRadius: 14,
                    border: "1px solid #dbe3ee",
                    background: "#fff",
                    padding: 14,
                    fontSize: 13.5,
                    lineHeight: 1.55,
                    boxSizing: "border-box",
                    fontFamily: "inherit",
                  }}
                />

                <button
                  onClick={async () => {
                    setExecutionState("running");
                    setToastMessage("Execution started. Generating client deliverables...");

                    try {
                      const response = await fetch("/api/run-agent", {
                        method: "POST",
                        headers: { "Content-Type": "application/json", "x-tenant-id": "client_demo_001", "x-actor-role": "customer" },
                        credentials: "include",
                        body: JSON.stringify({
                          selected_agents: selectedAgents,
                          task: "Create a client-specific client deliverable using the saved business profile, selected active agents, current offer, target audience, goals, and execution requirements.",
                          business_profile: {
                            niche: "Saved client business profile",
                            target_audience: "Saved target audience and customer context",
                            positioning: "Client-specific commercial positioning and execution requirements",
                          },
                        }),
                      });

                      const data = await response.json();

                      if (!response.ok || !data?.success) {
                        throw new Error("Execution failed");
                      }

                      setLiveDeliverable(data.deliverable);
                      setSelectedAssetIndex(0);
                      setExecutionState("completed");
                      setReviewStatus("pending");
                      setToastMessage("Client deliverable generated and ready for review.");
                    } catch {
                      setExecutionState("idle");
                      setToastMessage("Execution could not be completed. Please try again.");
                    }
                  }}
                  style={{
                    marginTop: 12,
                    width: "100%",
                    border: "none",
                    borderRadius: 13,
                    background:
                      executionState === "running"
                        ? "linear-gradient(135deg,#64748b,#475569)"
                        : "linear-gradient(135deg,#2563eb,#06b6d4)",
                    color: "#fff",
                    padding: "13px 16px",
                    fontWeight: 900,
                    cursor: "pointer",
                    boxShadow: "0 12px 26px rgba(37,99,235,.18)",
                  }}
                >
                  {executionState === "running" ? "Generating..." : "✨ Run Agent"}
                </button>
              </div>
            </div>

            <div style={{ marginTop: 12, color: "#64748b", fontSize: 12 }}>
              ⓘ All agents will use the business profile context above.
            </div>
          </div>

          <div style={cardStyle}>
            <StepHeader number="02" title="Live execution flow" />
            <h3 style={cardTitle}>Governed execution pipeline</h3>
            <p style={mutedText}>
              Every AI deliverable flows through approval, optimisation, workflow validation,
              and governed execution before deployment.
            </p>

            <div style={{ display: "grid", gap: 12, marginTop: 20 }}>
              {[
                ["Execution requested", executionState === "idle" ? "Waiting" : "Started", liveDeliverable?.created_at || "Live"],
                ["Deliverable status", executionState === "completed" ? "Ready" : "Pending", liveDeliverable?.created_at || "Live"],
                ["Client review", reviewStatus === "approved" ? "Approved" : reviewStatus === "rejected" ? "Revision requested" : "Pending", reviewStatus === "approved" ? "Complete" : "Open"],
                ["Execution ready", "Next", "—"],
              ].map(([title, status, time], index) => (
                <div key={title} style={{ display: "grid", gridTemplateColumns: "34px 1fr auto", gap: 12, alignItems: "center" }}>
                  <div
                    style={{
                      width: 28,
                      height: 28,
                      borderRadius: 10,
                      background: index === 3 ? "#06b6d4" : "#2563eb",
                      color: "#fff",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      fontSize: 13.5,
                    }}
                  >
                    {index + 1}
                  </div>
                  <div>
                    <div style={{ fontWeight: 850, fontSize: 13 }}>{title}</div>
                    <div style={{ color: "#64748b", fontSize: 12 }}>{status}</div>
                  </div>
                  <div style={{ color: "#64748b", fontSize: 12 }}>{time}</div>
                </div>
              ))}
            </div>
          </div>

          <div style={cardStyle}>
            <StepHeader number="03" title="Execution workspace" />
            <h3 style={cardTitle}>Client deliverables will appear here</h3>
            <p style={mutedText}>
              Campaign outputs, approvals, execution flows, creative assets, billing events,
              and governed automation actions will appear after execution.
            </p>

            <div
              style={{
                marginTop: 24,
                minHeight: 185,
                borderRadius: 18,
                background:
                  executionState === "running"
                    ? "linear-gradient(135deg,#eff6ff,#ffffff)"
                    : executionState === "completed"
                      ? "linear-gradient(135deg,#ecfdf5,#ffffff)"
                      : "linear-gradient(135deg,#eff6ff,#f8fafc)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                color:
                  executionState === "completed"
                    ? "#16a34a"
                    : "#2563eb",
                fontWeight: 900,
                textAlign: "center",
                padding: 20,
              }}
            >
              {executionState === "running" ? (
                <div>
                  <div style={{ fontSize: 28, marginBottom: 10 }}>⏳</div>
                  <div>Generating client deliverables...</div>
                  <div
                    style={{
                      marginTop: 14,
                      height: 8,
                      width: 240,
                      maxWidth: "100%",
                      borderRadius: 999,
                      background: "#dbeafe",
                      overflow: "hidden",
                    }}
                  >
                    <div
                      style={{
                        width: "72%",
                        height: "100%",
                        borderRadius: 999,
                        background: "linear-gradient(135deg,#2563eb,#06b6d4)",
                      }}
                    />
                  </div>
                </div>
              ) : executionState === "completed" && liveDeliverable ? (
                <div style={{ width: "100%", textAlign: "left" }}>
                  <div
                    style={{
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "space-between",
                      gap: 12,
                      marginBottom: 12,
                    }}
                  >
                    <div
                      style={{
                        color: "#16a34a",
                        fontWeight: 900,
                        fontSize: 13,
                      }}
                    >
                      ✅ Latest deliverable ready
                    </div>

                    <div
                      style={{
                        color: "#64748b",
                        fontSize: 12,
                        fontWeight: 700,
                      }}
                    >
                      {liveDeliverable?.created_at || "Ready now"}
                    </div>
                  </div>

                  <div
                    style={{
                      color: "#0f172a",
                      fontSize: 18,
                      fontWeight: 900,
                      lineHeight: 1.25,
                      marginBottom: 8,
                    }}
                  >
                    {liveDeliverable?.title || "Client deliverable"}
                  </div>

                  <div
                    style={{
                      color: "#64748b",
                      fontSize: 13,
                      lineHeight: 1.55,
                      maxWidth: 420,
                    }}
                  >
                    {(liveDeliverable?.summary || "Client-ready deliverable generated.").slice(0, 150)}
                    {(liveDeliverable?.summary || "").length > 150 ? "..." : ""}
                  </div>

                  <div
                    style={{
                      marginTop: 14,
                      display: "flex",
                      gap: 8,
                      flexWrap: "wrap",
                    }}
                  >
                    {(liveDeliverable?.tags || ["Approval required"]).slice(0, 3).map((tag: string) => (
                      <span
                        key={tag}
                        style={{
                          border: "1px solid #dbeafe",
                          background: "#eff6ff",
                          color: "#2563eb",
                          borderRadius: 999,
                          padding: "7px 10px",
                          fontSize: 12,
                          fontWeight: 800,
                        }}
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                </div>
              ) : executionState === "completed" ? (
                <div>
                  <div style={{ fontSize: 28, marginBottom: 10 }}>✅</div>
                  <div>Deliverable ready for review</div>
                  <div style={{ marginTop: 6, color: "#64748b", fontSize: 12 }}>
                    Approval or feedback required
                  </div>
                </div>
              ) : (
                "Run selected agents to generate a live deliverable"
              )}
            </div>
          </div>

          <div style={cardStyle}>
            <StepHeader number="04" title="Quick actions" />
            <h3 style={cardTitle}>Workspace actions</h3>

            <div style={{ display: "grid", gap: 11, marginTop: 20 }}>
              {["View execution history", "Manage workflows", "Agent performance", "Workspace settings"].map((item) => (
                <button
                  key={item}
                  style={{
                    border: "1px solid #e5eaf2",
                    background: "#fff",
                    borderRadius: 13,
                    padding: "13px 14px",
                    textAlign: "left",
                    fontWeight: 800,
                    cursor: "pointer",
                  }}
                >
                  {item} →
                </button>
              ))}
            </div>
          </div>
        </section>

        <section style={secondaryGridStyle}>
          <div style={cardStyle}>
            <StepHeader number="05" title="Execution timeline" />
            <h3 style={cardTitle}>Execution timeline</h3>
            <p style={{ color: "#2563eb", fontWeight: 800, fontSize: 13 }}>Live governed execution events connected</p>

            <div style={{ display: "grid", gap: 18, marginTop: 22 }}>
              {(executionTimeline.length
                ? executionTimeline
                : [{
                    event_id: "pending_execution_timeline",
                    created_at: liveDeliverable?.created_at || "",
                    agent_id: selectedAgents[0] || "agent",
                    event_type: timelineLoading ? "loading_execution_timeline" : "waiting_for_execution",
                    event_status: liveDeliverable ? "deliverable_generated" : "waiting",
                    workflow_stage: "client_workspace",
                    action_type: "client_execution",
                    title: liveDeliverable
                      ? "Deliverable generated"
                      : timelineLoading
                        ? "Loading execution timeline"
                        : "Waiting for execution",
                    summary: liveDeliverable
                      ? "The latest client deliverable is ready for review."
                      : "Run selected agents to generate live governed execution events.",
                    approval_status: reviewStatus,
                    quality_status: liveDeliverable ? "ready_for_review" : "pending",
                    execution_status: executionState,
                  }]).map((event) => {
                const time = event.created_at
                  ? new Date(event.created_at).toLocaleString()
                  : "Live";
                const agentName = getAgentDisplayName(event.agent_id || "agent");
                const approvalStatus = event.approval_status || "not_required";
                const qualityStatus = event.quality_status || "pending";
                const executionStatus = event.execution_status || event.event_status || "tracked";
                const isExecutionIssue = String(executionStatus).toLowerCase().includes("failed") || String(executionStatus).toLowerCase().includes("unsupported");
                const isApprovalRequired = String(approvalStatus).toLowerCase().includes("approval") && !String(approvalStatus).toLowerCase().includes("approved_safe");
                const statusTone = isExecutionIssue
                  ? { bg: "#fff7ed", border: "#fed7aa", text: "#ea580c", label: "Needs attention" }
                  : isApprovalRequired
                    ? { bg: "#fffbeb", border: "#fde68a", text: "#ca8a04", label: "Approval gated" }
                    : { bg: "#f0fdf4", border: "#bbf7d0", text: "#16a34a", label: "Governed ready" };

                return (
                  <div
                    key={event.event_id || `${event.agent_id}-${event.event_type}`}
                    style={{
                      border: `1px solid ${statusTone.border}`,
                      borderRadius: 18,
                      padding: 16,
                      background: "#ffffff",
                      boxShadow: "0 12px 30px rgba(15,23,42,0.05)",
                    }}
                  >
                    <div style={{ display: "flex", justifyContent: "space-between", gap: 14, flexWrap: "wrap", alignItems: "flex-start" }}>
                      <div>
                        <div style={{ color: "#64748b", fontSize: 12.5, fontWeight: 800 }}>{time}</div>
                        <div style={{ fontWeight: 950, color: "#0f172a", fontSize: 16, marginTop: 5 }}>
                          {event.title || event.event_type || "Execution event"}
                        </div>
                        <div style={{ color: "#475569", fontSize: 13.5, lineHeight: 1.45, marginTop: 6 }}>
                          {event.summary || "Governed execution event recorded by the platform ledger."}
                        </div>
                      </div>

                      <div style={{ textAlign: "right", color: "#64748b", fontSize: 13, fontWeight: 850 }}>
                        <div>{agentName}</div>
                        <div style={{ marginTop: 8, display: "inline-flex", background: statusTone.bg, color: statusTone.text, border: `1px solid ${statusTone.border}`, borderRadius: 999, padding: "6px 9px", fontSize: 11.5, fontWeight: 950 }}>
                          {statusTone.label}
                        </div>
                      </div>
                    </div>

                    <div style={{ display: "flex", flexWrap: "wrap", gap: 8, marginTop: 14 }}>
                      <span style={{ background: "#eff6ff", color: "#2563eb", border: "1px solid #dbeafe", borderRadius: 999, padding: "7px 10px", fontWeight: 850, fontSize: 12 }}>
                        {event.execution_action || event.action_type || "Tracked action"}
                      </span>
                      <span style={{ background: "#f0fdf4", color: "#16a34a", border: "1px solid #dcfce7", borderRadius: 999, padding: "7px 10px", fontWeight: 850, fontSize: 12 }}>
                        Quality: {qualityStatus}
                      </span>
                      <span style={{ background: "#fff7ed", color: "#ea580c", border: "1px solid #fed7aa", borderRadius: 999, padding: "7px 10px", fontWeight: 850, fontSize: 12 }}>
                        Approval: {approvalStatus}
                      </span>
                      <span style={{ background: statusTone.bg, color: statusTone.text, border: `1px solid ${statusTone.border}`, borderRadius: 999, padding: "7px 10px", fontWeight: 850, fontSize: 12 }}>
                        Execution: {executionStatus}
                      </span>
                      <span style={{ background: "#f8fafc", color: "#334155", border: "1px solid #e2e8f0", borderRadius: 999, padding: "7px 10px", fontWeight: 850, fontSize: 12 }}>
                        Stage: {event.workflow_stage || "workflow"}
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          <div style={cardStyle}>
            <div style={{ display: "flex", justifyContent: "space-between", gap: 16, flexWrap: "wrap" }}>
              <div>
                <StepHeader number="06" title="Execution output viewer" />
                <h3 style={cardTitle}>Client deliverables</h3>
              </div>
              <div
                style={{
                  background: reviewStatus === "rejected" ? "#fee2e2" : "#dcfce7",
                  color: reviewStatus === "rejected" ? "#dc2626" : "#16a34a",
                  padding: "10px 14px",
                  borderRadius: 999,
                  fontWeight: 900,
                  fontSize: 13.5,
                  height: "fit-content",
                }}
              >
                {reviewStatus === "approved" ? "Approved" : reviewStatus === "rejected" ? "Revision requested" : "Completed"}
              </div>
            </div>

            <div style={deliverableCardGridStyle}>
              <div
                style={{
                  minHeight: 280,
                  borderRadius: 18,
                  background: "#f8fafc",
                  border: "1px solid #e5eaf2",
                  position: "relative",
                  overflow: "hidden",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                }}
              >
                {primaryAssetUrl ? (
                  <img
                    src={primaryAssetUrl}
                    alt={liveDeliverable?.title || "Generated deliverable asset"}
                    style={{
                      width: "100%",
                      height: "100%",
                      objectFit: "cover",
                      display: "block",
                    }}
                  />
                ) : (
                  <div
                    style={{
                      display: "flex",
                      flexDirection: "column",
                      justifyContent: "space-between",
                      height: "100%",
                      width: "100%",
                      padding: 22,
                      background: "linear-gradient(180deg,#ffffff 0%,#f8fafc 100%)",
                      color: "#64748b",
                      boxSizing: "border-box",
                    }}
                  >
                    <div>
                      <div
                        style={{
                          display: "flex",
                          alignItems: "center",
                          justifyContent: "space-between",
                          gap: 12,
                          marginBottom: 18,
                        }}
                      >
                        <div
                          style={{
                            display: "flex",
                            alignItems: "center",
                            gap: 10,
                          }}
                        >
                          <div
                            style={{
                              width: 42,
                              height: 42,
                              borderRadius: 14,
                              background: "#eff6ff",
                              display: "flex",
                              alignItems: "center",
                              justifyContent: "center",
                              color: "#2563eb",
                              fontSize: 18,
                              fontWeight: 900,
                              flex: "0 0 auto",
                            }}
                          >
                            ✦
                          </div>

                          <div>
                            <div
                              style={{
                                color: "#0f172a",
                                fontWeight: 900,
                                fontSize: 13,
                                marginBottom: 3,
                              }}
                            >
                              Media preview unavailable
                            </div>

                            <div
                              style={{
                                fontSize: 11,
                                color: "#64748b",
                              }}
                            >
                              Waiting for uploaded or generated assets
                            </div>
                          </div>
                        </div>

                        <div
                          style={{
                            border: "1px solid #e2e8f0",
                            borderRadius: 999,
                            padding: "6px 9px",
                            fontSize: 11,
                            fontWeight: 800,
                            background: "#fff",
                            color: "#475569",
                            
                          }}
                        >
                          Pending media
                        </div>
                      </div>

                      <div
                        style={{
                          borderRadius: 18,
                          border: "1px dashed #dbe4ee",
                          background: "linear-gradient(135deg,#f8fafc 0%,#f1f5f9 100%)",
                          minHeight: 142,
                          display: "flex",
                          alignItems: "center",
                          justifyContent: "center",
                          overflow: "hidden",
                        }}
                      >
                        <div
                          style={{
                            textAlign: "center",
                            padding: 22,
                            maxWidth: "100%",
                          }}
                        >
                          <div
                            style={{
                              fontSize: 30,
                              marginBottom: 12,
                            }}
                          >
                            🖼️
                          </div>

                          <div
                            style={{
                              color: "#0f172a",
                              fontWeight: 800,
                              fontSize: 13,
                              marginBottom: 8,
                            }}
                          >
                            No live asset attached
                          </div>

                          <div
                            style={{
                              fontSize: 11.5,
                              lineHeight: 1.6,
                              color: "#64748b",
                            }}
                          >
                            Generated assets, uploaded brand files, previews, and deliverable media will appear here automatically.
                          </div>
                        </div>
                      </div>
                    </div>

                    <div
                      style={{
                        display: "flex",
                        justifyContent: "space-between",
                        alignItems: "center",
                        gap: 12,
                        marginTop: 18,
                        fontSize: 11,
                        color: "#94a3b8",
                      }}
                    >
                      <div>Secure asset workspace</div>
                      <div>Enterprise media pipeline</div>
                    </div>
                  </div>
                )}
              </div>

              {attachedAssets.length > 0 ? (
                <div
                  style={{
                    position: "absolute",
                    left: 12,
                    bottom: 12,
                    right: 12,
                    display: "flex",
                    justifyContent: "space-between",
                    gap: 10,
                    pointerEvents: "none",
                    flexWrap: "wrap",
                  }}
                >
                  <div
                    style={{
                      background: "rgba(15,23,42,.82)",
                      color: "#fff",
                      borderRadius: 999,
                      padding: "7px 10px",
                      fontSize: 11,
                      fontWeight: 900,
                      overflow: "hidden",
                      textOverflow: "ellipsis",
                      whiteSpace: "nowrap",
                    }}
                  >
                    {selectedAsset?.title || selectedAsset?.name || "Selected media"}
                  </div>
                  <div
                    style={{
                      background: "rgba(255,255,255,.92)",
                      color: "#334155",
                      borderRadius: 999,
                      padding: "7px 10px",
                      fontSize: 11,
                      fontWeight: 900,
                      whiteSpace: "nowrap",
                    }}
                  >
                    {selectedAssetIndex + 1}/{attachedAssets.length}
                  </div>
                </div>
              ) : null}

              <div style={{ minWidth: 0 }}>
                <div style={{ display: "flex", justifyContent: "space-between", gap: 10, flexWrap: "wrap" }}>
                  <h4 style={{ margin: 0, fontSize: 20 }}>
                    {liveDeliverable?.title || "Latest client deliverable"}
                  </h4>
                  <div style={{ color: "#64748b", fontSize: 12 }}>
                    {liveDeliverable?.created_at || "Ready for review"}
                  </div>
                </div>

                <p style={{ color: "#475569", lineHeight: 1.6 }}>
                  {liveDeliverable?.summary ||
                    "Client-specific deliverable generated from the latest execution, business profile, selected agents, and review requirements."}
                </p>

                <div style={{ display: "flex", gap: 10, flexWrap: "wrap", marginBottom: 16 }}>
                  {(liveDeliverable?.tags || ["Deliverable", "Assets", "Execution", "Workflow"]).map((tag: string) => (
                    <span
                      key={tag}
                      style={{
                        border: "1px solid #e5eaf2",
                        borderRadius: 999,
                        padding: "8px 11px",
                        fontSize: 12,
                        fontWeight: 800,
                      }}
                    >
                      {tag}
                    </span>
                  ))}
                </div>

                {attachedAssets.length > 1 ? (
                  <div style={{ marginBottom: 16 }}>
                    <div style={{ color: "#64748b", fontSize: 12, fontWeight: 800, marginBottom: 8 }}>
                      Attached media
                    </div>
                    <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(120px,1fr))", gap: 8 }}>
                      {attachedAssets.slice(0, 6).map((asset, index) => {
                        const assetUrl = asset?.url || asset?.image_url || asset?.src || "";
                        const selected = selectedAssetIndex === index;
                        return (
                          <button
                            key={`${assetUrl || asset?.name || "asset"}-${index}`}
                            onClick={() => setSelectedAssetIndex(index)}
                            style={{
                              border: selected ? "1px solid #2563eb" : "1px solid #e5eaf2",
                              borderRadius: 12,
                              padding: 10,
                              textAlign: "left",
                              fontSize: 11,
                              fontWeight: 800,
                              color: selected ? "#2563eb" : "#475569",
                              background: selected ? "#eff6ff" : "#f8fafc",
                              cursor: "pointer",
                            }}
                          >
                            <div style={{ marginBottom: 4 }}>{asset?.title || asset?.name || `Asset ${index + 1}`}</div>
                            <div style={{ color: "#94a3b8", fontSize: 10 }}>
                              {asset?.type || asset?.source || "media"}
                            </div>
                          </button>
                        );
                      })}
                    </div>
                  </div>
                ) : null}

                <div
                  style={{
                    display: "flex",
                    gap: 10,
                    flexWrap: "wrap",
                    marginBottom: 16,
                  }}
                >
                  <button
                    onClick={() => setShowDeliverableModal(true)}
                    style={{
                      border: "1px solid #dbeafe",
                      background: "#eff6ff",
                      color: "#2563eb",
                      borderRadius: 12,
                      padding: "10px 13px",
                      fontWeight: 900,
                      fontSize: 12,
                      cursor: "pointer",
                    }}
                  >
                    Expand preview
                  </button>

                  <button
                    disabled={!deliverableDownloadUrl}
                    onClick={() => {
                      if (!deliverableDownloadUrl) {
                        setToastMessage("No downloadable asset is attached yet.");
                        return;
                      }
                      window.open(deliverableDownloadUrl, "_blank", "noopener,noreferrer");
                    }}
                    style={{
                      border: "1px solid #e5eaf2",
                      background: "#fff",
                      color: deliverableDownloadUrl ? "#334155" : "#94a3b8",
                      borderRadius: 12,
                      padding: "10px 13px",
                      fontWeight: 900,
                      fontSize: 12,
                      cursor: deliverableDownloadUrl ? "pointer" : "not-allowed",
                    }}
                  >
                    Open asset
                  </button>

                  <button
                    onClick={async () => {
                      const shareText = `${liveDeliverable?.title || "Client deliverable"} — ${liveDeliverable?.summary || "Ready for review."}`;
                      try {
                        await navigator.clipboard.writeText(shareText);
                        setToastMessage("Deliverable summary copied.");
                      } catch {
                        setToastMessage("Copy was not available in this browser.");
                      }
                    }}
                    style={{
                      border: "1px solid #e5eaf2",
                      background: "#fff",
                      color: "#334155",
                      borderRadius: 12,
                      padding: "10px 13px",
                      fontWeight: 900,
                      fontSize: 12,
                      cursor: "pointer",
                    }}
                  >
                    Copy summary
                  </button>
                </div>

                <div style={{ display: "flex", gap: 12, flexWrap: "wrap", alignItems: "center" }}>
                  <button
                    onClick={() => setShowDeliverableModal(true)}
                    style={{
                      border: "1px solid #dbeafe",
                      background: "#eff6ff",
                      color: "#2563eb",
                      borderRadius: 12,
                      padding: "12px 18px",
                      fontWeight: 900,
                      cursor: "pointer",
                    }}
                  >
                    View full deliverable
                  </button>

                  <button
                    disabled={reviewActionLoading}
                    onClick={async () => {
                      const saved = await recordClientReviewAction("approved");
                      if (!saved) return;

                      setReviewStatus("approved");
                      setExecutionState("completed");
                      setToastMessage("Deliverable approved and saved to the client review log.");
                    }}
                    style={{
                      border: "none",
                      background: reviewActionLoading ? "#86efac" : "#22c55e",
                      color: "#fff",
                      borderRadius: 12,
                      padding: "12px 18px",
                      fontWeight: 900,
                      cursor: reviewActionLoading ? "not-allowed" : "pointer",
                    }}
                  >
                    {reviewActionLoading ? "Saving..." : "👍 Approve"}
                  </button>

                  <button
                    disabled={reviewActionLoading}
                    onClick={() => {
                      setToastMessage("");
                      setShowRejectModal(true);
                      setExecutionState("rejected");
                    }}
                    style={{
                      border: "1px solid #fecaca",
                      background: "#fff",
                      color: "#dc2626",
                      borderRadius: 12,
                      padding: "12px 18px",
                      fontWeight: 900,
                      cursor: reviewActionLoading ? "not-allowed" : "pointer",
                    }}
                  >
                    👎 Reject
                  </button>
                </div>

                <div
                  style={{
                    marginTop: 14,
                    paddingTop: 14,
                    borderTop: "1px solid #eef2f7",
                    color: "#94a3b8",
                    fontSize: 11.5,
                    lineHeight: 1.5,
                  }}
                >
                  Review actions are saved to the workspace history and can be used to improve future deliverables.
                </div>
              </div>
            </div>
          </div>
        </section>
      </div>


      {showDeliverableModal ? (
        <div
          style={{
            position: "fixed",
            inset: 0,
            background: "rgba(15,23,42,.32)",
            zIndex: 9997,
            display: "flex",
            alignItems: "flex-start",
            justifyContent: "center",
            padding: "clamp(14px,2vw,24px)",
            overflow: "auto",
          }}
        >
          <div
            style={{
              width: 1040,
              maxWidth: "100%",
              maxHeight: "calc(100vh - 32px)",
              overflow: "auto",
              background: "#fff",
              borderRadius: 28,
              boxShadow: "0 30px 90px rgba(15,23,42,.24)",
              border: "1px solid #e5eaf2",
            }}
          >
            <div
              style={{
                padding: "clamp(20px,2.4vw,28px)",
                borderBottom: "1px solid #eef2f7",
                display: "flex",
                justifyContent: "space-between",
                gap: 18,
                alignItems: "flex-start",
                flexWrap: "wrap",
              }}
            >
              <div>
                <div
                  style={{
                    color: "#2563eb",
                    fontSize: 12,
                    fontWeight: 900,
                    letterSpacing: 1.2,
                    textTransform: "uppercase",
                    marginBottom: 8,
                  }}
                >
                  Full deliverable review
                </div>

                <h2
                  style={{
                    margin: 0,
                    fontSize: "clamp(22px,2.4vw,28px)",
                    letterSpacing: -0.8,
                    lineHeight: 1.15,
                  }}
                >
                  {liveDeliverable?.title || "Client deliverable"}
                </h2>

                <div style={{ marginTop: 8, color: "#64748b", fontSize: 13 }}>
                  {liveDeliverable?.created_at || "Ready for review"}
                </div>

                <div style={{ display: "flex", gap: 8, flexWrap: "wrap", marginTop: 14 }}>
                  <button
                    disabled={!deliverableDownloadUrl}
                    onClick={() => {
                      if (!deliverableDownloadUrl) {
                        setToastMessage("No downloadable asset is attached yet.");
                        return;
                      }
                      window.open(deliverableDownloadUrl, "_blank", "noopener,noreferrer");
                    }}
                    style={{
                      border: "1px solid #e5eaf2",
                      background: "#fff",
                      color: deliverableDownloadUrl ? "#334155" : "#94a3b8",
                      borderRadius: 12,
                      padding: "9px 12px",
                      fontWeight: 900,
                      fontSize: 12,
                      cursor: deliverableDownloadUrl ? "pointer" : "not-allowed",
                    }}
                  >
                    Open asset
                  </button>

                  <button
                    onClick={async () => {
                      const shareText = `${liveDeliverable?.title || "Client deliverable"} — ${liveDeliverable?.summary || "Ready for review."}`;
                      try {
                        await navigator.clipboard.writeText(shareText);
                        setToastMessage("Deliverable summary copied.");
                      } catch {
                        setToastMessage("Copy was not available in this browser.");
                      }
                    }}
                    style={{
                      border: "1px solid #e5eaf2",
                      background: "#fff",
                      color: "#334155",
                      borderRadius: 12,
                      padding: "9px 12px",
                      fontWeight: 900,
                      fontSize: 12,
                      cursor: "pointer",
                    }}
                  >
                    Copy summary
                  </button>
                </div>
              </div>

              <button
                onClick={() => setShowDeliverableModal(false)}
                aria-label="Close full deliverable review"
                style={{
                  width: 42,
                  height: 42,
                  borderRadius: 999,
                  border: "1px solid #e5eaf2",
                  background: "#fff",
                  cursor: "pointer",
                  fontWeight: 900,
                  color: "#0f172a",
                }}
              >
                ×
              </button>
            </div>

            <div style={modalContentGridStyle}>
              <div
                style={{
                  borderRadius: 22,
                  border: "1px solid #e5eaf2",
                  background: "#f8fafc",
                  overflow: "hidden",
                  minHeight: "clamp(260px,38vw,360px)",
                }}
              >
                {primaryAssetUrl ? (
                  <img
                    src={primaryAssetUrl}
                    alt={liveDeliverable?.title || "Generated deliverable asset"}
                    style={{
                      width: "100%",
                      height: "100%",
                      minHeight: "clamp(260px,38vw,360px)",
                      objectFit: "cover",
                      display: "block",
                    }}
                  />
                ) : (
                  <div
                    style={{
                      minHeight: 320,
                      padding: 28,
                      display: "flex",
                      flexDirection: "column",
                      justifyContent: "center",
                      alignItems: "center",
                      textAlign: "center",
                      background: "linear-gradient(135deg,#ffffff,#f8fafc)",
                    }}
                  >
                    <div style={{ fontSize: 38, marginBottom: 14 }}>🖼️</div>
                    <div style={{ color: "#0f172a", fontWeight: 900, fontSize: 16, marginBottom: 8 }}>
                      No live asset attached
                    </div>
                    <div style={{ color: "#64748b", fontSize: 13, lineHeight: 1.65, maxWidth: 280 }}>
                      Generated assets, uploaded brand files, previews, and deliverable media will appear here once attached.
                    </div>
                  </div>
                )}
              </div>

              <div style={{ minWidth: 0 }}>
                <div style={{ display: "flex", gap: 10, flexWrap: "wrap", marginBottom: 18 }}>
                  {(liveDeliverable?.tags || ["Deliverable", "Assets", "Execution", "Workflow"]).map((tag: string) => (
                    <span
                      key={tag}
                      style={{
                        border: "1px solid #dbeafe",
                        background: "#eff6ff",
                        color: "#2563eb",
                        borderRadius: 999,
                        padding: "8px 11px",
                        fontSize: 12,
                        fontWeight: 900,
                      }}
                    >
                      {tag}
                    </span>
                  ))}
                </div>

                <section
                  style={{
                    border: "1px solid #eef2f7",
                    borderRadius: 18,
                    padding: 20,
                    marginBottom: 16,
                    background: "#fff",
                  }}
                >
                  <h3 style={{ margin: "0 0 10px", fontSize: 17 }}>Executive summary</h3>
                  <p style={{ margin: 0, color: "#475569", lineHeight: 1.75, fontSize: 14.5 }}>
                    {liveDeliverable?.summary ||
                      "Client-specific deliverable generated from the latest execution, business profile, selected agents, and review requirements."}
                  </p>
                </section>

                <section
                  style={{
                    border: "1px solid #eef2f7",
                    borderRadius: 18,
                    padding: 20,
                    marginBottom: 16,
                    background: "#fbfdff",
                  }}
                >
                  <h3 style={{ margin: "0 0 12px", fontSize: 17 }}>Review checklist</h3>
                  <div style={{ display: "grid", gap: 10 }}>
                    {[
                      "Confirm brand fit and tone",
                      "Confirm offer and deliverable direction",
                      "Check media or asset requirements",
                      "Approve for execution or request revision",
                    ].map((item) => (
                      <div
                        key={item}
                        style={{
                          display: "flex",
                          alignItems: "center",
                          gap: 10,
                          color: "#475569",
                          fontSize: 13.5,
                        }}
                      >
                        <span
                          style={{
                            width: 22,
                            height: 22,
                            borderRadius: 999,
                            background: "#eff6ff",
                            color: "#2563eb",
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center",
                            fontSize: 12,
                            fontWeight: 900,
                          }}
                        >
                          ✓
                        </span>
                        {item}
                      </div>
                    ))}
                  </div>
                </section>

                {attachedAssets.length > 0 ? (
                  <section
                    style={{
                      border: "1px solid #eef2f7",
                      borderRadius: 18,
                      padding: 20,
                      marginBottom: 16,
                      background: "#fff",
                    }}
                  >
                    <h3 style={{ margin: "0 0 12px", fontSize: 17 }}>Attached media</h3>
                    <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(150px,1fr))", gap: 10 }}>
                      {attachedAssets.slice(0, 8).map((asset, index) => {
                        const assetUrl = asset?.url || asset?.image_url || asset?.src || "";
                        const selected = selectedAssetIndex === index;
                        return (
                          <button
                            key={`${assetUrl || asset?.name || "asset"}-${index}`}
                            onClick={() => setSelectedAssetIndex(index)}
                            style={{
                              border: selected ? "1px solid #2563eb" : "1px solid #e5eaf2",
                              borderRadius: 14,
                              padding: 12,
                              textAlign: "left",
                              fontSize: 12,
                              fontWeight: 800,
                              color: selected ? "#2563eb" : "#475569",
                              background: selected ? "#eff6ff" : "#f8fafc",
                              cursor: "pointer",
                            }}
                          >
                            <div style={{ marginBottom: 5 }}>{asset?.title || asset?.name || `Asset ${index + 1}`}</div>
                            <div style={{ color: "#94a3b8", fontSize: 10.5 }}>
                              {asset?.type || asset?.source || asset?.mime_type || "media"}
                            </div>
                          </button>
                        );
                      })}
                    </div>
                  </section>
                ) : null}

                <div style={{ display: "flex", gap: 12, flexWrap: "wrap", justifyContent: "flex-end", alignItems: "center" }}>
                  <button
                    onClick={() => setShowDeliverableModal(false)}
                    style={{
                      border: "1px solid #e5eaf2",
                      background: "#fff",
                      color: "#334155",
                      borderRadius: 12,
                      padding: "12px 16px",
                      fontWeight: 900,
                      cursor: "pointer",
                    }}
                  >
                    Close
                  </button>

                  <button
                    disabled={reviewActionLoading}
                    onClick={async () => {
                      const saved = await recordClientReviewAction("approved");
                      if (!saved) return;

                      setReviewStatus("approved");
                      setExecutionState("completed");
                      setShowDeliverableModal(false);
                      setToastMessage("Deliverable approved and saved to the client review log.");
                    }}
                    style={{
                      border: "none",
                      background: reviewActionLoading ? "#86efac" : "#22c55e",
                      color: "#fff",
                      borderRadius: 12,
                      padding: "12px 18px",
                      fontWeight: 900,
                      cursor: reviewActionLoading ? "not-allowed" : "pointer",
                    }}
                  >
                    {reviewActionLoading ? "Saving..." : "Approve deliverable"}
                  </button>

                  <button
                    disabled={reviewActionLoading}
                    onClick={() => {
                      setToastMessage("");
                      setShowDeliverableModal(false);
                      setShowRejectModal(true);
                      setExecutionState("rejected");
                    }}
                    style={{
                      border: "1px solid #fecaca",
                      background: "#fff",
                      color: "#dc2626",
                      borderRadius: 12,
                      padding: "12px 18px",
                      fontWeight: 900,
                      cursor: reviewActionLoading ? "not-allowed" : "pointer",
                    }}
                  >
                    Request revision
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      ) : null}

      {toastMessage && !showRejectModal ? (
        <div
          style={{
            position: "fixed",
            right: 24,
            bottom: 24,
            zIndex: 9998,
            background: "#0f172a",
            color: "#ffffff",
            borderRadius: 16,
            padding: "14px 18px",
            boxShadow: "0 18px 45px rgba(15,23,42,.22)",
            fontWeight: 800,
            maxWidth: 360,
          }}
        >
          {toastMessage}
        </div>
      ) : null}

      {showRejectModal ? (
        <div
          style={{
            position: "fixed",
            inset: 0,
            background: "rgba(15,23,42,.28)",
            zIndex: 9999,
            display: "flex",
            alignItems: "flex-start",
            justifyContent: "center",
            padding: "clamp(14px,2vw,24px)",
            overflow: "auto",
          }}
        >
          <div
            style={{
              width: 520,
              maxWidth: "100%",
              background: "#fff",
              borderRadius: 26,
              padding: 30,
              boxShadow: "0 30px 80px rgba(15,23,42,.20)",
            }}
          >
            <h2 style={{ margin: 0, fontSize: 26 }}>Provide rejection feedback</h2>
            <p style={{ color: "#64748b", lineHeight: 1.6 }}>
              Explain what needs to change so the agent can improve the next output.
            </p>

            <div style={{ display: "flex", gap: 8, flexWrap: "wrap", marginBottom: 16 }}>
              {["Not relevant", "Wrong tone", "Needs more detail", "Off brand", "Incorrect information"].map((reason) => (
                <button
                  key={reason}
                  onClick={() => setFeedbackReason(reason)}
                  style={{
                    border: feedbackReason === reason ? "1px solid #dc2626" : "1px solid #e5eaf2",
                    background: feedbackReason === reason ? "#fef2f2" : "#fff",
                    color: feedbackReason === reason ? "#dc2626" : "#334155",
                    borderRadius: 999,
                    padding: "8px 11px",
                    fontWeight: 800,
                    fontSize: 12,
                    cursor: "pointer",
                  }}
                >
                  {reason}
                </button>
              ))}
            </div>

            <textarea
              value={feedbackText}
              onChange={(e) => setFeedbackText(e.target.value)}
              placeholder="Describe what should be improved..."
              style={{
                width: "100%",
                minHeight: 140,
                borderRadius: 16,
                border: "1px solid #e5eaf2",
                padding: 16,
                fontSize: 13,
                resize: "none",
                boxSizing: "border-box",
                outline: "none",
                fontFamily: "inherit",
              }}
            />

            <div style={{ display: "flex", justifyContent: "flex-end", gap: 12, marginTop: 18, flexWrap: "wrap" }}>
              <button
                onClick={() => {
                  setShowRejectModal(false);
                  setExecutionState(liveDeliverable ? "completed" : "idle");
                }}
                style={{
                  border: "1px solid #e5eaf2",
                  background: "#fff",
                  borderRadius: 12,
                  padding: "12px 16px",
                  fontWeight: 800,
                  cursor: "pointer",
                }}
              >
                Cancel
              </button>

              <button
                disabled={reviewActionLoading}
                onClick={async () => {
                  const saved = await recordClientReviewAction("rejected", feedbackText, feedbackReason);
                  if (!saved) return;

                  setReviewStatus("rejected");
                  setShowRejectModal(false);
                  setToastMessage("Feedback submitted. The agent will use it to improve the next output.");
                }}
                style={{
                  border: "none",
                  background: reviewActionLoading ? "#fca5a5" : "#dc2626",
                  color: "#fff",
                  borderRadius: 12,
                  padding: "12px 18px",
                  fontWeight: 900,
                  cursor: reviewActionLoading ? "not-allowed" : "pointer",
                }}
              >
                {reviewActionLoading ? "Saving..." : "Submit feedback"}
              </button>
            </div>
          </div>
        </div>
      ) : null}
    </main>
  );
}

const cardStyle = {
  background: "#fff",
  borderRadius: 24,
  padding: "clamp(18px,2vw,24px)",
  boxShadow: "0 14px 34px rgba(15,23,42,.045)",
  border: "1px solid #edf1f6",
};

const labelStyle = {
  color: "#64748b",
  fontSize: 13.5,
  fontWeight: 700,
  marginBottom: 8,
};

const mutedText = {
  color: "#64748b",
  lineHeight: 1.55,
  fontSize: 13.5,
};

const cardTitle = {
  margin: 0,
  fontSize: 21,
  letterSpacing: -0.4,
};

function StepHeader({ number, title }: { number: string; title: string }) {
  return (
    <div
      style={{
        display: "flex",
        alignItems: "center",
        gap: 10,
        color: "#2563eb",
        fontSize: 12,
        fontWeight: 900,
        letterSpacing: 0.9,
        textTransform: "uppercase",
        marginBottom: 8,
      }}
    >
      <span
        style={{
          width: 28,
          height: 28,
          borderRadius: 999,
          background: "#eff6ff",
          color: "#2563eb",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        {number}
      </span>
      {title}
    </div>
  );
}
