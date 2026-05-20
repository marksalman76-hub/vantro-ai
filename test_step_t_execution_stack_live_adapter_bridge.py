from backend.app.runtime.execution_stack import ExecutionStack, ExecutionRequest, execution_summary

stack = ExecutionStack()

result = stack.route(
    ExecutionRequest(
        action_type="execute_live_integration_action",
        payload={
            "tenant_id": "client_demo_001",
            "integration_key": "crm",
            "action": "add_note",
            "actor_role": "customer",
            "payload": {
                "location_id": "mlWJi2CdN2cXHRe06d5b",
                "contact_id": "REPLACE_WITH_EXISTING_GHL_CONTACT_ID",
                "body": "ExecutionStack bridge proof: agent runtime can route to live CRM adapter safely.",
            },
        },
        owner_approved=False,
    )
)

print(execution_summary(result))
