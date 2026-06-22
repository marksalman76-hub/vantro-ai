import dynamic from 'next/dynamic'
import Navbar      from '@/components/Navbar'
import Footer      from '@/components/Footer'
import HeroSection from '@/components/sections/HeroSection'
import { generateOrganizationSchema, generateProductSchema, generateWebsiteSchema } from '@/lib/seo'

// Everything below the fold is lazy-loaded so the hero is interactive immediately
// and the browser only parses/renders these chunks as the user scrolls into view.
const WhyVantro           = dynamic(() => import('@/components/sections/WhyVantro'))
const DemoVideo           = dynamic(() => import('@/components/sections/DemoVideo'))
const AdaptabilityShowcase= dynamic(() => import('@/components/sections/AdaptabilityShowcase'))
const AgentRoster         = dynamic(() => import('@/components/sections/AgentRoster'))
const DynamicEvolution    = dynamic(() => import('@/components/sections/DynamicEvolution'))
const HowItWorks          = dynamic(() => import('@/components/sections/HowItWorks'))
const ROICalculator       = dynamic(() => import('@/components/sections/ROICalculator'))
const IndustryAdaptability= dynamic(() => import('@/components/sections/IndustryAdaptability'))
const BrandVoiceLearning  = dynamic(() => import('@/components/sections/BrandVoiceLearning'))
const AgentIntelligence   = dynamic(() => import('@/components/sections/AgentIntelligence'))
const Integrations        = dynamic(() => import('@/components/sections/Integrations'))
const Pricing             = dynamic(() => import('@/components/sections/Pricing'))
const Testimonials        = dynamic(() => import('@/components/sections/Testimonials'))
const CTASection          = dynamic(() => import('@/components/sections/CTASection'))
const AIChatbot           = dynamic(() => import('@/components/AIChatbot'))

export default function Home() {
  return (
    <>
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(generateOrganizationSchema()) }} />
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(generateProductSchema()) }} />
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(generateWebsiteSchema()) }} />

      <Navbar />

      <main>
        <HeroSection />
        <WhyVantro />
        <DemoVideo />
        <AdaptabilityShowcase />
        <AgentRoster />
        <DynamicEvolution />
        <HowItWorks />
        <ROICalculator />
        <IndustryAdaptability />
        <BrandVoiceLearning />
        <AgentIntelligence />
        <Integrations />
        <Pricing />
        <Testimonials />
        <CTASection />
      </main>

      <Footer />
      <AIChatbot />
    </>
  )
}
