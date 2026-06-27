import { NextRequest } from 'next/server'
import crypto from 'crypto'

const RUNWAY_BASE     = 'https://api.dev.runwayml.com/v1'
const RUNWAY_VERSION  = '2024-11-06'
const HIGGSFIELD_BASE = 'https://api.higgsfield.ai/v1'
const KLING_BASE      = 'https://api.klingai.com/v1'

function klingJwt(ak: string, sk: string): string {
  const header  = Buffer.from(JSON.stringify({ alg: 'HS256', typ: 'JWT' })).toString('base64url')
  const now     = Math.floor(Date.now() / 1000)
  const payload = Buffer.from(JSON.stringify({ iss: ak, exp: now + 1800, nbf: now - 5 })).toString('base64url')
  const sig     = crypto.createHmac('sha256', sk).update(`${header}.${payload}`).digest('base64url')
  return `${header}.${payload}.${sig}`
}

export async function GET(request: NextRequest) {
  const { searchParams } = request.nextUrl
  const provider  = searchParams.get('provider') || 'runway'
  const taskId    = searchParams.get('task_id') || searchParams.get('job_id') || ''
  const klingType = searchParams.get('kling_type') || 'text2video'

  if (!taskId) return Response.json({ error: 'task_id or job_id is required' }, { status: 400 })
  if (!/^[a-zA-Z0-9_-]{4,256}$/.test(taskId)) return Response.json({ error: 'Invalid task ID' }, { status: 400 })

  if (provider === 'higgsfield') {
    const HIGGSFIELD_KEY = process.env.HIGGSFIELD_API_KEY || ''
    if (!HIGGSFIELD_KEY) return Response.json({ error: 'Status unavailable.' }, { status: 503 })
    const r = await fetch(`${HIGGSFIELD_BASE}/generation/${taskId}`, {
      headers: { Authorization: `Bearer ${HIGGSFIELD_KEY}` },
    })
    const data = await r.json()
    return Response.json(data, { status: r.status })
  }

  if (provider === 'kling') {
    const KLING_AK = process.env.KLING_ACCESS_KEY || ''
    const KLING_SK = process.env.KLING_SECRET_KEY || ''
    if (!KLING_AK || !KLING_SK) return Response.json({ error: 'Status unavailable.' }, { status: 503 })
    const jwt = klingJwt(KLING_AK, KLING_SK)
    const r = await fetch(`${KLING_BASE}/videos/${klingType}/${taskId}`, {
      headers: { Authorization: `Bearer ${jwt}` },
    })
    const data = await r.json()
    if (data.code !== 0) return Response.json({ error: 'Status check failed.' }, { status: 500 })
    const task     = data.data
    const kStatus  = task?.task_status ?? ''
    const videoUrl = task?.task_result?.videos?.[0]?.url ?? null
    return Response.json({
      status: kStatus === 'succeed' ? 'SUCCEEDED' : kStatus === 'failed' ? 'FAILED' : 'processing',
      video_url: videoUrl,
      provider: 'kling',
    })
  }

  // Runway
  const RUNWAY_KEY = process.env.RUNWAY_API_KEY || ''
  if (!RUNWAY_KEY) return Response.json({ error: 'Status unavailable.' }, { status: 503 })
  const r = await fetch(`${RUNWAY_BASE}/tasks/${taskId}`, {
    headers: { Authorization: `Bearer ${RUNWAY_KEY}`, 'X-Runway-Version': RUNWAY_VERSION },
  })
  const data = await r.json()
  return Response.json(data, { status: r.status })
}
