"use client";

import React, { useEffect, useRef, useState } from "react";

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


const DEFAULT_AGENTS: string[] = [
  "product_research_agent",
  "competitor_intelligence_agent",
  "brand_strategy_agent",
  "store_builder_agent",
  "website_landing_apps_agent",
  "product_copywriting_agent",
  "ugc_creative_agent",
  "product_image_agent",
  "paid_ads_agent",
  "analytics_optimisation_agent",
  "email_reply_agent",
  "crm_ai_agent",
  "seo_agent",
  "social_media_manager_content_creator_agent",
  "influencer_collaboration_agent",
  "lead_generator_appointment_setter_agent",
  "sales_closer_agent",
  "receptionist_agent",
  "product_development_agent",
  "ecommerce_agent",
  "customer_support_agent",
  "business_growth_partnerships_agent",
];
const BACKEND_API_BASE = process.env.NEXT_PUBLIC_BACKEND_URL || process.env.NEXT_PUBLIC_API_BASE_URL || "https://api.trance-formation.com.au";

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

const ENTERPRISE_RESERVED_AGENT_IDS = new Set([
  "head_agent",
  "orchestration_agent",
  "multi_agent_orchestration_agent",
]);

const NON_ENTERPRISE_AGENT_CATALOGUE: string[] = Object.keys(AGENT_DISPLAY_NAMES).filter(
  (agentId) => !ENTERPRISE_RESERVED_AGENT_IDS.has(agentId)
);

const ENTERPRISE_PACKAGE_AGENTS: string[] = Object.keys(AGENT_DISPLAY_NAMES);

function getPackageAgentLimit(packageName: string) {
  const normalisedPackage = String(packageName || "").toLowerCase();

  if (normalisedPackage.includes("enterprise")) return null;
  if (normalisedPackage.includes("business")) return 10;
  if (normalisedPackage.includes("growth")) return 7;
  if (normalisedPackage.includes("starter")) return 3;

  return 3;
}

function getPackageAgentCatalogue(packageName: string, activeAgents?: string[]) {
  const normalisedPackage = String(packageName || "").toLowerCase();
  const allowedBaseCatalogue = normalisedPackage.includes("enterprise")
    ? ENTERPRISE_PACKAGE_AGENTS
    : NON_ENTERPRISE_AGENT_CATALOGUE;

  const cleanActiveAgents = (activeAgents || []).filter((agentId) =>
    allowedBaseCatalogue.includes(agentId)
  );

  if (cleanActiveAgents.length > 0) {
    return cleanActiveAgents;
  }

  return allowedBaseCatalogue;
}

function getPackageAgentLimitLabel(packageName: string, visibleCount: number) {
  const normalisedPackage = String(packageName || "").toLowerCase();
  const packageLimit = getPackageAgentLimit(packageName);

  if (normalisedPackage.includes("enterprise")) {
    return `${visibleCount}/${visibleCount} available`;
  }

  if (packageLimit === null) return `${visibleCount} available`;

  return `${visibleCount}/${packageLimit} active`;
}

function getAgentDisplayName(agentId: string) {
  return AGENT_DISPLAY_NAMES[agentId] ||
    agentId
      .replace(/_/g, " ")
      .replace(/\b\w/g, (letter) => letter.toUpperCase());
}


// client_portal_ux_pass3_layout_foundation
// client_portal_ux_pass4_two_column_layout
// client_portal_ux_pass5_premium_inputs
// client_portal_ux_pass6_agents_integrations
// client_portal_ux_pass7_compact_agents_integrations
// client_portal_ux_pass8_compact_workspace_pills
// client_portal_upper_sections_locked_pre_bottom_rebuild
// client_portal_ux_pass10_business_context_refine
// client_portal_aligned_upper_ui_locked
// client_portal_bottom_section_rebuild_locked
// client_portal_activity_feed_compact_locked
// client_portal_bottom_cards_aligned_locked
// client_portal_activity_premium_polish_locked
// client_portal_responsive_motion_locked
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
  const [businessProfile, setBusinessProfile] = useState<Record<string, string>>({});
  const [businessProfileSaved, setBusinessProfileSaved] = useState(false);
  const [toastMessage, setToastMessage] = useState("");
  const [showDeliverableModal, setShowDeliverableModal] = useState(false);
  const [selectedAssetIndex, setSelectedAssetIndex] = useState(0);

  const [integrations, setIntegrations] = useState<ClientIntegration[]>([]);
  const [executionTimeline, setExecutionTimeline] = useState<ExecutionTimelineEvent[]>([]);
  const [timelineLoading, setTimelineLoading] = useState(false);
  const [integrationMessage, setIntegrationMessage] = useState("");
  const [activeAccountPanel, setActiveAccountPanel] = useState("");
  const [darkModeEnabled, setDarkModeEnabled] = useState(false);
  const [showEnterpriseCatalogueModal, setShowEnterpriseCatalogueModal] = useState(false);
  const profileMenuRef = useRef<HTMLDetailsElement | null>(null);


  const shellStyle = {
    maxWidth: "none",
    width: "100%",
    padding: "clamp(18px,2.4vw,34px) clamp(16px,2.6vw,34px) 60px",
    boxSizing: "border-box" as const,
  };

  const primaryGridStyle = {
    display: "grid",
    gridTemplateColumns: "repeat(2, minmax(0, 1fr))",
    gap: 14,
    alignItems: "stretch",
    marginBottom: 20,
  };

  const secondaryGridStyle = {
    display: "grid",
    gridTemplateColumns: "repeat(2, minmax(0, 1fr))",
    gap: 14,
    alignItems: "start",
  };

  const deliverableCardGridStyle = {
    marginTop: 12,
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit,minmax(min(100%,280px),1fr))",
    gap: 14,
    padding: 16,
    borderRadius: 12,
    border: "1px solid #e5eaf2",
    background: "#fff",
  };

  
  const responsiveWorkspaceGridStyle = {
    display: "grid",
    gridTemplateColumns: "repeat(2, minmax(0, 1fr))",
    gap: 14,
    alignItems: "stretch",
    marginBottom: 20,
  };

  const responsiveSecondaryGridStyle = {
    display: "grid",
    gridTemplateColumns: "repeat(2, minmax(0, 1fr))",
    gap: 14,
    alignItems: "start",
  };


