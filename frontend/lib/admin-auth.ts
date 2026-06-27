import { createHmac } from 'crypto'

export function verifyAdminToken(token: string): boolean {
  const adminPassword = process.env.ADMIN_PASSWORD
  const secret = process.env.OTP_SECRET || ''
  if (!adminPassword || !token) return false
  const expected = createHmac('sha256', secret).update(adminPassword).digest('hex')
  return token === expected
}
