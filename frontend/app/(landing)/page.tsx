import Hero          from '@/components/sections/hero'
import LogoStrip     from '@/components/sections/LogoStrip'
import Features      from '@/components/sections/features'
import DemoVideo     from '@/components/sections/DemoVideo'
import HowItWorks    from '@/components/sections/HowItWorks'
import AgentCarousel from '@/components/sections/AgentCarousel'
import WhyVantro     from '@/components/sections/WhyVantro'
import ROICalculator from '@/components/sections/ROICalculator'
import Integrations  from '@/components/sections/Integrations'
import Testimonials  from '@/components/sections/Testimonials'
import Pricing       from '@/components/sections/Pricing'
import CTAFooter     from '@/components/sections/CTAFooter'

export const metadata = {
  title:       'Vantro — Deploy AI Agents That Work For You',
  description: 'Deploy autonomous AI agents that handle sales, support, research, and operations 24/7. No MLOps team required.',
}

export default function Home() {
  return (
    <>
      <Hero />
      <LogoStrip />
      <Features />
      <DemoVideo />
      <HowItWorks />
      <AgentCarousel />
      <WhyVantro />
      <ROICalculator />
      <Integrations />
      <Testimonials />
      <Pricing />
      <CTAFooter />
    </>
  )
}
