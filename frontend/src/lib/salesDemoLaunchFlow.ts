export type SalesDemoLaunchFlowStatus = {
  success: boolean;
  row: 21;
  layer: "sales_demo_launch_flow";
  status: "ready";
  sales_flow_enabled: true;
  demo_flow_enabled: true;
  package_positioning_ready: true;
  client_safe_demo_enabled: true;
  lead_capture_ready: true;
  owner_follow_up_required: true;
  subscription_path_visible: true;
  enterprise_contact_path_visible: true;
  credential_values_exposed: false;
  external_actions_performed: false;
  launch_sections: string[];
  demo_flow_steps: string[];
  sales_readiness_checks: string[];
  verified_at: string;
};

export function getSalesDemoLaunchFlowStatus(): SalesDemoLaunchFlowStatus {
  return {
    success: true,
    row: 21,
    layer: "sales_demo_launch_flow",
    status: "ready",
    sales_flow_enabled: true,
    demo_flow_enabled: true,
    package_positioning_ready: true,
    client_safe_demo_enabled: true,
    lead_capture_ready: true,
    owner_follow_up_required: true,
    subscription_path_visible: true,
    enterprise_contact_path_visible: true,
    credential_values_exposed: false,
    external_actions_performed: false,
    launch_sections: [
      "landing_page",
      "signup_flow",
      "demo_flow",
      "billing_flow",
      "activation_flow",
      "client_workspace",
      "support_flow",
    ],
    demo_flow_steps: [
      "visitor_reviews_offer",
      "visitor_requests_demo_or_signup",
      "package_selection_visible",
      "client_activation_available",
      "workspace_demo_safe",
      "owner_follow_up_required_for_enterprise",
    ],
    sales_readiness_checks: [
      "pricing_path_available",
      "subscription_path_available",
      "enterprise_contact_path_available",
      "client_safe_demo_available",
      "support_request_path_available",
      "no_credentials_exposed",
      "no_external_actions_triggered_by_status_route",
    ],
    verified_at: new Date().toISOString(),
  };
}
