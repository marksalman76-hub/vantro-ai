import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Create Video',
  description: 'Generate a professional AI avatar video in minutes. Choose your avatar, voice, script, language and tone.',
  robots: { index: false, follow: false },
}

export default function CreateLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>
}
