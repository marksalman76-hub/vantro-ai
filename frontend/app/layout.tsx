import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-inter',
  display: 'swap',
})

export const metadata: Metadata = {
  metadataBase: new URL('https://vantro.ai'),
  title: {
    default: 'Vantro AI — Autonomous AI Workforce Platform',
    template: '%s | Vantro AI',
  },
  description: '22 specialized AI agents running 24/7 across sales, ops, support, and engineering. Deploy your autonomous AI workforce in 5 minutes. 200+ integrations.',
  keywords: ['AI agents', 'autonomous AI workforce', 'AI automation platform', 'AI sales agent', 'AI ops automation', 'AI customer support'],
  alternates: { canonical: 'https://vantro.ai' },
  openGraph: {
    type: 'website',
    url: 'https://vantro.ai',
    siteName: 'Vantro AI',
    title: 'Vantro AI — Deploy Your Autonomous AI Workforce',
    description: '22 specialized AI agents. 200+ integrations. Working 24/7 so your team can focus on what only humans can do.',
    images: [{ url: '/og-image.png', width: 1200, height: 630, alt: 'Vantro AI Platform' }],
  },
  twitter: {
    card: 'summary_large_image',
    site: '@vantroai',
    title: 'Vantro AI — Autonomous AI Workforce',
    description: '22 specialized AI agents. 200+ integrations. Deploy in 5 minutes.',
    images: ['/og-image.png'],
  },
  robots: { index: true, follow: true },
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={inter.variable}>
      <body>{children}</body>
    </html>
  )
}