const modalContentGridStyle = {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit,minmax(min(100%,300px),1fr))",
    gap: 14,
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

  useEffect(() => {
    const syncAccountPanelFromHash = () => {
      const hash = window.location.hash.replace("#", "");
      if (["settings", "profile", "password-reset", "two-factor-authentication"].includes(hash)) {
        setActiveAccountPanel(hash);
      }
    };

    syncAccountPanelFromHash();
    window.addEventListener("hashchange", syncAccountPanelFromHash);
    return () => window.removeEventListener("hashchange", syncAccountPanelFromHash);
  }, []);

  const creditsRemaining = account?.credits_remaining ?? 0;
  const tenantId = account?.tenant_id || account?.client_id || "unknown_client";
  const accountPackage = account?.package_name || account?.package || "Starter";
  const visibleAgentCatalogue = getPackageAgentCatalogue(accountPackage, account?.active_agents);
  const visibleAgentCount = visibleAgentCatalogue.length;
  const packageAgentLimitLabel = getPackageAgentLimitLabel(accountPackage, visibleAgentCount);
  const isEnterprisePackage = String(accountPackage || "").toLowerCase().includes("enterprise");
  const inlineVisibleAgentCatalogue = isEnterprisePackage
    ? visibleAgentCatalogue.slice(0, 7)
    : visibleAgentCatalogue;
  const accountStatus = account?.status || "active";
  const activeAgentCount = visibleAgentCount;
  const accountAny = account as any;
  const businessProfileAny = businessProfile as any;
  const typedBusinessName = String(businessProfile.business_name || "").trim();
  const clientDisplayName =
    typedBusinessName ||
    businessProfileAny?.company_name ||
    businessProfileAny?.brand_name ||
    accountAny?.company_name ||
    accountAny?.business_name ||
    accountAny?.client_name ||
    accountAny?.contact_name ||
    accountAny?.full_name ||
    accountAny?.email ||
    "Client";
  const clientEmail = accountAny?.email || accountAny?.contact_email || "";
  const clientInitials =
    String(clientDisplayName)
      .split(/\s+/)
      .filter(Boolean)
      .slice(0, 2)
      .map((part) => part.charAt(0).toUpperCase())
      .join("") || "CL";
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
    if (account) {
      loadBusinessProfile();
      loadExecutionTimeline();
    }
  }, [account]);

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





  useEffect(() => {
    function handleProfileMenuOutsideClick(event: MouseEvent) {
      const menu = profileMenuRef.current;
      if (!menu) return;
      if (!menu.open) return;
      if (event.target instanceof Node && menu.contains(event.target)) return;
      menu.open = false;
    }

    document.addEventListener("mousedown", handleProfileMenuOutsideClick);
    return () => document.removeEventListener("mousedown", handleProfileMenuOutsideClick);
  }, []);


  async function loadBusinessProfile() {
    try {
      const response = await fetch("/api/client-business-profile", { cache: "no-store" });
      const data = await response.json();

      if (data?.success && data.profile) {
        setBusinessProfile(data.profile);
        setBusinessProfileSaved(Boolean(data.profile_saved));
      }
    } catch {
      setBusinessProfileSaved(false);
    }
  }

  async function saveBusinessProfile() {
    try {
      const cleanedProfile = {
        ...businessProfile,
        business_name: (businessProfile.business_name || "").trim(),
      };

      const response = await fetch("/api/client-business-profile", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ profile: cleanedProfile }),
      });

      const result = await response.json().catch(() => ({
        success: false,
        error: "invalid_json_response",
      }));

      if (!response.ok || !result?.success) {
        console.error("Business profile save failed", result);
        setToastMessage(
          result?.error
            ? `Business profile save failed: ${result.error}`
            : "Business profile could not be saved."
        );
        return;
      }

      const savedProfile =
        result?.profile && typeof result.profile === "object"
          ? result.profile
          : cleanedProfile;

      setBusinessProfile(savedProfile);
      setBusinessProfileSaved(true);
      localStorage.setItem("client_business_profile", JSON.stringify(savedProfile));
      setToastMessage("Business profile saved successfully.");
    } catch (error) {
      console.error("Business profile save runtime failure", error);
      setToastMessage("Business profile could not be saved.");
    }
  }

  async function loadExecutionTimeline() {
    try {
      setTimelineLoading(true);

      const eventTenantId = account?.tenant_id || account?.client_id || "unknown_client";

      const response = await fetch(
        `${BACKEND_API_BASE}/client/execution-events?tenant_id=${encodeURIComponent(eventTenantId)}&project_id=live_readiness_matrix&limit=20`,
        {
          cache: "no-store",
          headers: {
            "x-tenant-id": tenantId,
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
      const response = await fetch(`${BACKEND_API_BASE}/client/integrations`, { cache: "no-store", headers: { "x-tenant-id": tenantId, "x-actor-role": "customer" } });
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
      headers: { "Content-Type": "application/json", "x-tenant-id": tenantId, "x-actor-role": "customer" },
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
      headers: { "Content-Type": "application/json", "x-tenant-id": tenantId, "x-actor-role": "customer" },
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
      headers: { "Content-Type": "application/json", "x-tenant-id": tenantId, "x-actor-role": "customer" },
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
        background: darkModeEnabled ? "#0f172a" : "#f4f7fb",
        color: darkModeEnabled ? "#f8fafc" : "var(--color-dark)",
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
            gap: 14,
            marginBottom: 14,
            flexWrap: "wrap",
          }}
        >
          <div>
            <div
              style={{
                color: "var(--color-brand)",
                fontSize: 12.5,
                fontWeight: 760,
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
                color: "var(--color-muted)",
                lineHeight: 1.42,
                fontSize: 12.5,
              }}
            >
              Run selected AI agents, generate governed outputs, manage
              execution workflows, and produce commercial-grade deliverables.
            </p>
          </div>

          <div style={{ display: "flex", alignItems: "center", gap: 10, flexWrap: "wrap", justifyContent: "flex-end", position: "relative" }}>
            <button
              style={{
                border: "none",
                borderRadius: 12,
                padding: "8px 10px",
                background: "var(--color-dark)",
                color: "#fff",
                fontWeight: 700,
                cursor: "pointer",
                boxShadow: "0 10px 24px rgba(15,23,42,.12)",
              }}
            >
              + New execution
            </button>

            <div
              style={{
                background: "#fff",
                borderRadius: 16,
                padding: "8px 10px",
                border: "1px solid #e5eaf2",
                fontWeight: 800,
                boxShadow: "0 8px 22px rgba(15,23,42,.045)",
                textTransform: "uppercase",
              }}
            >
              <span
                style={{
                  color: accountStatus === "active" || accountStatus === "paid" || accountStatus === "trialing" ? "#22c55e" : "#ef4444",
                  marginRight: 8,
                }}
              >
                ●
              </span>
              {accountStatus === "active" || accountStatus === "paid" || accountStatus === "trialing" ? "ACTIVE" : "INACTIVE"}
            </div>

            <button
              aria-label="Notifications"
              style={{
                width: 34,
                height: 34,
                borderRadius: 16,
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
                  borderRadius: 16,
                  background: accountStatus === "active" || accountStatus === "paid" || accountStatus === "trialing" ? "#22c55e" : "#ef4444",
                  border: "2px solid #fff",
                }}
              />
            </button>

            <details ref={profileMenuRef} style={{ position: "relative", zIndex: 100 }}>
              <summary
                style={{
                  width: 34,
                  height: 34,
                  borderRadius: 16,
                  background: "var(--color-dark)",
                  color: "#fff",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  fontWeight: 760,
                  cursor: "pointer",
                  listStyle: "none",
                }}
              >
                {clientInitials}
              </summary>

              <div
                style={{
                  position: "absolute",
                  right: 0,
                  top: 54,
                  width: 280,
                  background: "#fff",
                  border: "1px solid #e5eaf2",
                  borderRadius: 18,
                  boxShadow: "0 24px 60px rgba(15,23,42,.18)",
                  padding: 14,
                  zIndex: 50,
                }}
              >
                <div style={{ display: "flex", gap: 12, alignItems: "center", paddingBottom: 12, borderBottom: "1px solid #edf1f6" }}>
                  <div style={{ width: 46, height: 46, borderRadius: 999, background: "var(--color-dark)", color: "#fff", display: "flex", alignItems: "center", justifyContent: "center", fontWeight: 800 }}>{clientInitials}</div>
                  <div>
                    <div style={{ fontWeight: 800, color: "var(--color-dark)" }}>{clientDisplayName}</div>
                    <div style={{ fontSize: 12, color: "var(--color-muted)" }}>{clientEmail || accountPackage}</div>
                    <div style={{ fontSize: 12, fontWeight: 700, marginTop: 4, color: "var(--color-muted)" }}>
                      <span style={{ color: accountStatus === "active" || accountStatus === "paid" || accountStatus === "trialing" ? "#22c55e" : "#ef4444", marginRight: 6 }}>●</span>
                      {accountStatus === "active" || accountStatus === "paid" || accountStatus === "trialing" ? "ACTIVE" : "INACTIVE"} · Paid plan
                    </div>
                  </div>
                </div>

                <button
                  onClick={() => {
                    setActiveAccountPanel("settings");
                    window.location.hash = "settings";
                    
                  }}
                  style={{ width: "100%", border: "none", background: "transparent", padding: "11px 8px", textAlign: "left", fontWeight: 700, cursor: "pointer", color: "var(--color-dark)" }}
                >
                  ⚙️ Settings
                </button>

                <button
                  onClick={() => {
                    setActiveAccountPanel("profile");
                    window.location.hash = "profile";
                    window.setTimeout(() => {
                      document.getElementById("account-centre-profile-panel")?.scrollIntoView({
                        behavior: "smooth",
                        block: "start",
                      });
                    }, 50);
                  }}
                  style={{ width: "100%", border: "none", background: "transparent", padding: "11px 8px", textAlign: "left", fontWeight: 700, cursor: "pointer", color: "var(--color-dark)" }}
                >
                  👤 Profile
                </button>

                <button
                  onClick={() => {
                    setActiveAccountPanel("password-reset");
                    window.location.hash = "password-reset";
                    
                  }}
                  style={{ width: "100%", border: "none", background: "transparent", padding: "11px 8px", textAlign: "left", fontWeight: 700, cursor: "pointer", color: "var(--color-dark)" }}
                >
                  🔐 Password reset
                </button>

                <button
                  onClick={() => {
                    setActiveAccountPanel("two-factor-authentication");
                    window.location.hash = "two-factor-authentication";
                    
                  }}
                  style={{ width: "100%", border: "none", background: "transparent", padding: "11px 8px", textAlign: "left", fontWeight: 700, cursor: "pointer", color: "var(--color-dark)" }}
                >
                  🛡️ 2FA
                </button>

                <button
                  onClick={() => {
                    setDarkModeEnabled((previous) => !previous);
                    setToastMessage(darkModeEnabled ? "Light mode enabled." : "Dark mode enabled.");
                  }}
                  style={{ width: "100%", border: "none", borderTop: "1px solid #edf1f6", background: "transparent", padding: "12px 8px", textAlign: "left", fontWeight: 800, cursor: "pointer", color: "var(--color-dark)" }}
                >
                  {darkModeEnabled ? "☀️ Switch to light mode" : "🌙 Toggle dark / light mode"}
                </button>

                <button
                  onClick={async () => {
                    try {
                      await fetch("/api/logout", { method: "POST" });
                    } finally {
                      window.location.href = "/login";
                    }
                  }}
                  style={{ width: "100%", border: "none", borderTop: "1px solid #edf1f6", background: "transparent", padding: "12px 8px", textAlign: "left", fontWeight: 800, cursor: "pointer", color: "#ef4444" }}
                >
                  🚪 Logout
                </button>
              </div>
            </details>
          </div>
        </header>

        <section
          style={{
            ...cardStyle,
            padding: "13px 16px",
            marginBottom: 18,
          }}
        >
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(5, minmax(0, 1fr))",
              gap: 0,
              alignItems: "center",
            }}
          >
            {[
              ["Workspace status", accountStatus === "active" ? "Ready for execution" : accountStatus, accountPackage, accountStatus === "active" || accountStatus === "paid" || accountStatus === "trialing" ? "#22c55e" : "#ef4444"],
              ["Approvals", reviewStatus === "pending" && liveDeliverable ? "1 pending" : "0 pending", liveDeliverable ? "Client review" : "No pending review", "#f59e0b"],
              ["Agents", String(activeAgentCount), activeAgentCount ? "Active in this workspace" : "No active agents", "var(--color-brand)"],
              ["Credits", String(creditsRemaining), "Available balance", "var(--color-brand)"],
            ].map(([label, value, note, dot], index) => (
              <div
                key={label}
                style={{
                  padding: "4px 22px",
                  borderLeft: index === 0 ? "none" : "1px solid #e5eaf2",
                  minHeight: 54,
                  display: "flex",
                  flexDirection: "column",
                  justifyContent: "center",
                }}
              >
                <div style={{ display: "flex", alignItems: "center", gap: 8, color: "var(--color-muted)", fontSize: 12, fontWeight: 850 }}>
                  <span style={{ width: 9, height: 9, borderRadius: 999, background: String(dot), boxShadow: "0 0 0 5px rgba(79,70,229,.08)" }} />
                  {label}
                </div>
                <div style={{ marginTop: 5, color: "var(--color-dark)", fontSize: 18, lineHeight: 1.1, fontWeight: 900 }}>
                  {value}
                </div>
                <div style={{ marginTop: 4, color: "var(--color-muted)", fontSize: 12 }}>
                  {note}
                </div>
              </div>
            ))}
          </div>
        </section>

        {activeAccountPanel ? (
          <section id="account-centre-profile-panel" style={{ ...cardStyle, padding: 18, marginBottom: 18, position: "relative", zIndex: 3 }}>
            <div style={{ display: "flex", justifyContent: "space-between", gap: 14, alignItems: "flex-start", flexWrap: "wrap" }}>
              <div>
                <div style={{ color: "var(--color-brand)", fontSize: 12, fontWeight: 900, letterSpacing: .6, textTransform: "uppercase", marginBottom: 6 }}>
                  Account centre
                </div>
                <h2 style={{ margin: 0, color: "var(--color-dark)", fontSize: 22, letterSpacing: -.4 }}>
                  {activeAccountPanel === "settings" ? "Settings" : activeAccountPanel === "profile" ? "Profile" : activeAccountPanel === "password-reset" ? "Password reset" : "Two-factor authentication"}
                </h2>
                <p style={{ margin: "7px 0 0", color: "var(--color-muted)", fontSize: 13, lineHeight: 1.45 }}>
                  Manage client account controls without leaving the workspace.
                </p>
              </div>

              <button
                type="button"
                onClick={() => {
                  setActiveAccountPanel("");
                  window.location.hash = "";
                }}
                style={{ border: "1px solid #e5eaf2", background: "#fff", borderRadius: 999, padding: "9px 13px", fontWeight: 850, cursor: "pointer", color: "var(--color-dark)" }}
              >
                Close
              </button>
            </div>


            <div style={{ marginTop: 14, display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(220px,1fr))", gap: 12 }}>
              {activeAccountPanel === "settings" ? (
                <>
                  <div style={{ border: "1px solid #edf1f6", borderRadius: 16, padding: 14, background: "#fff" }}>
                    <div style={{ fontSize: 11, color: "var(--color-muted)", fontWeight: 900, textTransform: "uppercase" }}>Theme</div>
                    <div style={{ marginTop: 6, color: "var(--color-dark)", fontWeight: 900 }}>Display mode</div>
                    <button
                      type="button"
                      onClick={() => document.documentElement.classList.toggle("dark")}
                      style={{ marginTop: 10, border: "1px solid rgba(79,70,229,.18)", background: "#fff", color: "#4f46e5", borderRadius: 12, padding: "9px 11px", fontWeight: 850, cursor: "pointer" }}
                    >
                      Toggle dark / light mode
                    </button>
                  </div>
                  <div style={{ border: "1px solid #edf1f6", borderRadius: 16, padding: 14, background: "#fff" }}>
                    <div style={{ fontSize: 11, color: "var(--color-muted)", fontWeight: 900, textTransform: "uppercase" }}>Workspace</div>
                    <div style={{ marginTop: 6, color: "var(--color-dark)", fontWeight: 900 }}>{accountPackage}</div>
                    <div style={{ marginTop: 5, color: "var(--color-muted)", fontSize: 12 }}>Status: {accountStatus}</div>
                  </div>
                </>
              ) : null}

              {activeAccountPanel === "profile" ? (
                <>
                  <div style={{ border: "1px solid #edf1f6", borderRadius: 16, padding: 14, background: "#fff" }}>
                    <div style={{ fontSize: 11, color: "var(--color-muted)", fontWeight: 900, textTransform: "uppercase" }}>Client</div>

                    <input
                      type="text"
                      value={businessProfile.business_name || ""}
                      onChange={(e) => {
                        setBusinessProfile((prev) => ({
                          ...prev,
                          business_name: e.target.value,
                        }));
                        setBusinessProfileSaved(false);
                      }}
                      placeholder="Type business name here"
                      style={{
                        marginTop: 8,
                        width: "100%",
                        height: 34,
                        border: "1.5px solid rgba(79,70,229,.35)",
                        borderRadius: 10,
                        padding: "9px 11px",
                        fontSize: 13,
                        color: "#0f172a",
                        background: "#fff",
                        outline: "none",
                        boxSizing: "border-box",
                        fontFamily: "inherit",
                      }}
                    />

                    <div style={{ marginTop: 8, color: "var(--color-muted)", fontSize: 12 }}>
                      {clientEmail || "No email shown"}
                    </div>

                    <button
                      type="button"
                      onClick={saveBusinessProfile}
                      style={{
                        marginTop: 12,
                        border: 0,
                        borderRadius: 12,
                        padding: "8px 10px",
                        background: "linear-gradient(135deg,#4f46e5,#4338ca)",
                        color: "#fff",
                        fontSize: 12.4,
                        fontWeight: 900,
                        cursor: "pointer",
                      }}
                    >
                      Save profile
                    </button>
                  </div>

                  <div style={{ border: "1px solid #edf1f6", borderRadius: 16, padding: 14, background: "#fff" }}>
                    <div style={{ fontSize: 11, color: "var(--color-muted)", fontWeight: 900, textTransform: "uppercase" }}>
                      Business profile
                    </div>

                    <div style={{ marginTop: 6, color: "var(--color-dark)", fontWeight: 900 }}>
                      {businessProfile.business_name || "Not saved yet"}
                    </div>

                    <div style={{ marginTop: 5, color: "var(--color-muted)", fontSize: 12 }}>
                      Edit the Business Profile Intelligence section below.
                    </div>
                  </div>
                </>
              ) : null}

              {activeAccountPanel === "password-reset" ? (
                <div style={{ border: "1px solid #edf1f6", borderRadius: 16, padding: 14, background: "#fff" }}>
                  <div style={{ fontSize: 11, color: "var(--color-muted)", fontWeight: 900, textTransform: "uppercase" }}>Password reset</div>
                  <div style={{ marginTop: 6, color: "var(--color-dark)", fontWeight: 900 }}>Secure reset request</div>
                  <p style={{ color: "var(--color-muted)", fontSize: 12, lineHeight: 1.45 }}>Use this panel to trigger the secure password reset flow once the backend route is connected.</p>
                  <button type="button" onClick={() => setToastMessage("Password reset request panel opened. Secure email flow is ready for backend connection.")} style={{ border: 0, background: "var(--color-dark)", color: "#fff", borderRadius: 12, padding: "8px 10px", fontWeight: 850, cursor: "pointer" }}>
                    Send reset link
                  </button>
                </div>
              ) : null}

              {activeAccountPanel === "two-factor-authentication" ? (
                <div style={{ border: "1px solid #edf1f6", borderRadius: 16, padding: 14, background: "#fff" }}>
                  <div style={{ fontSize: 11, color: "var(--color-muted)", fontWeight: 900, textTransform: "uppercase" }}>Two-factor authentication</div>
                  <div style={{ marginTop: 6, color: "var(--color-dark)", fontWeight: 900 }}>Extra account protection</div>
                  <p style={{ color: "var(--color-muted)", fontSize: 12, lineHeight: 1.45 }}>2FA setup panel is now functional in the workspace UI and ready for secure backend connection.</p>
                  <button type="button" onClick={() => setToastMessage("2FA setup panel opened. Secure setup flow is ready for backend connection.")} style={{ border: 0, background: "var(--color-dark)", color: "#fff", borderRadius: 12, padding: "8px 10px", fontWeight: 850, cursor: "pointer" }}>
                    Start 2FA setup
                  </button>
                </div>
              ) : null}
            </div>
          </section>
        ) : null}

        <section style={{ ...cardStyle, padding: 18, marginBottom: 18, position: "relative", zIndex: 2, overflow: "visible" }}>
          <div style={{ display: "flex", justifyContent: "space-between", gap: 16, alignItems: "flex-start", marginBottom: 18, flexWrap: "wrap" }}>
            <div>
              <div style={{ color: "var(--color-brand)", fontSize: 11.5, fontWeight: 850, letterSpacing: 1.4, textTransform: "uppercase", marginBottom: 7 }}>
                Business profile intelligence ✨
              </div>
              <h2 style={{ margin: 0, fontSize: 25, letterSpacing: -0.8 }}>
                Business context for tailored AI execution
              </h2>
              <p style={{ marginTop: 9, color: "var(--color-muted)", maxWidth: 760, lineHeight: 1.5 }}>
                Add business context once so every active AI agent can produce more accurate deliverables, assets, copy, positioning, and execution recommendations.
              </p>
            </div>

            <div style={{ display: "flex", gap: 10, alignItems: "center", flexWrap: "wrap" }}>
              <div style={{ background: "rgba(238,242,255,.95)", color: "var(--color-brand)", padding: "9px 13px", borderRadius: 12, fontWeight: 850, fontSize: 12 }}>
                ● {businessProfileSaved ? "Saved" : "Not saved yet"}
              </div>
              <button type="button" onClick={() => setToastMessage("Add business details, save the profile, then future AI executions will use this context.")} style={{ border: "1px solid rgba(79,70,229,.18)", background: "#fff", color: "#334155", padding: "9px 13px", borderRadius: 12, fontWeight: 850, fontSize: 12, cursor: "pointer" }}>
                ? How it works
              </button>
            </div>
          </div>

          <div style={{ marginBottom: 12, borderRadius: 12, border: "1px solid rgba(79,70,229,.12)", background: "rgba(238,242,255,.45)", padding: "8px 10px", color: "#334155", fontSize: 12.4, fontWeight: 750 }}>
            Start with <strong>Business name</strong>. This controls the client initials and account name shown in the top-right profile menu.
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "repeat(5, minmax(0, 1fr))", gap: 12, position: "relative", zIndex: 20, pointerEvents: "auto" }}>
            {[
              ["business_name", "◆", "Business name", "Type business name here", "input", "normal"],
              ["business_niche", "▦", "Business niche", "Describe your business niche, product category, and market position", "textarea", "normal"],
              ["products_services", "◇", "Products & services", "Main products, bundles, offers", "textarea", "normal"],
              ["target_audience", "♙", "Target audience", "Customer type, location, needs", "textarea", "normal"],
              ["competitors", "♕", "Competitors", "Competitor names, websites, market examples", "textarea", "normal"],
              ["offers", "⌑", "Offers", "Current promotions, bundles, guarantees", "textarea", "normal"],
              ["brand_voice", "◁", "Brand voice", "Premium, playful, clinical, bold, friendly", "textarea", "normal"],
              ["positioning", "◎", "Positioning", "Why customers should choose you", "textarea", "normal"],
              ["goals", "⚑", "Goals", "Sales, launches, retention, growth", "textarea", "normal"],
              ["notes", "◌", "Key differentiators", "What makes your business unique? Benefits, values, or competitive advantages.", "textarea", "normal"],
            ].map(([key, icon, label, placeholder, fieldType, size]) => (
              <div
                key={String(key)}
                style={{
                  gridColumn: "span 1",
                  borderRadius: 16,
                  border: "1px solid rgba(15,23,42,.08)",
                  background: "#fff",
                  padding: 12,
                  minHeight: 98,
                  boxShadow: "0 14px 38px rgba(15,23,42,.04)",
                  boxSizing: "border-box",
                  position: "relative",
                  zIndex: 21,
                  pointerEvents: "auto",
                }}
              >
                <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 9, pointerEvents: "none" }}>
                  <div style={{ width: 28, height: 28, borderRadius: 10, display: "grid", placeItems: "center", background: "rgba(238,242,255,.95)", color: "#4f46e5", fontWeight: 900, fontSize: 13, border: "1px solid rgba(79,70,229,.12)" }}>{icon}</div>
                  <div style={{ color: "#0f172a", fontSize: 12.5, fontWeight: 900 }}>
                    {label}{label === "Key differentiators" ? <span style={{ color: "#64748b", fontWeight: 700 }}> (optional)</span> : null}
                  </div>
                </div>

                {fieldType === "input" ? (
                  <input
                    type="text"
                    aria-label={String(label)}
                    placeholder={String(placeholder)}
                    value={businessProfile[String(key)] || ""}
                    onChange={(e) => {
                      const nextValue = e.target.value;
                      setBusinessProfile((prev) => ({ ...prev, [String(key)]: nextValue }));
                      setBusinessProfileSaved(false);
                    }}
                    autoComplete="organization"
                    style={{
                      width: "100%",
                      height: 34,
                      border: "1.5px solid rgba(79,70,229,.35)",
                      background: "#fff",
                      padding: "9px 11px",
                      borderRadius: 10,
                      fontSize: 13,
                      color: "#0f172a",
                      outline: "none",
                      boxSizing: "border-box",
                      fontFamily: "inherit",
                      marginTop: 8,
                      cursor: "text",
                      position: "relative",
                      zIndex: 50,
                      pointerEvents: "auto",
                      userSelect: "text",
                    }}
                  />
                ) : (
                  <textarea
                    aria-label={String(label)}
                    placeholder={String(placeholder)}
                    value={businessProfile[String(key)] || ""}
                    onChange={(e) => {
                      const nextValue = e.target.value;
                      setBusinessProfile((prev) => ({ ...prev, [String(key)]: nextValue }));
                      setBusinessProfileSaved(false);
                    }}
                    rows={2}
                    style={{
                      width: "100%",
                      resize: "vertical",
                      minHeight: 48,
                      border: "1px solid rgba(79,70,229,.18)",
                      background: "#fff",
                      padding: "9px 10px",
                      borderRadius: 10,
                      fontSize: 12.4,
                      lineHeight: 1.38,
                      color: "#0f172a",
                      outline: "none",
                      boxSizing: "border-box",
                      fontFamily: "inherit",
                      marginTop: 8,
                      cursor: "text",
                      position: "relative",
                      zIndex: 50,
                      pointerEvents: "auto",
                      userSelect: "text",
                    }}
                  />
                )}
              </div>
            ))}
          </div>

          <div style={{ marginTop: 14, borderRadius: 16, border: "1px solid rgba(79,70,229,.10)", background: "#fff", padding: 10, boxShadow: "0 10px 28px rgba(15,23,42,.04)", position: "relative", zIndex: 25 }}>
            <div style={{ display: "grid", gridTemplateColumns: "180px 180px 180px 1fr", gap: 10, alignItems: "center" }}>
              <button type="button" onClick={saveBusinessProfile} style={{ border: 0, borderRadius: 12, padding: "8px 10px", height: 34, background: "linear-gradient(135deg,#4f46e5,#4338ca)", color: "#fff", fontSize: 12.4, fontWeight: 900, cursor: "pointer" }}>▣ Save business profile</button>
              <button type="button" onClick={loadBusinessProfile} style={{ border: "1px solid rgba(79,70,229,.18)", borderRadius: 12, padding: "8px 10px", height: 34, background: "#fff", color: "#4f46e5", fontSize: 12.4, fontWeight: 900, cursor: "pointer" }}>↻ Reset to last save</button>
              <button type="button" onClick={() => setToastMessage("Preview will show how agents use this profile in the next workspace pass.")} style={{ border: "1px solid rgba(79,70,229,.18)", borderRadius: 12, padding: "8px 10px", height: 34, background: "#fff", color: "#4f46e5", fontSize: 12.4, fontWeight: 900, cursor: "pointer" }}>◉ Preview profile</button>
              <div style={{ borderLeft: "1px solid rgba(79,70,229,.12)", paddingLeft: 14, minHeight: 44, display: "flex", flexDirection: "column", justifyContent: "center" }}>
                <div style={{ fontWeight: 900, color: "#0f172a", fontSize: 12.5, marginBottom: 2 }}>One workspace. One business.</div>
                <div style={{ color: "#64748b", fontSize: 11.4, lineHeight: 1.3 }}>You can refine this profile, but changing business identity requires approval unless Enterprise multi-business access is enabled.</div>
                <div style={{ marginTop: 2, color: businessProfileSaved ? "#16a34a" : "#4f46e5", fontSize: 11.4, fontWeight: 900 }}>Status: {businessProfileSaved ? "Saved" : "Not saved yet"}</div>
              </div>
            </div>
            <div style={{ marginTop: 8, borderRadius: 11, border: "1px solid rgba(79,70,229,.10)", background: "rgba(238,242,255,.50)", padding: "7px 11px", color: "#475569", fontSize: 11.7, lineHeight: 1.35, fontWeight: 700 }}>
              ✨ Pro tip: The more specific you are, the better your AI agents can create content, copy, and strategies tailored to your business.
            </div>
          </div>
        </section>

        <section
        style={{
          ...cardStyle,
          padding: "14px 18px",
          marginBottom: 18,
        }}
      >
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "150px repeat(6, minmax(130px, 1fr)) 155px",
            gap: 10,
            alignItems: "center",
            width: "100%",
          }}
        >
          <div>
            <h2 style={{ margin: 0, fontSize: 16 }}>Integrations</h2>
            <p style={{ margin: "4px 0 0", color: "var(--color-muted)", fontSize: 13 }}>
              Connected systems
            </p>
          </div>

          {[
            ["E", "Email"],
            ["C", "CRM"],
            ["E", "Ecommerce Store"],
            ["W", "Website / CMS"],
            ["C", "Calendar"],
            ["S", "SMS / Phone"],
          ].map(([letter, label]) => (
            <button
              key={label}
              type="button"
              style={{
                border: "1px solid #e5eaf2",
                borderRadius: 12,
                background: "#fff",
                padding: "8px 10px",
                display: "flex",
                alignItems: "center",
                gap: 8,
                minHeight: 48,
                cursor: "pointer",
                boxShadow: "0 8px 20px rgba(15,23,42,.04)",
                whiteSpace: "nowrap",
                overflow: "hidden",
              }}
            >
              <span
                style={{
                  width: 28,
                  height: 28,
                  borderRadius: 9,
                  background: "#eef2f7",
                  color: "#64748b",
                  display: "inline-flex",
                  alignItems: "center",
                  justifyContent: "center",
                  fontWeight: 900,
                  flex: "0 0 auto",
                }}
              >
                {letter}
              </span>
              <span style={{ minWidth: 0, textAlign: "left", lineHeight: 1.1 }}>
                <span
                  style={{
                    display: "block",
                    fontWeight: 900,
                    color: "var(--color-dark)",
                    fontSize: 13,
                    overflow: "hidden",
                    textOverflow: "ellipsis",
                  }}
                >
                  {label}
                </span>
                <span style={{ display: "block", color: "var(--color-muted)", fontSize: 12, fontWeight: 800, marginTop: 3 }}>
                  Connect
                </span>
              </span>
            </button>
          ))}

          <button
            type="button"
            style={{
              border: "1px solid #d8dcff",
              borderRadius: 12,
              background: "#fff",
              color: "var(--color-primary)",
              padding: "8px 12px",
              minHeight: 48,
              fontWeight: 900,
              cursor: "pointer",
              whiteSpace: "nowrap",
            }}
          >
            + Add integration
          </button>
        </div>
      </section>


        

        <section style={responsiveWorkspaceGridStyle}>
          <div style={{ ...cardStyle, minHeight: 430 }}>
            <StepHeader number="01" title="Run AI Agent" />
            <h3 style={cardTitle}>Select agents and launch governed execution.</h3>
            <p style={{ ...mutedText, margin: "6px 0 0" }}>
              Configure your task and run using your saved business profile.
            </p>

            <div style={{ display: "grid", gridTemplateColumns: "260px minmax(0,1fr)", gap: 16, marginTop: 18 }}>
              <div>
                <div style={{ ...labelStyle, display: "flex", alignItems: "center", justifyContent: "space-between", gap: 8 }}>
                  <span>Active agents</span>
                  <span style={{ color: "var(--color-brand)", fontWeight: 900 }}>{packageAgentLimitLabel}</span>
                </div>
                <div style={{ display: "grid", gap: 7, maxHeight: visibleAgentCount <= 3 ? "none" : 268, overflowY: visibleAgentCount <= 3 ? "visible" : "auto", paddingRight: visibleAgentCount <= 3 ? 0 : 4 }}>
                  {inlineVisibleAgentCatalogue.map((agent) => {
                    const active = selectedAgents.includes(agent);
                    const agentName = getAgentDisplayName(agent);
                    const agentIcon =
                      agentName.toLowerCase().includes("research") ? "⌕" :
                      agentName.toLowerCase().includes("copy") ? "✎" :
                      agentName.toLowerCase().includes("ugc") ? "▣" :
                      agentName.toLowerCase().includes("image") ? "▧" :
                      agentName.toLowerCase().includes("crm") ? "♟" :
                      agentName.toLowerCase().includes("email") ? "✉" :
                      agentName.toLowerCase().includes("analytics") ? "↗" :
                      agentName.toLowerCase().includes("influencer") ? "★" :
                      "AI";

                    return (
                      <button
                        key={agentName}
                        onClick={() => toggleAgent(agent)}
                        style={{
                          border: active ? "1px solid rgba(37, 99, 235, 0.34)" : "1px solid rgba(15, 23, 42, 0.10)",
                          background: active ? "linear-gradient(135deg,#eff6ff,#ffffff)" : "#ffffff",
                          color: active ? "var(--color-brand)" : "var(--color-dark)",
                          padding: "8px 10px",
                          borderRadius: 13,
                          cursor: "pointer",
                          textAlign: "left",
                          fontSize: 11.8,
                          fontWeight: 760,
                          transition: "all 0.18s ease",
                          boxShadow: active ? "0 10px 30px rgba(37,99,235,0.10)" : "0 1px 2px rgba(15,23,42,0.03)",
                          display: "grid",
                          gridTemplateColumns: "18px 28px minmax(0,1fr)",
                          gap: 8,
                          alignItems: "center",
                        }}
                      >
                        <span
                          style={{
                            width: 14,
                            height: 14,
                            borderRadius: 999,
                            border: active ? "none" : "1.5px solid rgba(79,70,229,.45)",
                            background: active ? "var(--color-brand)" : "#ffffff",
                            color: "#fff",
                            display: "inline-flex",
                            alignItems: "center",
                            justifyContent: "center",
                            fontSize: 9,
                            fontWeight: 900,
                          }}
                        >
                          {active ? "✓" : ""}
                        </span>
                        <span
                          style={{
                            width: 26,
                            height: 26,
                            borderRadius: 9,
                            background: active ? "#eef2ff" : "#f8fafc",
                            color: "var(--color-brand)",
                            display: "inline-flex",
                            alignItems: "center",
                            justifyContent: "center",
                            fontSize: 13,
                            fontWeight: 900,
                          }}
                        >
                          {agentIcon}
                        </span>
                        <span style={{ overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                          {agentName}
                        </span>
                      </button>
                    );
                  })}
                </div>

                {isEnterprisePackage ? (
                  <button
                    type="button"
                    onClick={() => setShowEnterpriseCatalogueModal(true)}
                    style={{
                      marginTop: 10,
                      width: "100%",
                      border: "1px solid #d8dcff",
                      background: "#fff",
                      color: "var(--color-brand)",
                      borderRadius: 12,
                      padding: "9px 10px",
                      fontSize: 11.8,
                      fontWeight: 900,
                      cursor: "pointer",
                      boxShadow: "0 8px 20px rgba(15,23,42,.04)",
                    }}
                  >
                    View full catalogue →
                  </button>
                ) : null}
              </div>

              <div>
                <div style={labelStyle}>Task</div>
                <textarea
                  defaultValue="Create a client-specific client deliverable using the saved business profile, selected active agents, current offer, target audience, goals, and execution requirements."
                  style={{
                    width: "100%",
                    minHeight: 178,
                    resize: "none",
                    borderRadius: 16,
                    border: "1px solid #dbe3ee",
                    background: "#fff",
                    padding: 14,
                    fontSize: 11.8,
                    lineHeight: 1.46,
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
                        headers: { "Content-Type": "application/json", "x-tenant-id": tenantId, "x-actor-role": "customer" },
                        credentials: "include",
                        body: JSON.stringify({
                          selected_agents: selectedAgents,
                          task: "Create a client-specific client deliverable using the saved business profile, selected active agents, current offer, target audience, goals, and execution requirements.",
                          business_profile: {
                            niche: businessProfile.business_niche || "Saved client business profile",
                            target_audience: businessProfile.target_audience || "Saved target audience and customer context",
                            positioning: businessProfile.notes || "Client-specific commercial positioning and execution requirements",
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
                    borderRadius: 16,
                    background: executionState === "running" ? "linear-gradient(135deg,var(--color-muted),var(--color-mid))" : "linear-gradient(135deg,var(--color-brand),#06b6d4)",
                    color: "#fff",
                    padding: "13px 16px",
                    fontWeight: 760,
                    cursor: "pointer",
                    boxShadow: "0 12px 26px rgba(37,99,235,.18)",
                  }}
                >
                  {executionState === "running" ? "Generating..." : "✨ Run Agent"}
                </button>
              </div>
            </div>

            <div style={{ marginTop: 12, color: "var(--color-muted)", fontSize: 12 }}>
              ⓘ Runs use your saved business profile.
            </div>
          </div>

          <div style={{ ...cardStyle, minHeight: 430 }}>
            <StepHeader number="02" title="Live execution flow" />
            <h3 style={cardTitle}>Execution pipeline</h3>
            <p style={mutedText}>
              Every AI deliverable flows through approval, optimisation, workflow validation,
              and governed execution before deployment.
            </p>

            <div style={{ display: "grid", gap: 8, marginTop: 12 }}>
              {[
                ["Execution requested", executionState === "idle" ? "Waiting" : "Started", liveDeliverable?.created_at || "Live"],
                ["Business profile applied", "Context loaded", "Live"],
                ["Deliverable status", executionState === "completed" ? "Ready" : "Pending", liveDeliverable?.created_at || "Live"],
                ["Client review", reviewStatus === "approved" ? "Approved" : reviewStatus === "rejected" ? "Revision requested" : "Pending", reviewStatus === "approved" ? "Complete" : "Open"],
                ["Execution ready", "Next", "—"],
              ].map(([title, status, time], index) => (
                <div key={title} style={{ display: "grid", gridTemplateColumns: "30px minmax(0,1fr) auto", gap: 9, alignItems: "center" }}>
                  <div
                    style={{
                      width: 26,
                      height: 26,
                      minWidth: 26,
                      minHeight: 26,
                      borderRadius: "999px",
                      background: index === 4 ? "#06b6d4" : "var(--color-brand)",
                      color: "#fff",
                      display: "inline-flex",
                      alignItems: "center",
                      justifyContent: "center",
                      fontSize: 11,
                      fontWeight: 900,
                    }}
                  >
                    {index + 1}
                  </div>

                  <div
                    style={{
                      border: "1px solid #e5eaf2",
                      borderRadius: 12,
                      background: "#fff",
                      padding: "8px 10px",
                      boxShadow: "0 8px 20px rgba(15,23,42,.04)",
                    }}
                  >
                    <div style={{ fontWeight: 900, color: "var(--color-dark)", fontSize: 12 }}>{title}</div>
                    <div style={{ color: "var(--color-muted)", fontSize: 11.5, fontWeight: 800, marginTop: 2 }}>{status}</div>
                  </div>

                  <div style={{ color: "var(--color-muted)", fontSize: 11.5, fontWeight: 800, whiteSpace: "nowrap" }}>{time}</div>
                </div>
              ))}

              <div
                style={{
                  border: "1px solid #dbeafe",
                  borderRadius: 14,
                  background: "linear-gradient(135deg,#eff6ff,#ffffff)",
                  padding: "9px 10px",
                  display: "grid",
                  gridTemplateColumns: "26px 1fr",
                  gap: 9,
                  alignItems: "center",
                }}
              >
                <div
                  style={{
                    width: 26,
                    height: 26,
                    borderRadius: 9,
                    background: "#ffffff",
                    color: "var(--color-brand)",
                    display: "inline-flex",
                    alignItems: "center",
                    justifyContent: "center",
                    fontWeight: 900,
                    boxShadow: "0 4px 12px rgba(37,99,235,.08)",
                  }}
                >
                  ✦
                </div>
                <div>
                  <div style={{ fontSize: 12, fontWeight: 900, color: "var(--color-dark)" }}>
                    Governed execution, every time.
                  </div>
                  <div style={{ marginTop: 2, fontSize: 11.5, fontWeight: 700, color: "var(--color-muted)", lineHeight: 1.35 }}>
                    Tracked, logged, quality-checked, and approval-routed.
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>


        <section style={{ ...responsiveSecondaryGridStyle, alignItems: "stretch" }}>
          <div style={{ ...cardStyle, height: 560, overflow: "hidden" }}>
            <StepHeader number="05" title="Activity" />
            <h3 style={cardTitle}>Activity</h3>
            <p style={{ color: "var(--color-brand)", fontWeight: 700, fontSize: 13 }}>Latest governed activity</p>

            <div style={{ display: "grid", gap: 10, marginTop: 10, maxHeight: 430, overflowY: "auto", paddingRight: 4 }}>
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
                  }]).slice(0, 2).map((event) => {
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
                  ? { bg: "#fff7ed", border: "#fed7aa", text: "var(--color-amber)", label: "Needs attention" }
                  : isApprovalRequired
                    ? { bg: "#fffbeb", border: "#fde68a", text: "#ca8a04", label: "Approval gated" }
                    : { bg: "#f0fdf4", border: "#bbf7d0", text: "var(--color-teal)", label: "Governed ready" };

                return (
                  <div
                    key={event.event_id || `${event.agent_id}-${event.event_type}`}
                    style={{
                      border: `1px solid ${statusTone.border}`,
                      borderRadius: 16,
                      padding: 20,
                      background: "rgba(255, 255, 255, 0.94)",
                      boxShadow: "0 20px 55px rgba(15,23,42,0.06)",
                      transition: "transform 0.18s ease, box-shadow 0.18s ease",
                    }}
                  >
                    <div style={{ display: "flex", justifyContent: "space-between", gap: 10, flexWrap: "wrap", alignItems: "flex-start" }}>
                      <div>
                        <div style={{ color: "var(--color-muted)", fontSize: 11.8, fontWeight: 700 }}>{time}</div>
                        <div style={{ fontWeight: 800, color: "var(--color-dark)", fontSize: 16, marginTop: 5 }}>
                          {event.title || event.event_type || "Execution event"}
                        </div>
                        <div style={{ color: "var(--color-mid)", fontSize: 11.8, lineHeight: 1.45, marginTop: 6 }}>
                          {event.summary || "Governed execution event recorded by the platform ledger."}
                        </div>
                      </div>

                      <div style={{ textAlign: "right", color: "var(--color-muted)", fontSize: 13, fontWeight: 850 }}>
                        <div>{agentName}</div>
                        <div style={{ marginTop: 4, display: "inline-flex", background: statusTone.bg, color: statusTone.text, border: `1px solid ${statusTone.border}`, borderRadius: 16, padding: "3px 6px", fontSize: 10, fontWeight: 800 }}>
                          {statusTone.label}
                        </div>
                      </div>
                    </div>

                    <div style={{ display: "flex", flexWrap: "wrap", gap: 8, marginTop: 10 }}>
                      <span style={{ background: "linear-gradient(135deg, rgba(239, 246, 255, 0.86), rgba(255, 255, 255, 0.96))", color: "var(--color-brand)", border: "1px solid rgba(37, 99, 235, 0.14)", borderRadius: 16, padding: "7px 10px", fontWeight: 850, fontSize: 12 }}>
                        {event.execution_action || event.action_type || "Tracked action"}
                      </span>
                      <span style={{ background: "#f0fdf4", color: "var(--color-teal)", border: "1px solid #dcfce7", borderRadius: 16, padding: "7px 10px", fontWeight: 850, fontSize: 12 }}>
                        Quality: {qualityStatus}
                      </span>
                      <span style={{ background: "#fff7ed", color: "var(--color-amber)", border: "1px solid #fed7aa", borderRadius: 16, padding: "7px 10px", fontWeight: 850, fontSize: 12 }}>
                        Approval: {approvalStatus}
                      </span>
                      <span style={{ background: statusTone.bg, color: statusTone.text, border: `1px solid ${statusTone.border}`, borderRadius: 16, padding: "7px 10px", fontWeight: 850, fontSize: 12 }}>
                        Execution: {executionStatus}
                      </span>
                      <span style={{ background: "var(--color-bg-light)", color: "#334155", border: "1px solid rgba(15, 23, 42, 0.08)", 
                    boxShadow: "0 18px 55px rgba(15, 23, 42, 0.06)",
                    backdropFilter: "blur(10px)",
                    WebkitBackdropFilter: "blur(10px)",
                    borderRadius: 16, padding: "7px 10px", fontWeight: 850, fontSize: 12 }}>
                        Stage: {event.workflow_stage || "workflow"}
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          <div style={{ ...cardStyle, height: 560, overflow: "hidden" }}>
            <div style={{ display: "flex", justifyContent: "space-between", gap: 16, flexWrap: "wrap" }}>
              <div>
                <StepHeader number="06" title="Execution output viewer" />
                <h3 style={cardTitle}>Client deliverables</h3>
              </div>
              <div
                style={{
                  background: reviewStatus === "rejected" ? "#fee2e2" : "#dcfce7",
                  color: reviewStatus === "rejected" ? "var(--color-red)" : "var(--color-teal)",
                  padding: "8px 12px",
                  borderRadius: 16,
                  fontWeight: 760,
                  fontSize: 11.8,
                  height: "fit-content",
                }}
              >
                {reviewStatus === "approved" ? "Approve ✓d" : reviewStatus === "rejected" ? "Revision requested" : "Completed"}
              </div>
            </div>

            <div style={deliverableCardGridStyle}>
              <div
                style={{
                  minHeight: 150,
                  borderRadius: 16,
                  background: "var(--color-bg-light)",
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
                      padding: 16,
                      background: "linear-gradient(180deg,#ffffff 0%,var(--color-bg-light) 100%)",
                      color: "var(--color-muted)",
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
                              width: 34,
                              height: 34,
                              borderRadius: 16,
                              background: "linear-gradient(135deg, rgba(239, 246, 255, 0.86), rgba(255, 255, 255, 0.96))",
                              display: "flex",
                              alignItems: "center",
                              justifyContent: "center",
                              color: "var(--color-brand)",
                              fontSize: 18,
                              fontWeight: 760,
                              flex: "0 0 auto",
                            }}
                          >
                            ✦
                          </div>

                          <div>
                            <div
                              style={{
                                color: "var(--color-dark)",
                                fontWeight: 760,
                                fontSize: 13,
                                marginBottom: 3,
                              }}
                            >
                              Media preview unavailable
                            </div>

                            <div
                              style={{
                                fontSize: 11,
                                color: "var(--color-muted)",
                              }}
                            >
                              Waiting for uploaded or generated assets
                            </div>
                          </div>
                        </div>

                        <div
                          style={{
                            border: "1px solid rgba(15, 23, 42, 0.08)",
                            
                    boxShadow: "0 18px 55px rgba(15, 23, 42, 0.06)",
                    backdropFilter: "blur(10px)",
                    WebkitBackdropFilter: "blur(10px)",
                    borderRadius: 16,
                            padding: "3px 6px",
                            fontSize: 11,
                            fontWeight: 700,
                            background: "#fff",
                            color: "var(--color-mid)",
                            
                          }}
                        >
                          Pending media
                        </div>
                      </div>

                      <div
                        style={{
                          borderRadius: 16,
                          border: "1px dashed #dbe4ee",
                          background: "linear-gradient(135deg,var(--color-bg-light) 0%,#f1f5f9 100%)",
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
                            padding: 16,
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
                              color: "var(--color-dark)",
                              fontWeight: 700,
                              fontSize: 13,
                              marginBottom: 8,
                            }}
                          >
                            No live asset attached
                          </div>

                          <div
                            style={{
                              fontSize: 10,
                              lineHeight: 1.6,
                              color: "var(--color-muted)",
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
                      borderRadius: 16,
                      padding: "7px 10px",
                      fontSize: 11,
                      fontWeight: 760,
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
                      borderRadius: 16,
                      padding: "7px 10px",
                      fontSize: 11,
                      fontWeight: 760,
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
                  <div style={{ color: "var(--color-muted)", fontSize: 12 }}>
                    {liveDeliverable?.created_at || "Ready for review"}
                  </div>
                </div>

                <p style={{ color: "var(--color-mid)", lineHeight: 1.6 }}>
                  {liveDeliverable?.summary ||
                    "Client-specific deliverable generated from the latest execution, business profile, selected agents, and review requirements."}
                </p>

                <div style={{ display: "flex", gap: 10, flexWrap: "wrap", marginBottom: 16 }}>
                  {(liveDeliverable?.tags || ["Deliverable", "Assets", "Execution", "Workflow"]).map((tag: string) => (
                    <span
                      key={tag}
                      style={{
                        border: "1px solid #e5eaf2",
                        borderRadius: 16,
                        padding: "8px 11px",
                        fontSize: 11.8,
                        fontWeight: 700,
                      }}
                    >
                      {tag}
                    </span>
                  ))}
                </div>

                {attachedAssets.length > 1 ? (
                  <div style={{ marginBottom: 16 }}>
                    <div style={{ color: "var(--color-muted)", fontSize: 11.8, fontWeight: 700, marginBottom: 8 }}>
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
                              border: selected ? "1px solid var(--color-brand)" : "1px solid #e5eaf2",
                              borderRadius: 16,
                              padding: 10,
                              textAlign: "left",
                              fontSize: 11,
                              fontWeight: 700,
                              color: selected ? "var(--color-brand)" : "var(--color-mid)",
                              background: selected ? "#eff6ff" : "var(--color-bg-light)",
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
                      border: "1px solid rgba(37, 99, 235, 0.14)",
                      background: "linear-gradient(135deg, rgba(239, 246, 255, 0.86), rgba(255, 255, 255, 0.96))",
                      color: "var(--color-brand)",
                      borderRadius: 16,
                      padding: "8px 11px",
                      fontWeight: 760,
                      fontSize: 11.8,
                      cursor: "pointer",
                    }}
                  >
                    Preview
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
                      borderRadius: 16,
                      padding: "8px 11px",
                      fontWeight: 760,
                      fontSize: 11.8,
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
                      borderRadius: 16,
                      padding: "8px 11px",
                      fontWeight: 760,
                      fontSize: 11.8,
                      cursor: "pointer",
                    }}
                  >
                    Copy summary
                  </button>
                </div>

                <div style={{ display: "flex", gap: 16, flexWrap: "wrap", alignItems: "center" }}>
                  <button
                    onClick={() => setShowDeliverableModal(true)}
                    style={{
                      border: "1px solid rgba(37, 99, 235, 0.14)",
                      background: "linear-gradient(135deg, rgba(239, 246, 255, 0.86), rgba(255, 255, 255, 0.96))",
                      color: "var(--color-brand)",
                      borderRadius: 16,
                      padding: "8px 12px",
                      fontWeight: 760,
                      cursor: "pointer",
                    }}
                  >
                    Open deliverable
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
                      background: reviewActionLoading ? "#86efac" : "var(--color-teal)",
                      color: "#fff",
                      borderRadius: 16,
                      padding: "8px 12px",
                      fontWeight: 760,
                      cursor: reviewActionLoading ? "not-allowed" : "pointer",
                    }}
                  >
                    {reviewActionLoading ? "Saving..." : "👍 Approve ✓"}
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
                      color: "var(--color-red)",
                      borderRadius: 16,
                      padding: "8px 12px",
                      fontWeight: 760,
                      cursor: reviewActionLoading ? "not-allowed" : "pointer",
                      transition: "transform 0.16s ease, border-color 0.16s ease",
                    }}
                  >
                    👎 Request changes
                  </button>
                </div>

                <div
                  style={{
                    marginTop: 10,
                    paddingTop: 14,
                    borderTop: "1px solid #eef2f7",
                    color: "#94a3b8",
                    fontSize: 10,
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
              borderRadius: 12,
              boxShadow: "0 30px 90px rgba(15,23,42,.24)",
              border: "1px solid #e5eaf2",
            }}
          >
            <div
              style={{
                padding: "clamp(16px,2vw,22px)",
                borderBottom: "1px solid #eef2f7",
                display: "flex",
                justifyContent: "space-between",
                gap: 14,
                alignItems: "flex-start",
                flexWrap: "wrap",
              }}
            >
              <div>
                <div
                  style={{
                    color: "var(--color-brand)",
                    fontSize: 11.8,
                    fontWeight: 760,
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
                    fontSize: "clamp(20px,2vw,24px)",
                    letterSpacing: -0.8,
                    lineHeight: 1.15,
                  }}
                >
                  {liveDeliverable?.title || "Client deliverable"}
                </h2>

                <div style={{ marginTop: 4, color: "var(--color-muted)", fontSize: 13 }}>
                  {liveDeliverable?.created_at || "Ready for review"}
                </div>

                <div style={{ display: "flex", gap: 8, flexWrap: "wrap", marginTop: 10 }}>
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
                      borderRadius: 16,
                      padding: "3px 6px",
                      fontWeight: 760,
                      fontSize: 11.8,
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
                      borderRadius: 16,
                      padding: "3px 6px",
                      fontWeight: 760,
                      fontSize: 11.8,
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
                  width: 34,
                  height: 34,
                  borderRadius: 16,
                  border: "1px solid #e5eaf2",
                  background: "#fff",
                  cursor: "pointer",
                  fontWeight: 760,
                  color: "var(--color-dark)",
                }}
              >
                ×
              </button>
            </div>

            <div style={modalContentGridStyle}>
              <div
                style={{
                  borderRadius: 12,
                  border: "1px solid #e5eaf2",
                  background: "var(--color-bg-light)",
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
                      background: "linear-gradient(135deg,#ffffff,var(--color-bg-light))",
                    }}
                  >
                    <div style={{ fontSize: 38, marginBottom: 8 }}>🖼️</div>
                    <div style={{ color: "var(--color-dark)", fontWeight: 760, fontSize: 16, marginBottom: 8 }}>
                      No live asset attached
                    </div>
                    <div style={{ color: "var(--color-muted)", fontSize: 13, lineHeight: 1.65, maxWidth: 280 }}>
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
                        border: "1px solid rgba(37, 99, 235, 0.14)",
                        background: "linear-gradient(135deg, rgba(239, 246, 255, 0.86), rgba(255, 255, 255, 0.96))",
                        color: "var(--color-brand)",
                        borderRadius: 16,
                        padding: "8px 11px",
                        fontSize: 11.8,
                        fontWeight: 760,
                      }}
                    >
                      {tag}
                    </span>
                  ))}
                </div>

                <section
                  style={{
                    border: "1px solid #eef2f7",
                    borderRadius: 16,
                    padding: 20,
                    marginBottom: 16,
                    background: "#fff",
                  }}
                >
                  <h3 style={{ margin: "0 0 10px", fontSize: 17 }}>Executive summary</h3>
                  <p style={{ margin: 0, color: "var(--color-mid)", lineHeight: 1.75, fontSize: 14.5 }}>
                    {liveDeliverable?.summary ||
                      "Client-specific deliverable generated from the latest execution, business profile, selected agents, and review requirements."}
                  </p>
                </section>

                <section
                  style={{
                    border: "1px solid #eef2f7",
                    borderRadius: 16,
                    padding: 20,
                    marginBottom: 16,
                    background: "#fbfdff",
                  }}
                >
                  <h3 style={{ margin: "0 0 12px", fontSize: 17 }}>Review checklist</h3>
                  <div style={{ display: "grid", gap: 7 }}>
                    {[
                      "Confirm brand fit and tone",
                      "Confirm offer and deliverable direction",
                      "Check media or asset requirements",
                      "Approve ✓ for execution or request revision",
                    ].map((item) => (
                      <div
                        key={item}
                        style={{
                          display: "flex",
                          alignItems: "center",
                          gap: 10,
                          color: "var(--color-mid)",
                          fontSize: 11.8,
                        }}
                      >
                        <span
                          style={{
                            width: 22,
                            height: 22,
                            borderRadius: 16,
                            background: "linear-gradient(135deg, rgba(239, 246, 255, 0.86), rgba(255, 255, 255, 0.96))",
                            color: "var(--color-brand)",
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center",
                            fontSize: 11.8,
                            fontWeight: 760,
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
                      borderRadius: 16,
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
                              border: selected ? "1px solid var(--color-brand)" : "1px solid #e5eaf2",
                              borderRadius: 16,
                              padding: 20,
                              textAlign: "left",
                              fontSize: 11.8,
                              fontWeight: 700,
                              color: selected ? "var(--color-brand)" : "var(--color-mid)",
                              background: selected ? "#eff6ff" : "var(--color-bg-light)",
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

                <div style={{ display: "flex", gap: 16, flexWrap: "wrap", justifyContent: "flex-end", alignItems: "center" }}>
                  <button
                    onClick={() => setShowDeliverableModal(false)}
                    style={{
                      border: "1px solid #e5eaf2",
                      background: "#fff",
                      color: "#334155",
                      borderRadius: 16,
                      padding: "8px 10px",
                      fontWeight: 760,
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
                      background: reviewActionLoading ? "#86efac" : "var(--color-teal)",
                      color: "#fff",
                      borderRadius: 16,
                      padding: "8px 12px",
                      fontWeight: 760,
                      cursor: reviewActionLoading ? "not-allowed" : "pointer",
                    }}
                  >
                    {reviewActionLoading ? "Saving..." : "Approve ✓ deliverable"}
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
                      color: "var(--color-red)",
                      borderRadius: 16,
                      padding: "8px 12px",
                      fontWeight: 760,
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
            background: "var(--color-dark)",
            color: "#ffffff",
            borderRadius: 16,
            padding: "14px 18px",
            boxShadow: "0 18px 45px rgba(15,23,42,.22)",
            fontWeight: 700,
            maxWidth: 360,
          }}
        >
          {toastMessage}
        </div>
      ) : null}


      {showEnterpriseCatalogueModal ? (
        <div
          role="dialog"
          aria-modal="true"
          aria-label="Full enterprise agent catalogue"
          style={{
            position: "fixed",
            inset: 0,
            zIndex: 80,
            background: "rgba(15,23,42,0.42)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            padding: 18,
          }}
          onClick={() => setShowEnterpriseCatalogueModal(false)}
        >
          <div
            onClick={(event) => event.stopPropagation()}
            style={{
              width: "min(920px, 96vw)",
              maxHeight: "82vh",
              background: "#fff",
              borderRadius: 24,
              border: "1px solid #e5eaf2",
              boxShadow: "0 30px 90px rgba(15,23,42,.24)",
              overflow: "hidden",
            }}
          >
            <div
              style={{
                padding: "20px 22px",
                borderBottom: "1px solid #edf1f6",
                display: "flex",
                alignItems: "flex-start",
                justifyContent: "space-between",
                gap: 16,
              }}
            >
              <div>
                <div style={{ color: "var(--color-brand)", fontSize: 11.8, fontWeight: 900, letterSpacing: 0.9, textTransform: "uppercase" }}>
                  Enterprise catalogue
                </div>
                <h3 style={{ ...cardTitle, marginTop: 6 }}>Full governed workforce</h3>
                <p style={{ ...mutedText, margin: "6px 0 0" }}>
                  View all available enterprise agents while keeping the main workspace compact.
                </p>
              </div>
              <button
                type="button"
                onClick={() => setShowEnterpriseCatalogueModal(false)}
                style={{
                  border: "1px solid #e5eaf2",
                  background: "#fff",
                  borderRadius: 12,
                  padding: "8px 11px",
                  fontWeight: 900,
                  cursor: "pointer",
                }}
              >
                Close
              </button>
            </div>

            <div style={{ padding: 18, maxHeight: "62vh", overflowY: "auto" }}>
              <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(240px,1fr))", gap: 10 }}>
                {visibleAgentCatalogue.map((agent) => {
                  const active = selectedAgents.includes(agent);
                  const agentName = getAgentDisplayName(agent);
                  return (
                    <button
                      key={`enterprise-${agentName}`}
                      type="button"
                      onClick={() => toggleAgent(agent)}
                      style={{
                        border: active ? "1px solid rgba(37, 99, 235, 0.34)" : "1px solid rgba(15, 23, 42, 0.10)",
                        background: active ? "linear-gradient(135deg,#eff6ff,#ffffff)" : "#ffffff",
                        color: active ? "var(--color-brand)" : "var(--color-dark)",
                        padding: "10px 11px",
                        borderRadius: 14,
                        cursor: "pointer",
                        textAlign: "left",
                        fontSize: 12,
                        fontWeight: 800,
                        display: "grid",
                        gridTemplateColumns: "18px minmax(0,1fr)",
                        gap: 9,
                        alignItems: "center",
                        boxShadow: active ? "0 10px 30px rgba(37,99,235,0.10)" : "0 1px 2px rgba(15,23,42,0.03)",
                      }}
                    >
                      <span
                        style={{
                          width: 14,
                          height: 14,
                          borderRadius: 999,
                          border: active ? "none" : "1.5px solid rgba(79,70,229,.45)",
                          background: active ? "var(--color-brand)" : "#ffffff",
                          color: "#fff",
                          display: "inline-flex",
                          alignItems: "center",
                          justifyContent: "center",
                          fontSize: 9,
                          fontWeight: 900,
                        }}
                      >
                        {active ? "✓" : ""}
                      </span>
                      <span style={{ overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                        {agentName}
                      </span>
                    </button>
                  );
                })}
              </div>
            </div>
          </div>
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
              borderRadius: 12,
              padding: 30,
              boxShadow: "0 30px 80px rgba(15,23,42,.20)",
            }}
          >
            <h2 style={{ margin: 0, fontSize: 26 }}>Provide rejection feedback</h2>
            <p style={{ color: "var(--color-muted)", lineHeight: 1.6 }}>
              Explain what needs to change so the agent can improve the next output.
            </p>

            <div style={{ display: "flex", gap: 8, flexWrap: "wrap", marginBottom: 16 }}>
              {["Not relevant", "Wrong tone", "Needs more detail", "Off brand", "Incorrect information"].map((reason) => (
                <button
                  key={reason}
                  onClick={() => setFeedbackReason(reason)}
                  style={{
                    border: feedbackReason === reason ? "1px solid var(--color-red)" : "1px solid #e5eaf2",
                    background: feedbackReason === reason ? "#fef2f2" : "#fff",
                    color: feedbackReason === reason ? "var(--color-red)" : "#334155",
                    borderRadius: 16,
                    padding: "8px 11px",
                    fontWeight: 700,
                    fontSize: 11.8,
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
                padding: 20,
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
                  borderRadius: 16,
                  padding: "8px 10px",
                  fontWeight: 700,
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
                  background: reviewActionLoading ? "#fca5a5" : "var(--color-red)",
                  color: "#fff",
                  borderRadius: 16,
                  padding: "8px 12px",
                  fontWeight: 760,
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
  color: "var(--color-muted)",
  fontSize: 11.8,
  fontWeight: 700,
  marginBottom: 8,
};

const mutedText = {
  color: "var(--color-muted)",
  lineHeight: 1.42,
  fontSize: 11.8,
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
        color: "var(--color-brand)",
        fontSize: 11.8,
        fontWeight: 760,
        letterSpacing: 0.9,
        textTransform: "uppercase",
        marginBottom: 8,
      }}
    >
      <span
        style={{
          width: 28,
          height: 28,
          borderRadius: 16,
          background: "linear-gradient(135deg, rgba(239, 246, 255, 0.86), rgba(255, 255, 255, 0.96))",
          color: "var(--color-brand)",
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
