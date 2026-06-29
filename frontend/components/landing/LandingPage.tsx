'use client'

import Navigation from './Navigation'
import Hero from './Hero'
import Features from './Features'
import AgentShowcase from './AgentShowcase'
import Integrations from './Integrations'
import ScrollStory from './ScrollStory'
import Stats from './Stats'
import Testimonials from './Testimonials'
import HowItWorks from './HowItWorks'
import Pricing from './Pricing'
import FinalCTA from './FinalCTA'
import SiteFooter from './SiteFooter'

export default function LandingPage() {
  return (
    <main style={{ background: '#0F1419', overflowX: 'hidden', width: '100%' }}>
      <Navigation />
      <Hero />
      <Features />
      <AgentShowcase />
      <Integrations />
      <ScrollStory />
      <Stats />
      <Testimonials />
      <HowItWorks />
      <Pricing />
      <FinalCTA />
      <SiteFooter />
    </main>
  )
}
