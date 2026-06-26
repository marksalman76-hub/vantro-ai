import { NextRequest } from 'next/server'

const RUNWAY_BASE     = 'https://api.dev.runwayml.com/v1'
const RUNWAY_VERSION  = '2024-11-06'
const HIGGSFIELD_BASE = 'https://api.higgsfield.ai/v1'

export async function GET(request: NextRequest) {
  const authHeader = request.headers.get('Authorization')
  const token = authHeader?.replace('Bearer ', '').trim()
  if (!token) {
    return Response.json({ error: 'Unauthorized' }, { status: 401 })
  }

  const { searchParams } = request.nextUrl
  const provider = searchParams.get('provider') || 'runway'
  const taskId   = searchParams.get('task_id') || searchParams.get('job_id') || ''

  if (!taskId) {
    return Response.json({ error: 'task_id or job_id is required' }, { status: 400 })
  }

  if (provider === 'higgsfield') {
    const HIGGSFIELD_KEY = process.env.HIGGSFIELD_API_KEY || ''
    if (!HIGGSFIELD_KEY) {
      return Response.json({ error: 'HIGGSFIELD_API_KEY not configured' }, { status: 503 })
    }
    const r = await fetch(`${HIGGSFIELD_BASE}/generation/${taskId}`, {
      headers: { Authorization: `Bearer ${HIGGSFIELD_KEY}` },
    })
    const data = await r.json()
    return Response.json(data, { status: r.status })
  }

  const RUNWAY_KEY = process.env.RUNWAY_API_KEY || ''
  if (!RUNWAY_KEY) {
    return Response.json({ error: 'RUNWAY_API_KEY not configured' }, { status: 503 })
  }
  const r = await fetch(`${RUNWAY_BASE}/tasks/${taskId}`, {
    headers: {
      Authorization: `Bearer ${RUNWAY_KEY}`,
      'X-Runway-Version': RUNWAY_VERSION,
    },
  })
  const data = await r.json()
  return Response.json(data, { status: r.status })
}
