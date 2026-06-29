import { NextRequest, NextResponse } from 'next/server';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://api.vantro.ai';

async function toJsonResponse(res: Response) {
  const text = await res.text();
  const contentType = res.headers.get('content-type') || '';

  if (contentType.includes('application/json') && text) {
    try {
      return NextResponse.json(JSON.parse(text), { status: res.status });
    } catch {
      return NextResponse.json(
        { error: 'Invalid JSON from backend', detail: text },
        { status: res.status }
      );
    }
  }

  return NextResponse.json(
    { error: text || res.statusText || 'Backend request failed' },
    { status: res.status }
  );
}

function getAuth(req: NextRequest): string {
  const cookieToken = req.cookies.get('access_token')?.value;
  return cookieToken ? `Bearer ${cookieToken}` : (req.headers.get('authorization') || '');
}

export async function GET(req: NextRequest) {
  const auth = getAuth(req);
  try {
    const res = await fetch(`${API_URL}/api/admin/brand-assets`, {
      headers: { Authorization: auth },
    });
    return toJsonResponse(res);
  } catch (error) {
    return NextResponse.json({ error: 'Backend unreachable', detail: String(error) }, { status: 502 });
  }
}

export async function POST(req: NextRequest) {
  const auth = getAuth(req);
  const contentType = req.headers.get('content-type') || '';
  const body = await req.arrayBuffer();
  try {
    const res = await fetch(`${API_URL}/api/admin/brand-assets`, {
      method: 'POST',
      headers: { Authorization: auth, 'Content-Type': contentType },
      body,
    });
    return toJsonResponse(res);
  } catch (error) {
    return NextResponse.json({ error: 'Backend unreachable', detail: String(error) }, { status: 502 });
  }
}
