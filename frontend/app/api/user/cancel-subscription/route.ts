import { NextRequest, NextResponse } from 'next/server'

export async function POST(request: NextRequest) {
  try {
    const authHeader = request.headers.get('Authorization')
    const token = authHeader?.replace('Bearer ', '').trim()
    if (!token) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    return NextResponse.json({ error: 'Subscription cancellation is not yet implemented. Contact support.' }, { status: 501 })
  } catch {
    return NextResponse.json(
      { detail: 'Cancellation failed. Please contact support at billing@vantro.ai.' },
      { status: 500 }
    )
  }
}
