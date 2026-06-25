import { useRoute } from 'wouter'
import { DraftPage, PrivacyPage, TermsPage, AboutPage, BlogPage, ContactPage, CookiesPage } from './pages'
import { ChatWidget } from './components/ChatWidget'
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
  const [isPrivacy] = useRoute('/privacy')
  const [isTerms] = useRoute('/terms')
  const [isAbout] = useRoute('/about')
  const [isBlog] = useRoute('/blog')
  const [isContact] = useRoute('/contact')
  const [isCookies] = useRoute('/cookies')

  if (isDraft) return <DraftPage />
  if (isPrivacy) return <PrivacyPage />
  if (isTerms) return <TermsPage />
  if (isAbout) return <AboutPage />
  if (isBlog) return <BlogPage />
  if (isContact) return <ContactPage />
  if (isCookies) return <CookiesPage />

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
        <ChatWidget />
      </div>
    </ToastProvider>
  )
}
