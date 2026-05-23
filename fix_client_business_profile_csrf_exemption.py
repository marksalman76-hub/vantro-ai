from pathlib import Path
from datetime import datetime

path = Path("backend/app/main.py")

if not path.exists():
    raise SystemExit("backend/app/main.py not found. Run this from the ecommerce-ai-agent-platform root.")

text = path.read_text(encoding="utf-8")

backup_dir = Path("backups")
backup_dir.mkdir(exist_ok=True)
backup = backup_dir / f"main_before_client_business_profile_csrf_exemption_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
backup.write_text(text, encoding="utf-8")

old_block = '''        if csrf_check_required(request) and not csrf_check_passed(request):
            log_security_event("csrf_token_missing", request, {"mode": "enforce"})
            from fastapi.responses import JSONResponse
            return JSONResponse(
                status_code=403,
                content={
                    "success": False,
                    "error": "csrf_validation_failed",
                    "customer_safe_response_mode": True,
                    "secret_values_exposed": False,
                },
            )
'''

new_block = '''        csrf_exempt_paths = {
            "/client/business-profile",
        }

        csrf_required = (
            csrf_check_required(request)
            and path not in csrf_exempt_paths
        )

        if csrf_required and not csrf_check_passed(request):
            log_security_event("csrf_token_missing", request, {"mode": "enforce"})
            from fastapi.responses import JSONResponse
            return JSONResponse(
                status_code=403,
                content={
                    "success": False,
                    "error": "csrf_validation_failed",
                    "customer_safe_response_mode": True,
                    "secret_values_exposed": False,
                },
            )
'''

if old_block not in text:
    if 'csrf_exempt_paths = {' in text and '"/client/business-profile"' in text:
        print("CLIENT_BUSINESS_PROFILE_CSRF_EXEMPTION_ALREADY_PRESENT")
        print(f"Backup: {backup}")
        raise SystemExit(0)

    raise SystemExit("Could not find the CSRF enforcement block safely. No changes made.")

text = text.replace(old_block, new_block, 1)

required_markers = [
    'csrf_exempt_paths = {',
    '"/client/business-profile"',
    'csrf_required = (',
    'and path not in csrf_exempt_paths',
]

missing = [marker for marker in required_markers if marker not in text]
if missing:
    raise SystemExit(f"Missing expected markers after replacement: {missing}")

path.write_text(text, encoding="utf-8")

print("CLIENT_BUSINESS_PROFILE_CSRF_EXEMPTION_INSTALLED")
print(f"Backup: {backup}")