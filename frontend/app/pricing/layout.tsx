import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Pricing',
  description: 'Simple, transparent pricing for AI video generation. Starter $99/mo, Growth $279/mo, Business $399/mo. Pay-as-you-go top-ups available.',
  openGraph: {
    title: 'Vantro Pricing — AI Video Generation Plans',
    description: 'Starter $99/mo · Growth $279/mo · Business $399/mo. Generate AI avatar videos with custom scripts and voices.',
  },
}

export default function PricingLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>
}
