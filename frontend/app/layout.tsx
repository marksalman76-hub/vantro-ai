import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Vantro — AI Agent Platform',
  description: 'Deploy your autonomous AI workforce.',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
