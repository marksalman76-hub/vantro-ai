import { NextRequest, NextResponse } from 'next/server';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://api.vantro.ai';

export async function POST(request: NextRequest) {
  const cookieToken = request.cookies.get('access_token')?.value;
  const token = cookieToken
    ? `Bearer ${cookieToken}`
    : (request.headers.get('authorization') || '');

  let body: string | undefined;
  try { body = await request.text(); } catch { body = undefined; }

  try {
    const res = await fetch(`${API_URL}/api/workspace/business-context`, {
      method: 'POST',
      headers: { Authorization: token, 'Content-Type': 'application/json' },
      ...(body !== undefined ? { body } : {}),
    });
    const data = await res.json();
    return NextResponse.json(data, { status: res.status });
  } catch (e) {
    return NextResponse.json({ error: 'Backend unreachable' }, { status: 502 });
  }
}
