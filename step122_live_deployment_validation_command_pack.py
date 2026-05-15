from pathlib import Path
from datetime import datetime, timezone
import json

ROOT = Path(r"C:\Users\User\Desktop\ecommerce-ai-agent-platform")
DATA = ROOT / "backend" / "app" / "data"
DOCS = ROOT / "docs"

DATA.mkdir(parents=True, exist_ok=True)
DOCS.mkdir(parents=True, exist_ok=True)

now = datetime.now(timezone.utc).isoformat()

pack = {
    "step": 122,
    "name": "Live Deployment Validation Command Pack",
    "generated_at_utc": now,
    "status": "live_deployment_validation_command_pack_created",
    "secret_values_included": False,
    "required_placeholders": {
        "BACKEND_URL": "replace with production backend URL",
        "FRONTEND_URL": "replace with production frontend URL"
    },
    "validation_commands": {
        "backend_health": "curl -i \"%BACKEND_URL%/health\"",
        "frontend_homepage": "curl -i \"%FRONTEND_URL%/\"",
        "admin_route": "curl -i \"%FRONTEND_URL%/admin\"",
        "client_route": "curl -i \"%FRONTEND_URL%/client\"",
        "cors_preflight": "curl -i -X OPTIONS \"%BACKEND_URL%/health\" -H \"Origin: %FRONTEND_URL%\" -H \"Access-Control-Request-Method: GET\"",
        "blocked_origin_preflight": "curl -i -X OPTIONS \"%BACKEND_URL%/health\" -H \"Origin: https://blocked-origin.example\" -H \"Access-Control-Request-Method: GET\""
    },
    "release_decision": {
        "can_continue": True,
        "next_step": "live_environment_values_capture_template_without_secrets",
    },
}

json_path = DATA / "step122_live_deployment_validation_command_pack.json"
md_path = DOCS / "STEP_122_LIVE_DEPLOYMENT_VALIDATION_COMMAND_PACK.md"
cmd_path = DOCS / "STEP_122_LIVE_DEPLOYMENT_VALIDATION_COMMANDS.cmd"

json_path.write_text(json.dumps(pack, indent=2), encoding="utf-8")

cmd_content = """@echo off
REM Step 122 — Live Deployment Validation Commands
REM Replace these two values with your real deployed URLs before running.
REM Do not paste secrets into this file.

set BACKEND_URL=https://YOUR-BACKEND-URL-HERE
set FRONTEND_URL=https://YOUR-FRONTEND-URL-HERE

echo Checking backend health...
curl -i "%BACKEND_URL%/health"

echo.
echo Checking frontend homepage...
curl -i "%FRONTEND_URL%/"

echo.
echo Checking admin route...
curl -i "%FRONTEND_URL%/admin"

echo.
echo Checking client route...
curl -i "%FRONTEND_URL%/client"

echo.
echo Checking allowed CORS preflight...
curl -i -X OPTIONS "%BACKEND_URL%/health" -H "Origin: %FRONTEND_URL%" -H "Access-Control-Request-Method: GET"

echo.
echo Checking blocked origin CORS preflight...
curl -i -X OPTIONS "%BACKEND_URL%/health" -H "Origin: https://blocked-origin.example" -H "Access-Control-Request-Method: GET"

echo.
echo STEP_122_LIVE_VALIDATION_COMMANDS_COMPLETE
"""
cmd_path.write_text(cmd_content, encoding="utf-8")

commands = "\n".join(
    f"- `{name}`: `{cmd}`"
    for name, cmd in pack["validation_commands"].items()
)

md = f"""# Step 122 — Live Deployment Validation Command Pack

Generated: {now}

## Status

**Result:** Live deployment validation command pack created.  
**Secret values included:** No

## Files Created

- `docs/STEP_122_LIVE_DEPLOYMENT_VALIDATION_COMMAND_PACK.md`
- `docs/STEP_122_LIVE_DEPLOYMENT_VALIDATION_COMMANDS.cmd`
- `backend/app/data/step122_live_deployment_validation_command_pack.json`

## Required Live Values

Replace only these placeholders before running live checks:

- `BACKEND_URL`
- `FRONTEND_URL`

## Validation Commands

{commands}

## Validation Coverage

- Backend `/health`
- Frontend homepage
- Admin route
- Client route
- Allowed production-origin CORS preflight
- Blocked-origin CORS preflight

## Safety Rules

- Do not add secrets to the command file.
- Do not paste provider keys into command prompt.
- Use only production URLs.
- Confirm blocked-origin CORS does not allow unknown domains.
- Review response headers for unsafe exposure.

## Release Decision

- Can continue: `True`
- Next step: Live environment values capture template without secrets.
"""

md_path.write_text(md, encoding="utf-8")

print("STEP_122_LIVE_DEPLOYMENT_VALIDATION_COMMAND_PACK_CREATED")
print("json_path", json_path)
print("md_path", md_path)
print("cmd_path", cmd_path)
print("secret_values_included", pack["secret_values_included"])
print("can_continue", pack["release_decision"]["can_continue"])
print("STEP_122_OK")