from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path.cwd()
stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = ROOT / "backups" / f"row11_agent_catalogue_production_ux_before_{stamp}"
backup.mkdir(parents=True, exist_ok=True)

catalogue_lib = ROOT / "frontend" / "src" / "lib" / "agentCatalogueProductionUx.ts"
options_route = ROOT / "frontend" / "src" / "app" / "api" / "signup-agent-selection" / "options" / "[plan]" / "route.ts"
validate_route = ROOT / "frontend" / "src" / "app" / "api" / "signup-agent-selection" / "validate" / "route.ts"
catalogue_route = ROOT / "frontend" / "src" / "app" / "api" / "agent-catalogue-production-ux" / "route.ts"

for p in [catalogue_lib, options_route, validate_route, catalogue_route]:
    if p.exists():
        shutil.copy2(p, backup / p.name)

catalogue_lib.parent.mkdir(parents=True, exist_ok=True)

catalogue_lib.write_text(r'''export type PackageKey = "starter" | "growth" | "business" | "enterprise";

export type CatalogueAgent = {
  agent_key: string;
  display_name: string;
  category: string;
  short_description: string;
  enterprise_only: boolean;
  internal_only: boolean;
  selectable: boolean;
  visible_to_client: boolean;
  client_safe_label: string;
  package_minimum: PackageKey;
};

export type CataloguePackageRules = {
  package_key: PackageKey;
  max_selectable_agents: number;
  enterprise_access: boolean;
  head_agent_visible: boolean;
  internal_agents_visible: boolean;
};

const PACKAGE_ORDER: PackageKey[] = ["starter", "growth", "business", "enterprise"];

export const PACKAGE_RULES: Record<PackageKey, CataloguePackageRules> = {
  starter: {
    package_key: "starter",
    max_selectable_agents: 3,
    enterprise_access: false,
    head_agent_visible: false,
    internal_agents_visible: false,
  },
  growth: {
    package_key: "growth",
    max_selectable_agents: 7,
    enterprise_access: false,
    head_agent_visible: false,
    internal_agents_visible: false,
  },
  business: {
    package_key: "business",
    max_selectable_agents: 10,
    enterprise_access: false,
    head_agent_visible: false,
    internal_agents_visible: false,
  },
  enterprise: {
    package_key: "enterprise",
    max_selectable_agents: 27,
    enterprise_access: true,
    head_agent_visible: true,
    internal_agents_visible: false,
  },
};

export const AGENT_CATALOGUE: CatalogueAgent[] = [
  {
    agent_key: "head_agent",
    display_name: "Head Agent",
    category: "Enterprise Control",
    short_description: "Coordinates the AI workforce and provides executive-level recommendations.",
    enterprise_only: true,
    internal_only: false,
    selectable: true,
    visible_to_client: true,
    client_safe_label: "Enterprise orchestration",
    package_minimum: "enterprise",
  },
  {
    agent_key: "strategist_agent",
    display_name: "Strategist Agent",
    category: "Strategy",
    short_description: "Develops business strategy, positioning, and growth direction.",
    enterprise_only: false,
    internal_only: false,
    selectable: true,
    visible_to_client: true,
    client_safe_label: "Business strategy",
    package_minimum: "starter",
  },
  {
    agent_key: "business_growth_partnerships_agent",
    display_name: "Business Growth & Partnerships Agent",
    category: "Growth",
    short_description: "Finds growth opportunities, partnerships, and expansion paths.",
    enterprise_only: false,
    internal_only: false,
    selectable: true,
    visible_to_client: true,
    client_safe_label: "Growth partnerships",
    package_minimum: "growth",
  },
  {
    agent_key: "lead_generator_appointment_setter_agent",
    display_name: "Lead Generator / Appointment Setter Agent",
    category: "Sales",
    short_description: "Supports lead generation, qualification, and appointment-setting workflows.",
    enterprise_only: false,
    internal_only: false,
    selectable: true,
    visible_to_client: true,
    client_safe_label: "Lead generation",
    package_minimum: "starter",
  },
  {
    agent_key: "marketing_specialist_agent",
    display_name: "Marketing Specialist Agent",
    category: "Marketing",
    short_description: "Creates campaign direction, messaging, and marketing execution plans.",
    enterprise_only: false,
    internal_only: false,
    selectable: true,
    visible_to_client: true,
    client_safe_label: "Marketing campaigns",
    package_minimum: "starter",
  },
  {
    agent_key: "social_media_manager_content_creator_agent",
    display_name: "Social Media Manager / Content Creator Agent",
    category: "Marketing",
    short_description: "Creates social content strategy, captions, and posting recommendations.",
    enterprise_only: false,
    internal_only: false,
    selectable: true,
    visible_to_client: true,
    client_safe_label: "Social content",
    package_minimum: "starter",
  },
  {
    agent_key: "seo_agent",
    display_name: "SEO Agent",
    category: "SEO",
    short_description: "Improves search visibility using technical, local, and content SEO guidance.",
    enterprise_only: false,
    internal_only: false,
    selectable: true,
    visible_to_client: true,
    client_safe_label: "SEO optimisation",
    package_minimum: "growth",
  },
  {
    agent_key: "email_reply_agent",
    display_name: "Email Reply Agent",
    category: "Communication",
    short_description: "Drafts professional replies and follow-up communication.",
    enterprise_only: false,
    internal_only: false,
    selectable: true,
    visible_to_client: true,
    client_safe_label: "Email replies",
    package_minimum: "starter",
  },
  {
    agent_key: "crm_ai_agent",
    display_name: "CRM AI Agent",
    category: "CRM",
    short_description: "Supports pipeline actions, follow-ups, segmentation, and CRM hygiene.",
    enterprise_only: false,
    internal_only: false,
    selectable: true,
    visible_to_client: true,
    client_safe_label: "CRM support",
    package_minimum: "growth",
  },
  {
    agent_key: "sales_closer_agent",
    display_name: "Sales / Closer Agent",
    category: "Sales",
    short_description: "Supports quote follow-up, objections, and deal progression.",
    enterprise_only: false,
    internal_only: false,
    selectable: true,
    visible_to_client: true,
    client_safe_label: "Sales closing",
    package_minimum: "growth",
  },
  {
    agent_key: "receptionist_agent",
    display_name: "Receptionist Agent",
    category: "Operations",
    short_description: "Handles front-desk style request routing and response support.",
    enterprise_only: false,
    internal_only: false,
    selectable: true,
    visible_to_client: true,
    client_safe_label: "Reception support",
    package_minimum: "starter",
  },
  {
    agent_key: "customer_support_agent",
    display_name: "Customer Support Agent",
    category: "Support",
    short_description: "Helps resolve customer issues and create support responses.",
    enterprise_only: false,
    internal_only: false,
    selectable: true,
    visible_to_client: true,
    client_safe_label: "Customer support",
    package_minimum: "starter",
  },
  {
    agent_key: "ecommerce_agent",
    display_name: "Ecommerce Agent",
    category: "Ecommerce",
    short_description: "Improves store conversion, product journeys, and ecommerce execution.",
    enterprise_only: false,
    internal_only: false,
    selectable: true,
    visible_to_client: true,
    client_safe_label: "Ecommerce optimisation",
    package_minimum: "starter",
  },
  {
    agent_key: "product_research_agent",
    display_name: "Product Research Agent",
    category: "Product",
    short_description: "Researches product opportunities, trends, and market fit.",
    enterprise_only: false,
    internal_only: false,
    selectable: true,
    visible_to_client: true,
    client_safe_label: "Product research",
    package_minimum: "growth",
  },
  {
    agent_key: "competitor_intelligence_agent",
    display_name: "Competitor Intelligence Agent",
    category: "Research",
    short_description: "Analyses competitors, gaps, and market positioning opportunities.",
    enterprise_only: false,
    internal_only: false,
    selectable: true,
    visible_to_client: true,
    client_safe_label: "Competitor intelligence",
    package_minimum: "growth",
  },
  {
    agent_key: "brand_strategy_agent",
    display_name: "Brand Strategy Agent",
    category: "Brand",
    short_description: "Builds positioning, voice, messaging, and brand direction.",
    enterprise_only: false,
    internal_only: false,
    selectable: true,
    visible_to_client: true,
    client_safe_label: "Brand strategy",
    package_minimum: "starter",
  },
  {
    agent_key: "store_builder_agent",
    display_name: "Store Builder Agent",
    category: "Build",
    short_description: "Plans ecommerce store structure, pages, and launch requirements.",
    enterprise_only: false,
    internal_only: false,
    selectable: true,
    visible_to_client: true,
    client_safe_label: "Store building",
    package_minimum: "business",
  },
  {
    agent_key: "website_landing_page_apps_agent",
    display_name: "Website / Landing Page / Apps Agent",
    category: "Build",
    short_description: "Plans websites, landing pages, and app-style client experiences.",
    enterprise_only: false,
    internal_only: false,
    selectable: true,
    visible_to_client: true,
    client_safe_label: "Web and app builds",
    package_minimum: "business",
  },
  {
    agent_key: "product_development_agent",
    display_name: "Product Development Agent",
    category: "Product",
    short_description: "Develops product concepts, features, validation, and launch direction.",
    enterprise_only: false,
    internal_only: false,
    selectable: true,
    visible_to_client: true,
    client_safe_label: "Product development",
    package_minimum: "business",
  },
  {
    agent_key: "product_copywriting_agent",
    display_name: "Product Copywriting Agent",
    category: "Copywriting",
    short_description: "Creates product copy, titles, descriptions, and conversion bullets.",
    enterprise_only: false,
    internal_only: false,
    selectable: true,
    visible_to_client: true,
    client_safe_label: "Product copywriting",
    package_minimum: "starter",
  },
  {
    agent_key: "ugc_creative_agent",
    display_name: "UGC Creative Agent",
    category: "Creative",
    short_description: "Creates UGC hooks, scripts, creator direction, and paid-ad concepts.",
    enterprise_only: false,
    internal_only: false,
    selectable: true,
    visible_to_client: true,
    client_safe_label: "UGC creative",
    package_minimum: "business",
  },
  {
    agent_key: "product_image_agent",
    display_name: "Product Image Agent",
    category: "Creative",
    short_description: "Creates product image direction and generated asset planning.",
    enterprise_only: false,
    internal_only: false,
    selectable: true,
    visible_to_client: true,
    client_safe_label: "Product images",
    package_minimum: "business",
  },
  {
    agent_key: "paid_ads_agent",
    display_name: "Paid Ads Agent",
    category: "Advertising",
    short_description: "Creates ad campaign structure, audiences, creative angles, and controls.",
    enterprise_only: false,
    internal_only: false,
    selectable: true,
    visible_to_client: true,
    client_safe_label: "Paid ads",
    package_minimum: "growth",
  },
  {
    agent_key: "analytics_optimisation_agent",
    display_name: "Analytics Optimisation Agent",
    category: "Analytics",
    short_description: "Turns analytics into optimisation recommendations and measurement plans.",
    enterprise_only: false,
    internal_only: false,
    selectable: true,
    visible_to_client: true,
    client_safe_label: "Analytics optimisation",
    package_minimum: "growth",
  },
  {
    agent_key: "influencer_collaboration_agent",
    display_name: "Influencer Collaboration Agent",
    category: "Influencer",
    short_description: "Plans influencer outreach, collaboration angles, and approval-safe briefs.",
    enterprise_only: false,
    internal_only: false,
    selectable: true,
    visible_to_client: true,
    client_safe_label: "Influencer collaboration",
    package_minimum: "business",
  },
  {
    agent_key: "orchestration_agent",
    display_name: "Orchestration Agent",
    category: "Internal",
    short_description: "Internal coordination layer hidden from standard client selection.",
    enterprise_only: true,
    internal_only: true,
    selectable: false,
    visible_to_client: false,
    client_safe_label: "Internal orchestration",
    package_minimum: "enterprise",
  },
  {
    agent_key: "security_compliance_agent",
    display_name: "Security & Compliance Agent",
    category: "Internal",
    short_description: "Internal governance, safety, and compliance support.",
    enterprise_only: false,
    internal_only: true,
    selectable: false,
    visible_to_client: false,
    client_safe_label: "Internal security",
    package_minimum: "enterprise",
  },
  {
    agent_key: "integration_automation_agent",
    display_name: "Integration / Automation Agent",
    category: "Internal",
    short_description: "Internal integration and automation support layer.",
    enterprise_only: false,
    internal_only: true,
    selectable: false,
    visible_to_client: false,
    client_safe_label: "Internal automation",
    package_minimum: "enterprise",
  },
];

function normalisePlan(plan: unknown): PackageKey {
  const value = String(plan || "").toLowerCase().trim();
  if (value === "enterprise") return "enterprise";
  if (value === "business") return "business";
  if (value === "growth") return "growth";
  return "starter";
}

function packageAllows(agent: CatalogueAgent, packageKey: PackageKey): boolean {
  const packageIndex = PACKAGE_ORDER.indexOf(packageKey);
  const minimumIndex = PACKAGE_ORDER.indexOf(agent.package_minimum);

  return packageIndex >= minimumIndex;
}

export function getCatalogueForPackage(plan: unknown) {
  const packageKey = normalisePlan(plan);
  const rules = PACKAGE_RULES[packageKey];

  const agents = AGENT_CATALOGUE
    .filter((agent) => {
      if (agent.internal_only && !rules.internal_agents_visible) return false;
      if (agent.agent_key === "head_agent" && !rules.head_agent_visible) return false;
      if (agent.enterprise_only && !rules.enterprise_access) return false;
      if (!agent.visible_to_client) return false;
      return packageAllows(agent, packageKey);
    })
    .map((agent) => ({
      ...agent,
      selectable: agent.selectable && packageAllows(agent, packageKey),
      selected_locked_after_activation: true,
      post_activation_changes_require_owner_approval: true,
      client_safe: true,
    }));

  return {
    success: true,
    agent_catalogue_production_ux_enabled: true,
    package_key: packageKey,
    rules,
    agent_count: agents.length,
    max_selectable_agents: rules.max_selectable_agents,
    agents,
  };
}

export function validateCatalogueSelection(plan: unknown, selectedAgents: unknown[]) {
  const catalogue = getCatalogueForPackage(plan);
  const allowed = new Set(catalogue.agents.filter((agent) => agent.selectable).map((agent) => agent.agent_key));
  const requested = selectedAgents.map((agent) => String(agent || "").trim()).filter(Boolean);
  const invalid = requested.filter((agent) => !allowed.has(agent));
  const duplicateCount = requested.length - new Set(requested).size;
  const overLimit = requested.length > catalogue.rules.max_selectable_agents;

  return {
    success: invalid.length === 0 && duplicateCount === 0 && !overLimit,
    agent_catalogue_production_ux_enabled: true,
    package_key: catalogue.package_key,
    selected_count: requested.length,
    max_selectable_agents: catalogue.rules.max_selectable_agents,
    invalid_agents: invalid,
    duplicate_count: duplicateCount,
    over_limit: overLimit,
    selected_locked_after_activation: true,
    post_activation_changes_require_owner_approval: true,
    client_safe_status:
      invalid.length || duplicateCount || overLimit
        ? "Selection needs correction before activation."
        : "Selection is valid and will lock after activation.",
  };
}
''', encoding="utf-8")

