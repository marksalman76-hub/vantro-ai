import { useRoute } from 'wouter'
import { DraftPage } from './pages'
import { ToastProvider } from './context/ToastContext'
import { ScrollProgress } from './components/ScrollProgress'
import { Navbar } from './components/Navbar'
import { Hero } from './components/Hero'
import { LogoStrip } from './components/LogoStrip'
import { Features } from './components/Features'
import { HowItWorks } from './components/HowItWorks'
import { AgentRoster } from './components/AgentRoster'
import { WhyVantro } from './components/WhyVantro'
import { Testimonials } from './components/Testimonials'
import { Pricing } from './components/Pricing'
import { FAQ } from './components/FAQ'
import { CTAFooter } from './components/CTAFooter'
import { Footer } from './components/Footer'
import { Toast } from './components/Toast'

export default function App() {
  const [isDraft] = useRoute('/draft')
  if (isDraft) return <DraftPage />
  return (
    <ToastProvider>
      <div className="bg-canvas text-snow min-h-[100dvh]" style={{ fontFamily: "'Inter', sans-serif" }}>
        <ScrollProgress />
        <Navbar />
        <main>
          <Hero />
          <LogoStrip />
          <Features />
          <HowItWorks />
          <AgentRoster />
          <WhyVantro />
          <Testimonials />
          <Pricing />
          <FAQ />
          <CTAFooter />
        </main>
        <Footer />
        <Toast />
      </div>
    </ToastProvider>
  )
}
