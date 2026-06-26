'use client'

import Navigation from './Navigation'
import Hero from './Hero'
import AgentShowcase from './AgentShowcase'
import Integrations from './Integrations'
import HowItWorks from './HowItWorks'
import Stats from './Stats'
import Testimonials from './Testimonials'
import Pricing from './Pricing'
import FinalCTA from './FinalCTA'
import SiteFooter from './SiteFooter'

export default function LandingPage() {
  return (
    <main style={{ background: '#0F1419', overflowX: 'hidden' }}>
      <Navigation />
      <Hero />
      <AgentShowcase />
      <Integrations />
      <HowItWorks />
      <Stats />
      <Testimonials />
      <Pricing />
      <FinalCTA />
      <SiteFooter />
    </main>
  )
}
