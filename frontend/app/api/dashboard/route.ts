import { NextRequest, NextResponse } from "next/server";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "https://api.vantro.ai";

export async function GET(request: NextRequest) {
  const token = request.headers.get("authorization")?.replace("Bearer ", "");
  if (!token) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });

  const headers = { Authorization: `Bearer ${token}` };

  try {
    const [userRes, creditsRes, jobsRes] = await Promise.all([
      fetch(`${API_URL}/api/auth/me`, { headers }),
      fetch(`${API_URL}/api/credits`, { headers }),
      fetch(`${API_URL}/api/media-jobs`, { headers }),
    ]);

    if (!userRes.ok) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });

    const [user, credits, mediaJobs] = await Promise.all([
      userRes.json(),
      creditsRes.ok ? creditsRes.json() : { total_credits: 0, used_credits: 0, remaining_credits: 0, tier: 'free' },
      jobsRes.ok ? jobsRes.json() : { total_jobs: 0, jobs: [] },
    ]);

    return NextResponse.json({ user, credits, mediaJobs });
  } catch {
    return NextResponse.json({ error: "Internal server error" }, { status: 500 });
  }
}
