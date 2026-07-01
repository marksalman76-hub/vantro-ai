import { NextRequest, NextResponse } from 'next/server';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://api.vantro.ai';

export async function GET(request: NextRequest) {
  const cookieToken = request.cookies.get('access_token')?.value;
  const token = cookieToken
    ? `Bearer ${cookieToken}`
    : (request.headers.get('authorization') || '');

  try {
    const res = await fetch(`${API_URL}/api/credits`, {
      method: 'GET',
      headers: { Authorization: token, 'Content-Type': 'application/json' },
    });
    const data = await res.json();
    return NextResponse.json(data, { status: res.status });
  } catch (e) {
    return NextResponse.json({ error: 'Backend unreachable' }, { status: 502 });
  }
}
