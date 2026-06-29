import { NextRequest, NextResponse } from 'next/server';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://api.vantro.ai';

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
  } catch (error) {
    return NextResponse.json({ error: 'Backend unreachable', detail: String(error) }, { status: 502 });
  }
}
