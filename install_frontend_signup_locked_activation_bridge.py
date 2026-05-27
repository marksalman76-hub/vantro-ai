from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP_DIR = ROOT / "backups" / f"frontend_signup_locked_activation_bridge_before_{STAMP}"
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

FILES = {
    ROOT / "frontend" / "src" / "app" / "api" / "signup-locked-activation" / "status" / "route.ts": r'''import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL = process.env.BACKEND_URL || process.env.NEXT_PUBLIC_BACKEND_URL || "https://api.trance-formation.com.au";

function getBearerToken(request: NextRequest): string | null {
  const authHeader = request.headers.get("authorization");
  if (authHeader && authHeader.toLowerCase().startsWith("bearer ")) {
    return authHeader;
  }

  const adminToken = process.env.ADMIN_PLATFORM_TOKEN;
  if (adminToken) {
    return `Bearer ${adminToken}`;
  }

  return null;
}

export async function GET(request: NextRequest) {
  const bearer = getBearerToken(request);

  if (!bearer) {
    return NextResponse.json(
      {
        success: false,
        error: "auth_required",
        message: "Missing bearer token.",
      },
      { status: 401 },
    );
  }

  const upstream = await fetch(`${BACKEND_URL}/signup-locked-activation/status`, {
    method: "GET",
    headers: {
      authorization: bearer,
      "content-type": "application/json",
    },
    cache: "no-store",
  });

  const text = await upstream.text();

  try {
    return NextResponse.json(JSON.parse(text), { status: upstream.status });
  } catch {
    return new NextResponse(text, {
      status: upstream.status,
      headers: { "content-type": "application/json" },
    });
  }
}
''',

    ROOT / "frontend" / "src" / "app" / "api" / "signup-locked-activation" / "draft" / "route.ts": r'''import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL = process.env.BACKEND_URL || process.env.NEXT_PUBLIC_BACKEND_URL || "https://api.trance-formation.com.au";

function getBearerToken(request: NextRequest): string | null {
  const authHeader = request.headers.get("authorization");
  if (authHeader && authHeader.toLowerCase().startsWith("bearer ")) {
    return authHeader;
  }

  const adminToken = process.env.ADMIN_PLATFORM_TOKEN;
  if (adminToken) {
    return `Bearer ${adminToken}`;
  }

  return null;
}

export async function POST(request: NextRequest) {
  const bearer = getBearerToken(request);

  if (!bearer) {
    return NextResponse.json(
      {
        success: false,
        error: "auth_required",
        message: "Missing bearer token.",
      },
      { status: 401 },
    );
  }

  const body = await request.text();

  const upstream = await fetch(`${BACKEND_URL}/signup-locked-activation/draft`, {
    method: "POST",
    headers: {
      authorization: bearer,
      "content-type": "application/json",
    },
    body,
    cache: "no-store",
  });

  const text = await upstream.text();

  try {
    return NextResponse.json(JSON.parse(text), { status: upstream.status });
  } catch {
    return new NextResponse(text, {
      status: upstream.status,
      headers: { "content-type": "application/json" },
    });
  }
}
''',

    ROOT / "frontend" / "src" / "app" / "api" / "signup-locked-activation" / "activate" / "route.ts": r'''import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL = process.env.BACKEND_URL || process.env.NEXT_PUBLIC_BACKEND_URL || "https://api.trance-formation.com.au";

function getBearerToken(request: NextRequest): string | null {
  const authHeader = request.headers.get("authorization");
  if (authHeader && authHeader.toLowerCase().startsWith("bearer ")) {
    return authHeader;
  }

  const adminToken = process.env.ADMIN_PLATFORM_TOKEN;
  if (adminToken) {
    return `Bearer ${adminToken}`;
  }

  return null;
}

export async function POST(request: NextRequest) {
  const bearer = getBearerToken(request);

  if (!bearer) {
    return NextResponse.json(
      {
        success: false,
        error: "auth_required",
        message: "Missing bearer token.",
      },
      { status: 401 },
    );
  }

  const body = await request.text();

  const upstream = await fetch(`${BACKEND_URL}/signup-locked-activation/activate`, {
    method: "POST",
    headers: {
      authorization: bearer,
      "content-type": "application/json",
    },
    body,
    cache: "no-store",
  });

  const text = await upstream.text();

  try {
    return NextResponse.json(JSON.parse(text), { status: upstream.status });
  } catch {
    return new NextResponse(text, {
      status: upstream.status,
      headers: { "content-type": "application/json" },
    });
  }
}
''',

    ROOT / "frontend" / "src" / "app" / "api" / "signup-locked-activation" / "change-request" / "route.ts": r'''import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL = process.env.BACKEND_URL || process.env.NEXT_PUBLIC_BACKEND_URL || "https://api.trance-formation.com.au";

function getBearerToken(request: NextRequest): string | null {
  const authHeader = request.headers.get("authorization");
  if (authHeader && authHeader.toLowerCase().startsWith("bearer ")) {
    return authHeader;
  }

  const adminToken = process.env.ADMIN_PLATFORM_TOKEN;
  if (adminToken) {
    return `Bearer ${adminToken}`;
  }

  return null;
}

export async function POST(request: NextRequest) {
  const bearer = getBearerToken(request);

  if (!bearer) {
    return NextResponse.json(
      {
        success: false,
        error: "auth_required",
        message: "Missing bearer token.",
      },
      { status: 401 },
    );
  }

  const body = await request.text();

  const upstream = await fetch(`${BACKEND_URL}/signup-locked-activation/change-request`, {
    method: "POST",
    headers: {
      authorization: bearer,
      "content-type": "application/json",
    },
    body,
    cache: "no-store",
  });

  const text = await upstream.text();

  try {
    return NextResponse.json(JSON.parse(text), { status: upstream.status });
  } catch {
    return new NextResponse(text, {
      status: upstream.status,
      headers: { "content-type": "application/json" },
    });
  }
}
''',

    ROOT / "test_frontend_signup_locked_activation_bridge.py": r'''from pathlib import Path

ROOT = Path.cwd()

EXPECTED_FILES = [
    ROOT / "frontend" / "src" / "app" / "api" / "signup-locked-activation" / "status" / "route.ts",
    ROOT / "frontend" / "src" / "app" / "api" / "signup-locked-activation" / "draft" / "route.ts",
    ROOT / "frontend" / "src" / "app" / "api" / "signup-locked-activation" / "activate" / "route.ts",
    ROOT / "frontend" / "src" / "app" / "api" / "signup-locked-activation" / "change-request" / "route.ts",
]

for path in EXPECTED_FILES:
    assert path.exists(), f"Missing expected file: {path}"
    text = path.read_text(encoding="utf-8")
    assert "signup-locked-activation" in text, f"Missing route bridge marker in {path}"
    assert "ADMIN_PLATFORM_TOKEN" in text, f"Missing admin token fallback in {path}"
    assert "auth_required" in text, f"Missing auth guard response in {path}"
    assert "cache: \"no-store\"" in text, f"Missing no-store fetch policy in {path}"
    assert "credential" not in text.lower(), f"Unsafe credential wording found in {path}"

print("FRONTEND_SIGNUP_LOCKED_ACTIVATION_BRIDGE_TESTS_PASSED")
for path in EXPECTED_FILES:
    print("verified", path)
'''
}

for path, content in FILES.items():
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        backup_path = BACKUP_DIR / path.relative_to(ROOT)
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        backup_path.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")
    path.write_text(content, encoding="utf-8")

print("FRONTEND_SIGNUP_LOCKED_ACTIVATION_BRIDGE_INSTALLED")
print(f"Backup folder: {BACKUP_DIR}")
for path in FILES:
    print(f"Created/updated: {path}")