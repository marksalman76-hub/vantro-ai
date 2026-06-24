import { useEffect } from 'react'
import { useRoute } from 'wouter'
import { motion } from 'framer-motion'
import { DraftPage, LoginPage, SignupPage, OnboardingPage } from './pages'
import { DashboardPage } from './pages/DashboardPage'
import { ToastProvider } from './context/ToastContext'
import { CursorFollower } from './components/CursorFollower'
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
  const [isLogin] = useRoute('/login')
  const [isSignup] = useRoute('/signup')
  const [isOnboarding] = useRoute('/onboarding')
  const [isDashboard] = useRoute('/dashboard')
  const [isDashboardSub] = useRoute('/dashboard/:rest*')

  useEffect(() => {
    const handle = () => {
      if (document.visibilityState === 'hidden') {
        document.body.classList.add('tab-hidden')
      } else {
        document.body.classList.remove('tab-hidden')
      }
    }
    document.addEventListener('visibilitychange', handle)
    return () => document.removeEventListener('visibilitychange', handle)
  }, [])

  if (isDraft) return <DraftPage />
  if (isLogin) return <LoginPage />
  if (isSignup) return <SignupPage />
  if (isOnboarding) return <OnboardingPage />
  if (isDashboard || isDashboardSub) return <DashboardPage />
  return (
    <ToastProvider>
      <div className="bg-canvas text-snow min-h-[100dvh]" style={{ fontFamily: "'Inter', sans-serif" }}>
        <ScrollProgress />
        <Navbar />
        <motion.main initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.45, ease: 'easeOut' }}>
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
        </motion.main>
        <Footer />
        <Toast />
        <CursorFollower />
      </div>
    </ToastProvider>
  )
}
