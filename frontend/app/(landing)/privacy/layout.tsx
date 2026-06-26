import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Privacy Policy | Vantro',
  description: 'How Vantro.ai collects, uses, and protects your personal data. GDPR and CCPA compliant.',
}

export default function PrivacyLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>
}
