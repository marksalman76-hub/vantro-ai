from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
TARGET = ROOT / "backend" / "app" / "core" / "saas_provisioning_runtime.py"
BACKUP_DIR = ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

if not TARGET.exists():
    raise FileNotFoundError(TARGET)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = BACKUP_DIR / f"saas_provisioning_runtime_before_single_use_enforcement_{timestamp}.py"
backup.write_text(TARGET.read_text(encoding="utf-8"), encoding="utf-8")

text = TARGET.read_text(encoding="utf-8")

helper_anchor = '''def _append_jsonl(path: Path, record: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\\n")
'''

helper = '''

def _rewrite_jsonl(path: Path, records: List[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    with tmp_path.open("w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + "\\n")
    tmp_path.replace(path)
'''

if "def _rewrite_jsonl(" not in text:
    if helper_anchor not in text:
        raise RuntimeError("Could not find _append_jsonl helper block")
    text = text.replace(helper_anchor, helper_anchor + helper)

start = text.find("def validate_one_time_link(payload: Dict[str, Any]) -> Dict[str, Any]:")
if start == -1:
    raise RuntimeError("validate_one_time_link function not found")

next_def = text.find("\ndef ", start + 1)
if next_def == -1:
    next_def = len(text)

new_function = '''def validate_one_time_link(payload: Dict[str, Any]) -> Dict[str, Any]:
    token = str(
        payload.get("token")
        or payload.get("one_time_token")
        or payload.get("activation_token")
        or ""
    ).strip()

    tenant_id = payload.get("tenant_id")

    if not token:
        return {"success": False, "valid": False, "error": "missing_token"}

    token_hash = _hash_token(token)
    links = _read_jsonl(LINKS_FILE, limit=2000)

    for index, link in enumerate(links):
        if link.get("token_hash") != token_hash:
            continue

        if tenant_id and link.get("tenant_id") != tenant_id:
            return {
                "success": False,
                "valid": False,
                "error": "tenant_token_mismatch",
            }

        if link.get("used") is True:
            link["reuse_attempts"] = int(link.get("reuse_attempts") or 0) + 1
            link["last_reuse_attempt_at"] = _now_iso()
            link["admin_review_required_on_reuse"] = True
            links[index] = link
            _rewrite_jsonl(LINKS_FILE, links)

            _append_jsonl(
                AUDIT_FILE,
                {
                    "timestamp": _now_iso(),
                    "event_type": "one_time_link_reuse_blocked",
                    "tenant_id": link.get("tenant_id"),
                    "client_number": link.get("client_number"),
                    "link_id": link.get("link_id"),
                    "admin_review_required": True,
                    "profile": SAAS_PROVISIONING_PROFILE,
                },
            )

            return {
                "success": False,
                "valid": False,
                "error": "one_time_link_already_used",
                "tenant_id": link.get("tenant_id"),
                "client_number": link.get("client_number"),
                "single_use": True,
                "blocked_after_use": True,
                "admin_review_required": True,
            }

        link["used"] = True
        link["used_at"] = _now_iso()
        link["used_by_client_email"] = payload.get("client_email")
        link["blocked_after_use"] = True
        links[index] = link
        _rewrite_jsonl(LINKS_FILE, links)

        _append_jsonl(
            AUDIT_FILE,
            {
                "timestamp": _now_iso(),
                "event_type": "one_time_link_validated_and_consumed",
                "tenant_id": link.get("tenant_id"),
                "client_number": link.get("client_number"),
                "link_id": link.get("link_id"),
                "single_use_consumed": True,
                "profile": SAAS_PROVISIONING_PROFILE,
            },
        )

        return {
            "success": True,
            "valid": True,
            "tenant_id": link.get("tenant_id"),
            "client_number": link.get("client_number"),
            "single_use": True,
            "used": True,
            "blocked_after_use": True,
        }

    return {"success": False, "valid": False, "error": "invalid_token"}

'''

text = text[:start] + new_function + text[next_def:]
TARGET.write_text(text, encoding="utf-8")

print("PRIORITY8_SINGLE_USE_LINK_ENFORCEMENT_FIXED")
print(f"Backup: {backup}")
print(f"Updated: {TARGET}")