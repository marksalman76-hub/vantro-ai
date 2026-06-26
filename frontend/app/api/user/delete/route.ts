import { NextRequest, NextResponse } from "next/server";

const API_URL =
  process.env.ACCOUNT_SERVER_URL ||
  process.env.API_BACKEND_URL ||
  process.env.NEXT_PUBLIC_API_URL ||
  "https://api.vantro.ai";

export async function DELETE(request: NextRequest) {
  try {
    const authHeader = request.headers.get('Authorization')
    const cookieToken = request.cookies.get('access_token')?.value
    const token = cookieToken ?? authHeader?.replace('Bearer ', '').trim()

    if (!token) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    const res = await fetch(`${API_URL}/api/account/delete`, {
      method: "DELETE",
      headers: {
        Authorization: token,
        "Content-Type": "application/json",
      },
    });

    const data = await res.json();

    if (!res.ok) {
      return NextResponse.json(
        { error: data.detail || "Account deletion failed" },
        { status: res.status }
      );
    }

    const response = NextResponse.json(data);
    response.cookies.delete("access_token");
    return response;
  } catch {
    return NextResponse.json({ error: "Internal server error" }, { status: 500 });
  }
}
