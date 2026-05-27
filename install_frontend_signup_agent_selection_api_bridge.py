from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

api_root = ROOT / "frontend" / "src" / "app" / "api" / "signup-agent-selection"
backup_dir = ROOT / "backups" / f"frontend_signup_agent_selection_api_before_{STAMP}"
backup_dir.mkdir(parents=True, exist_ok=True)

files = {
    api_root / "options" / "[plan]" / "route.ts": r'''
import { NextRequest, NextResponse } from "next/server";

function backendBase() {
  return process.env.BACKEND_URL || process.env.NEXT_PUBLIC_BACKEND_URL || "http://127.0.0.1:8000";
}

export async function GET(
  _request: NextRequest,
  context: { params: Promise<{ plan: string }> }
) {
  const { plan } = await context.params;

  const res = await fetch(`${backendBase()}/signup-agent-selection/options/${encodeURIComponent(plan)}`, {
    method: "GET",
    cache: "no-store",
  });

  const data = await res.json();
  return NextResponse.json(data, { status: res.status });
}
'''.lstrip(),

    api_root / "validate" / "route.ts": r'''
import { NextRequest, NextResponse } from "next/server";

function backendBase() {
  return process.env.BACKEND_URL || process.env.NEXT_PUBLIC_BACKEND_URL || "http://127.0.0.1:8000";
}

export async function POST(request: NextRequest) {
  const body = await request.json().catch(() => ({}));

  const res = await fetch(`${backendBase()}/signup-agent-selection/validate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    cache: "no-store",
    body: JSON.stringify(body),
  });

  const data = await res.json();
  return NextResponse.json(data, { status: res.status });
}
'''.lstrip(),

    api_root / "activation-packet" / "route.ts": r'''
import { NextRequest, NextResponse } from "next/server";

function backendBase() {
  return process.env.BACKEND_URL || process.env.NEXT_PUBLIC_BACKEND_URL || "http://127.0.0.1:8000";
}

export async function POST(request: NextRequest) {
  const body = await request.json().catch(() => ({}));

  const res = await fetch(`${backendBase()}/signup-agent-selection/activation-packet`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    cache: "no-store",
    body: JSON.stringify(body),
  });

  const data = await res.json();
  return NextResponse.json(data, { status: res.status });
}
'''.lstrip(),

    ROOT / "test_frontend_signup_agent_selection_api_bridge.py": r'''
from pathlib import Path

ROOT = Path.cwd()

expected_files = [
    ROOT / "frontend/src/app/api/signup-agent-selection/options/[plan]/route.ts",
    ROOT / "frontend/src/app/api/signup-agent-selection/validate/route.ts",
    ROOT / "frontend/src/app/api/signup-agent-selection/activation-packet/route.ts",
]

for path in expected_files:
    assert path.exists(), f"Missing {path}"
    text = path.read_text(encoding="utf-8")
    assert "signup-agent-selection" in text
    assert "NextResponse.json" in text
    assert "cache: \"no-store\"" in text

options = expected_files[0].read_text(encoding="utf-8")
assert "/signup-agent-selection/options/" in options

validate = expected_files[1].read_text(encoding="utf-8")
assert "/signup-agent-selection/validate" in validate

activation = expected_files[2].read_text(encoding="utf-8")
assert "/signup-agent-selection/activation-packet" in activation

print("FRONTEND_SIGNUP_AGENT_SELECTION_API_BRIDGE_TESTS_PASSED")
print("routes", len(expected_files))
'''
}

for path in files:
    if path.exists():
        backup_path = backup_dir / str(path.relative_to(ROOT)).replace("\\", "__").replace("/", "__")
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        backup_path.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")

for path, content in files.items():
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")

print("FRONTEND_SIGNUP_AGENT_SELECTION_API_BRIDGE_INSTALLED")
print(f"Backup folder: {backup_dir}")
for path in files:
    print(f"Created/updated: {path}")