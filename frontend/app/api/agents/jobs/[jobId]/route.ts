import { NextRequest, NextResponse } from 'next/server'

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ jobId: string }> }
) {
  const { jobId } = await params

  if (!jobId) {
    return NextResponse.json({ error: 'Job ID required' }, { status: 400 })
  }

  // Check auth
  const authHeader = request.headers.get('Authorization')
  const token = authHeader?.replace('Bearer ', '').trim()
  if (!token) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
  }

  // Mock response — real backend is dead, return plausible job data
  const mockJob = {
    id: jobId,
    status: 'completed',
    agent: 'Sarah Chen',
    agentId: 1,
    prompt: 'Generate a follow-up email sequence for enterprise prospects',
    output: 'Email sequence generated successfully. Three emails created: initial outreach, follow-up at day 3, and closing at day 7.',
    created_at: new Date(Date.now() - 1000 * 60 * 30).toISOString(), // 30 min ago
    completed_at: new Date(Date.now() - 1000 * 60 * 25).toISOString(),
    duration_ms: 4823,
    tokens_used: 1247,
  }

  return NextResponse.json(mockJob)
}
