import type { Metadata } from 'next'
import Navbar from '@/components/Navbar'
import Footer from '@/components/Footer'
import TrialSignupForm from '@/components/TrialSignupForm'

export const metadata: Metadata = {
  title: 'Start Your Free Trial',
  description: 'Deploy your first AI agent in under 10 minutes. No credit card required. 14-day free trial.',
  robots: { index: true, follow: true },
}

export default function SignupPage() {
  return (
    <>
      <Navbar />
      <main className="min-h-screen bg-dark pt-20 pb-20">
        {/* Background blobs */}
        <div className="pointer-events-none fixed inset-0 overflow-hidden -z-10">
          <div className="absolute -top-40 left-1/4 w-[500px] h-[500px] bg-violet-600/10 rounded-full blur-[120px]" />
          <div className="absolute bottom-0 right-1/4 w-[400px] h-[400px] bg-blue-600/10 rounded-full blur-[100px]" />
        </div>

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col lg:flex-row items-center justify-between gap-12 py-12">
            {/* Left: value prop */}
            <div className="flex-1 max-w-xl">
              <span className="inline-block px-3 py-1 rounded-full text-xs font-semibold glass border border-violet-500/20 text-violet-300 mb-5">
                14-Day Free Trial · No Credit Card
              </span>
              <h1 className="text-4xl sm:text-5xl font-bold text-white leading-tight mb-5">
                Your AI team is<br />
                <span className="gradient-text">ready to deploy</span>
              </h1>
              <p className="text-white/55 text-lg leading-relaxed mb-8">
                Join 500+ teams using Vantro agents to handle sales, support, research, and operations — 24/7, at scale.
              </p>

              <ul className="space-y-3">
                {[
                  'Deploy your first agent in under 10 minutes',
                  'Agents learn your brand voice and industry',
                  'Connects to 500+ tools you already use',
                  'Cancel any time — no strings attached',
                ].map((item) => (
                  <li key={item} className="flex items-start gap-3 text-sm text-white/65">
                    <span className="w-5 h-5 rounded-full bg-emerald-500/15 border border-emerald-400/30 flex items-center justify-center flex-shrink-0 mt-0.5">
                      <svg className="w-3 h-3 text-emerald-400" viewBox="0 0 12 12" fill="none">
                        <path d="M2 6l3 3 5-5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
                      </svg>
                    </span>
                    {item}
                  </li>
                ))}
              </ul>
            </div>

            {/* Right: form */}
            <div className="w-full max-w-md flex-shrink-0">
              <TrialSignupForm />
            </div>
          </div>
        </div>
      </main>
      <Footer />
    </>
  )
}
