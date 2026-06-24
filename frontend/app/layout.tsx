import type { Metadata } from 'next'
import { Poppins, Playfair_Display, Inter, Outfit, Instrument_Serif, Barlow, Space_Mono } from 'next/font/google'
import './globals.css'
import GTMScript       from '@/components/GTMScript'
import CookieConsent   from '@/components/CookieConsent'
import ExitIntentPopup from '@/components/ExitIntentPopup'
import StickyCtaBar    from '@/components/StickyCtaBar'

const poppins = Poppins({
  subsets: ['latin'],
  weight: ['300', '400', '500', '600', '700'],
  variable: '--font-poppins',
  display: 'swap',
})

const playfair = Playfair_Display({
  subsets: ['latin'],
  variable: '--font-playfair',
  display: 'swap',
})

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-inter',
  display: 'swap',
})

const outfit = Outfit({
  subsets: ['latin'],
  weight: ['300', '400', '500', '600', '700'],
  variable: '--font-outfit',
  display: 'swap',
})

const instrumentSerif = Instrument_Serif({
  subsets: ['latin'],
  weight: '400',
  style: ['normal', 'italic'],
  variable: '--font-instrument-serif',
  display: 'swap',
})

const barlow = Barlow({
  subsets: ['latin'],
  weight: ['300', '400', '500', '600'],
  variable: '--font-barlow',
  display: 'swap',
})

const spaceMono = Space_Mono({
  subsets: ['latin'],
  weight: ['400', '700'],
  variable: '--font-space-mono',
  display: 'swap',
})

export const metadata: Metadata = {
  title: {
    default: 'Vantro — Deploy AI Agents That Work For You',
    template: '%s | Vantro',
  },
  description:
    'Deploy autonomous AI agents that handle sales, support, research, and operations 24/7. Join 500+ teams saving 100+ hours per week with Vantro.',
  keywords: [
    'AI agents',
    'autonomous AI',
    'business automation',
    'AI workforce',
    'sales automation',
    'customer support AI',
    'Vantro',
  ],
  authors: [{ name: 'Vantro Inc.' }],
  creator: 'Vantro Inc.',
  openGraph: {
    type: 'website',
    locale: 'en_US',
    url: 'https://vantro.ai',
    siteName: 'Vantro',
    title: 'Vantro — Deploy AI Agents That Work For You',
    description:
      'Deploy autonomous AI agents that handle sales, support, research, and operations 24/7.',
    images: [{ url: 'https://vantro.ai/og-image.png', width: 1200, height: 630 }],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Vantro — Deploy AI Agents That Work For You',
    description: 'Autonomous AI agents for every business function.',
    creator: '@vantroai',
  },
  robots: {
    index: true,
    follow: true,
    googleBot: { index: true, follow: true, 'max-video-preview': -1, 'max-image-preview': 'large' },
  },
  metadataBase: new URL('https://vantro.ai'),
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${poppins.variable} ${playfair.variable} ${inter.variable} ${outfit.variable} ${instrumentSerif.variable} ${barlow.variable} ${spaceMono.variable}`}>
      <body className="font-sans bg-dark text-white antialiased">
        <GTMScript />
        {children}
        <CookieConsent />
        <ExitIntentPopup />
        <StickyCtaBar />
      </body>
    </html>
  )
}
