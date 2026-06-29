import { NextRequest, NextResponse } from 'next/server';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://api.vantro.ai';

function getAuth(req: NextRequest): string {
  const cookieToken = req.cookies.get('access_token')?.value;
  return cookieToken ? `Bearer ${cookieToken}` : (req.headers.get('authorization') || '');
}

export async function GET(
  req: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  const { path } = await params;
  const auth = getAuth(req);
  const filename = path.join('/');
  try {
    const res = await fetch(`${API_URL}/api/admin/brand-assets/files/${filename}`, {
      headers: { Authorization: auth },
    });
    const buffer = await res.arrayBuffer();
    return new NextResponse(buffer, {
      status: res.status,
      headers: {
        'Content-Type': res.headers.get('content-type') || 'application/octet-stream',
        'Content-Disposition': res.headers.get('content-disposition') || 'inline',
      },
    });
  } catch (error) {
    return NextResponse.json({ error: 'Backend unreachable', detail: String(error) }, { status: 502 });
  }
}
