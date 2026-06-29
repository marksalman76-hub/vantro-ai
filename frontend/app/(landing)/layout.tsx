import type { ReactNode } from 'react'
import CookieConsent from '@/components/CookieConsent'
import { ChatWidget } from '@/components/ui/chat-widget'

export default function LandingLayout({ children }: { children: ReactNode }) {
  return (
    <>
      {children}
      <CookieConsent />
      <ChatWidget />
    </>
  )
}
