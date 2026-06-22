import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Get Started',
  description: 'Set up your Vantro workspace in minutes and create your first AI video.',
  robots: { index: false, follow: false },
}

export default function OnboardingLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>
}
