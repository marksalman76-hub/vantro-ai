import { NextRequest, NextResponse } from 'next/server';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

function getAuth(req: NextRequest): string {
  const cookieToken = req.cookies.get('access_token')?.value;
  return cookieToken ? `Bearer ${cookieToken}` : (req.headers.get('authorization') || '');
}

export async function DELETE(
  req: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params;
  const auth = getAuth(req);
  try {
    const res = await fetch(`${API_URL}/api/admin/brand-assets/${id}`, {
      method: 'DELETE',
      headers: { Authorization: auth },
    });
    const data = await res.json();
    return NextResponse.json(data, { status: res.status });
  } catch {
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}
