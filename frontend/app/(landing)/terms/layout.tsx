import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Terms of Service | Vantro',
  description: 'Terms of Service for Vantro.ai — the AI agent platform for ecommerce businesses. Read about acceptable use, billing, and your rights.',
  openGraph: {
    title: 'Terms of Service | Vantro',
    description: 'Terms of Service for Vantro.ai — the AI agent platform for ecommerce businesses.',
  },
}

export default function TermsLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>
}
