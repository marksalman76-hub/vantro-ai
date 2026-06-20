import Navbar                from '@/components/Navbar'
import Footer                from '@/components/Footer'
import AIChatbot             from '@/components/AIChatbot'
import HeroSection           from '@/components/sections/HeroSection'
import WhyVantro             from '@/components/sections/WhyVantro'
import DemoVideo             from '@/components/sections/DemoVideo'
import AdaptabilityShowcase  from '@/components/sections/AdaptabilityShowcase'
import AgentRoster           from '@/components/sections/AgentRoster'
import DynamicEvolution      from '@/components/sections/DynamicEvolution'
import HowItWorks            from '@/components/sections/HowItWorks'
import ROICalculator         from '@/components/sections/ROICalculator'
import IndustryAdaptability  from '@/components/sections/IndustryAdaptability'
import BrandVoiceLearning    from '@/components/sections/BrandVoiceLearning'
import AgentIntelligence     from '@/components/sections/AgentIntelligence'
import Integrations          from '@/components/sections/Integrations'
import Pricing               from '@/components/sections/Pricing'
import Testimonials          from '@/components/sections/Testimonials'
import CTASection            from '@/components/sections/CTASection'
import { generateOrganizationSchema, generateProductSchema, generateWebsiteSchema } from '@/lib/seo'

export default function Home() {
  return (
    <>
      {/* Structured data */}
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(generateOrganizationSchema()) }} />
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(generateProductSchema()) }} />
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(generateWebsiteSchema()) }} />

      <Navbar />

      <main>
        {/* 1 */ } <HeroSection />
        {/* 2 */ } <WhyVantro />
        {/* 2b */} <DemoVideo />
        {/* 3 */ } <AdaptabilityShowcase />
        {/* 4 */ } <AgentRoster />
{/* 6 */ } <DynamicEvolution />
        {/* 7 */ } <HowItWorks />
        {/* 8 */ } <ROICalculator />
        {/* 9 */ } <IndustryAdaptability />
{/* 11 */} <BrandVoiceLearning />
        {/* 12 */} <AgentIntelligence />
        {/* 13 */} <Integrations />
        {/* 14 */} <Pricing />
        {/* 15 */} <Testimonials />
        {/* 15 */} <CTASection />
      </main>

      <Footer />
      <AIChatbot />
    </>
  )
}