catalogue_route.parent.mkdir(parents=True, exist_ok=True)
catalogue_route.write_text(r'''import { NextRequest, NextResponse } from "next/server";
import {
  AGENT_CATALOGUE,
  getCatalogueForPackage,
  validateCatalogueSelection,
} from "@/lib/agentCatalogueProductionUx";

export const dynamic = "force-dynamic";

export async function GET(req: NextRequest): Promise<NextResponse> {
  const plan = req.nextUrl.searchParams.get("plan") || "starter";

  return NextResponse.json(getCatalogueForPackage(plan), {
    status: 200,
    headers: { "cache-control": "no-store, no-cache, must-revalidate" },
  });
}

export async function POST(req: NextRequest): Promise<NextResponse> {
  let body: Record<string, unknown> = {};

  try {
    body = await req.json();
  } catch {
    body = {};
  }

  const plan = body.plan || body.package_key || "starter";
  const selectedAgents = Array.isArray(body.selected_agents)
    ? body.selected_agents
    : Array.isArray(body.agents)
      ? body.agents
      : [];

  return NextResponse.json({
    ...validateCatalogueSelection(plan, selectedAgents),
    catalogue_total_count: AGENT_CATALOGUE.length,
  }, {
    status: 200,
    headers: { "cache-control": "no-store, no-cache, must-revalidate" },
  });
}
''', encoding="utf-8")

