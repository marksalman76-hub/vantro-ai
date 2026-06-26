import { NextResponse } from 'next/server'

export async function GET() {
  return NextResponse.json({
    total_credits: 999999,
    used_credits: 0,
    remaining_credits: 999999,
    tier: 'Enterprise',
    plan: 'Enterprise',
  })
}
