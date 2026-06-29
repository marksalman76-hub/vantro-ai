'use client'

import Link from 'next/link'

export default function RefundPolicyPage() {
  return (
    <div
      className="min-h-screen px-4 py-24"
      style={{ background: 'radial-gradient(ellipse 80% 50% at 50% -10%, rgba(255,107,53,0.08) 0%, transparent 60%), #0A0D14' }}
    >
      <div className="mesh-grid pointer-events-none fixed inset-0 opacity-15" />

      <div className="relative max-w-2xl mx-auto">
        <div className="text-center mb-12">
          <Link href="/" className="inline-flex items-center gap-2.5">
            <div className="w-9 h-9 rounded-xl flex items-center justify-center text-white font-black text-sm" style={{ background: 'linear-gradient(135deg,#FF6B35,#00D9FF)', boxShadow: '0 0 20px rgba(255,107,53,0.40)' }}>V</div>
            <span className="text-xl font-bold tracking-tight text-white">Vantro<span style={{ color: '#FF6B35' }}>.ai</span></span>
          </Link>
        </div>

        <div className="rounded-2xl p-8 md:p-10" style={{ background: 'rgba(26,31,46,0.80)', border: '1px solid rgba(255,255,255,0.08)', backdropFilter: 'blur(20px)' }}>
          <h1 className="text-3xl font-bold text-white mb-2">Refund Policy</h1>
          <p className="text-sm mb-8" style={{ color: 'rgba(255,255,255,0.35)' }}>Last updated: June 2025</p>

          <div className="space-y-8" style={{ color: 'rgba(255,255,255,0.65)', fontSize: 15, lineHeight: 1.75 }}>

            <section>
              <h2 className="text-white font-semibold text-lg mb-3">30-Day Money-Back Guarantee</h2>
              <p>
                If you are not satisfied with Vantro for any reason, you may request a full refund within <strong style={{ color: '#FF6B35' }}>30 days</strong> of your initial payment. No questions asked.
              </p>
            </section>

            <div style={{ height: 1, background: 'rgba(255,255,255,0.06)' }} />

            <section>
              <h2 className="text-white font-semibold text-lg mb-3">Eligibility</h2>
              <ul className="space-y-2 list-none">
                {[
                  'Refunds apply to first-time purchases on any plan (Starter, Growth, or Business).',
                  'The request must be made within 30 calendar days of the original charge date.',
                  'Renewals after the first billing cycle are not eligible for refunds.',
                  'Accounts found to be in violation of our Terms of Service are not eligible.',
                ].map(item => (
                  <li key={item} className="flex items-start gap-3">
                    <div className="flex-shrink-0 mt-1.5 w-1.5 h-1.5 rounded-full" style={{ background: '#FF6B35' }} />
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </section>

            <div style={{ height: 1, background: 'rgba(255,255,255,0.06)' }} />

            <section>
              <h2 className="text-white font-semibold text-lg mb-3">How to Request a Refund</h2>
              <p className="mb-3">
                Email us at <a href="mailto:billing@vantro.ai" style={{ color: '#FF6B35', textDecoration: 'none' }}>billing@vantro.ai</a> with subject <strong style={{ color: 'rgba(255,255,255,0.85)' }}>Refund Request</strong> and include:
              </p>
              <ul className="space-y-2 list-none">
                {[
                  'Your registered email address',
                  'The plan you subscribed to',
                  'Stripe payment receipt or transaction ID (optional — speeds up processing)',
                ].map(item => (
                  <li key={item} className="flex items-start gap-3">
                    <div className="flex-shrink-0 mt-1.5 w-1.5 h-1.5 rounded-full" style={{ background: '#1FFFD6' }} />
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
              <p className="mt-4">
                Requests processed within <strong style={{ color: 'rgba(255,255,255,0.85)' }}>3–5 business days</strong>. Refunds go to the original payment method.
              </p>
            </section>

            <div style={{ height: 1, background: 'rgba(255,255,255,0.06)' }} />

            <section>
              <h2 className="text-white font-semibold text-lg mb-3">Partial Refunds & Downgrades</h2>
              <p>
                No partial refunds for unused time within a billing cycle. Downgrades take effect at next renewal — access continues until then.
              </p>
            </section>

            <div style={{ height: 1, background: 'rgba(255,255,255,0.06)' }} />

            <section>
              <h2 className="text-white font-semibold text-lg mb-3">Cancellations</h2>
              <p>
                Cancel anytime from your dashboard. Future charges stop immediately. Access continues until end of the paid period — no proration after the 30-day window.
              </p>
            </section>

            <div style={{ height: 1, background: 'rgba(255,255,255,0.06)' }} />

            <section>
              <h2 className="text-white font-semibold text-lg mb-3">Contact</h2>
              <p>
                Questions? <a href="mailto:billing@vantro.ai" style={{ color: '#FF6B35', textDecoration: 'none' }}>billing@vantro.ai</a>
              </p>
            </section>
          </div>
        </div>

        <div className="text-center mt-8 flex items-center justify-center gap-6 text-xs" style={{ color: 'rgba(255,255,255,0.25)' }}>
          <Link href="/privacy" className="hover:text-white/50 transition-colors">Privacy Policy</Link>
          <span>·</span>
          <Link href="/terms" className="hover:text-white/50 transition-colors">Terms of Service</Link>
          <span>·</span>
          <Link href="/" className="hover:text-white/50 transition-colors">Back to home</Link>
        </div>
      </div>
    </div>
  )
}