options_route.parent.mkdir(parents=True, exist_ok=True)
options_route.write_text(r'''import { NextRequest, NextResponse } from "next/server";
import { getCatalogueForPackage } from "@/lib/agentCatalogueProductionUx";

export const dynamic = "force-dynamic";

export async function GET(
  _req: NextRequest,
  context: { params: Promise<{ plan: string }> }
): Promise<NextResponse> {
  const { plan } = await context.params;

  return NextResponse.json(getCatalogueForPackage(plan), {
    status: 200,
    headers: { "cache-control": "no-store, no-cache, must-revalidate" },
  });
}
''', encoding="utf-8")

validate_route.parent.mkdir(parents=True, exist_ok=True)
validate_route.write_text(r'''import { NextRequest, NextResponse } from "next/server";
import { validateCatalogueSelection } from "@/lib/agentCatalogueProductionUx";

export const dynamic = "force-dynamic";

export async function POST(req: NextRequest): Promise<NextResponse> {
  let body: Record<string, unknown> = {};

  try {
    body = await req.json();
  } catch {
    body = {};
  }

  const plan = body.plan || body.package_key || "starter";
  const selectedAgents = Array.isArray(body.selected_agents)
    ? body.selected_agents
    : Array.isArray(body.agents)
      ? body.agents
      : [];

  const validation = validateCatalogueSelection(plan, selectedAgents);

  return NextResponse.json(validation, {
    status: validation.success ? 200 : 400,
    headers: { "cache-control": "no-store, no-cache, must-revalidate" },
  });
}
''', encoding="utf-8")

test = ROOT / "test_row11_agent_catalogue_production_ux.py"
test.write_text(r'''from pathlib import Path

checks = {
    "frontend/src/lib/agentCatalogueProductionUx.ts": [
        "AGENT_CATALOGUE",
        "PACKAGE_RULES",
        "getCatalogueForPackage",
        "validateCatalogueSelection",
        "agent_catalogue_production_ux_enabled",
        "selected_locked_after_activation",
        "post_activation_changes_require_owner_approval",
        "head_agent",
        "orchestration_agent",
        "internal_only",
    ],
    "frontend/src/app/api/agent-catalogue-production-ux/route.ts": [
        "getCatalogueForPackage",
        "validateCatalogueSelection",
        "catalogue_total_count",
    ],
    "frontend/src/app/api/signup-agent-selection/options/[plan]/route.ts": [
        "getCatalogueForPackage",
        "cache-control",
    ],
    "frontend/src/app/api/signup-agent-selection/validate/route.ts": [
        "validateCatalogueSelection",
        "selected_agents",
    ],
}

missing = {}

for file, needles in checks.items():
    text = Path(file).read_text(encoding="utf-8")
    absent = [needle for needle in needles if needle not in text]
    if absent:
        missing[file] = absent

if missing:
    raise SystemExit(f"ROW11_AGENT_CATALOGUE_PRODUCTION_UX_FAILED missing={missing}")

print("ROW11_AGENT_CATALOGUE_PRODUCTION_UX_PASSED")
''', encoding="utf-8")

print("ROW11_AGENT_CATALOGUE_PRODUCTION_UX_INSTALLED")
print(f"Backup: {backup}")
print(f"Created/updated: {catalogue_lib}")
print(f"Created/updated: {catalogue_route}")
print(f"Updated: {options_route}")
print(f"Updated: {validate_route}")
print(f"Created: {test}")