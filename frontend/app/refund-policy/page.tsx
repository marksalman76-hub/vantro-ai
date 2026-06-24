import type { Metadata } from 'next'
import Link from 'next/link'
import Navbar from '@/components/Navbar'
import Footer from '@/components/Footer'

export const metadata: Metadata = {
  title: 'Refund Policy — Vantro',
  description: 'Vantro refund policy: eligibility conditions, the 72-hour refund window, and how to request a refund.',
  robots: { index: true, follow: true },
}

const TOC = [
  { id: 'overview',     label: '1. Overview'                     },
  { id: 'eligibility',  label: '2. Eligibility Conditions'       },
  { id: 'no-refund',    label: '3. When Refunds Are Not Available' },
  { id: 'how-to',       label: '4. How to Request a Refund'      },
  { id: 'processing',   label: '5. Processing Time'               },
  { id: 'contact',      label: '6. Contact'                       },
]

export default function RefundPolicyPage() {
  return (
    <>
      <Navbar />
      <div className="min-h-screen bg-dark pt-20">
        {/* Hero */}
        <div className="bg-gradient-to-b from-dark-950 to-dark border-b border-white/[0.06] py-14 px-4">
          <div className="max-w-3xl mx-auto">
            <p className="text-xs font-semibold text-violet-400 uppercase tracking-widest mb-3">Legal</p>
            <h1 className="text-4xl sm:text-5xl font-bold text-white mb-4">Refund Policy</h1>
            <p className="text-white/55 text-lg">Last updated: <time dateTime="2026-06-24">June 24, 2026</time></p>
            <p className="mt-4 text-white/60 leading-relaxed max-w-2xl">
              This Refund Policy explains when you are eligible for a refund on your Vantro subscription
              and how to request one.
            </p>
          </div>
        </div>

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-14">
          <div className="flex flex-col lg:flex-row gap-12">
            {/* Sticky TOC */}
            <aside className="lg:w-56 flex-shrink-0">
              <div className="lg:sticky lg:top-28">
                <p className="text-xs font-semibold text-white/35 uppercase tracking-widest mb-4">Contents</p>
                <nav>
                  <ul className="space-y-1.5">
                    {TOC.map((item) => (
                      <li key={item.id}>
                        <Link
                          href={`#${item.id}`}
                          className="text-sm text-white/45 hover:text-violet-300 transition-colors block py-0.5"
                        >
                          {item.label}
                        </Link>
                      </li>
                    ))}
                  </ul>
                </nav>
              </div>
            </aside>

            {/* Content */}
            <article className="flex-1 min-w-0 prose-legal">
              <style>{`
                .prose-legal h2 { color: white; font-size: 1.375rem; font-weight: 700; margin-top: 2.5rem; margin-bottom: 1rem; padding-bottom: 0.5rem; border-bottom: 1px solid rgba(255,255,255,0.07); }
                .prose-legal h3 { color: rgba(255,255,255,0.85); font-size: 1.05rem; font-weight: 600; margin-top: 1.5rem; margin-bottom: 0.5rem; }
                .prose-legal p  { color: rgba(255,255,255,0.6); line-height: 1.75; margin-bottom: 1rem; }
                .prose-legal ul { list-style: disc; padding-left: 1.5rem; margin-bottom: 1rem; }
                .prose-legal li { color: rgba(255,255,255,0.6); line-height: 1.75; margin-bottom: 0.375rem; }
                .prose-legal a  { color: #a78bfa; text-decoration: underline; text-underline-offset: 3px; }
                .prose-legal a:hover { color: #c4b5fd; }
                .prose-legal strong { color: rgba(255,255,255,0.8); font-weight: 600; }
              `}</style>

              <section id="overview">
                <h2>1. Overview</h2>
                <p>
                  Vantro offers a <strong>72-hour full refund window</strong> for new subscribers who have
                  not yet executed any agent tasks. This policy exists to give you confidence when signing
                  up: if the platform is not right for you and you have not used any of our AI agents, you
                  can request a complete refund with no questions asked.
                </p>
                <p>
                  Outside of these conditions, all subscription fees are non-refundable. We encourage you
                  to review our plans and available agents carefully before subscribing.
                </p>
              </section>

              <section id="eligibility">
                <h2>2. Eligibility Conditions</h2>
                <p>You are eligible for a full refund if <strong>all</strong> of the following are true:</p>
                <ul>
                  <li>
                    <strong>72-hour window:</strong> Your account was created no more than 72 hours ago at
                    the time you submit your refund request.
                  </li>
                  <li>
                    <strong>No tasks executed:</strong> No agent jobs have been run on your account. A job
                    is considered executed the moment an agent begins processing your request — it does not
                    matter whether the job completed successfully.
                  </li>
                  <li>
                    <strong>Active subscription:</strong> Your subscription must be in an active or
                    trialling state at the time of the request.
                  </li>
                </ul>
                <p>
                  If all three conditions are met, you are entitled to a full refund of your most recent
                  payment and your subscription will be cancelled immediately.
                </p>
              </section>

              <section id="no-refund">
                <h2>3. When Refunds Are Not Available</h2>
                <p>Refunds are <strong>not available</strong> in the following circumstances:</p>
                <ul>
                  <li>
                    <strong>Tasks executed:</strong> One or more agent jobs have been run on your workspace,
                    regardless of their outcome.
                  </li>
                  <li>
                    <strong>Window expired:</strong> More than 72 hours have passed since your account was
                    created.
                  </li>
                  <li>
                    <strong>Repeat subscriptions:</strong> Refunds apply only to the first payment on a
                    new subscription. Subsequent monthly renewal charges are non-refundable.
                  </li>
                  <li>
                    <strong>Credit top-ups:</strong> One-time credit purchases are non-refundable once
                    credits have been added to your account.
                  </li>
                  <li>
                    <strong>Violations of Terms:</strong> Accounts suspended for violations of our{' '}
                    <Link href="/terms">Terms of Service</Link> are not eligible for a refund.
                  </li>
                </ul>
              </section>

              <section id="how-to">
                <h2>4. How to Request a Refund</h2>
                <h3>Option A — Billing dashboard (recommended)</h3>
                <p>
                  The fastest way to request a refund is through your billing dashboard. Log in to your
                  account, navigate to{' '}
                  <strong>Dashboard &rsaquo; Billing</strong>, and click{' '}
                  <strong>&ldquo;Request Refund&rdquo;</strong>. The system will verify your eligibility
                  instantly and, if approved, issue the refund automatically.
                </p>
                <h3>Option B — Email support</h3>
                <p>
                  If you are unable to access your account or prefer to contact us directly, email{' '}
                  <a href="mailto:support@vantro.ai">support@vantro.ai</a> with the subject line{' '}
                  <em>&ldquo;Refund Request — [your registered email]&rdquo;</em>. Include the email
                  address associated with your account and a brief description of your request. Our team
                  will review and respond within one business day.
                </p>
              </section>

              <section id="processing">
                <h2>5. Processing Time</h2>
                <p>
                  Once a refund is approved, it is submitted to your payment provider immediately. The time
                  it takes to appear on your statement depends on your bank or card issuer:
                </p>
                <ul>
                  <li><strong>Credit / debit cards:</strong> typically 5–10 business days</li>
                  <li><strong>Other payment methods:</strong> may vary; please consult your provider</li>
                </ul>
                <p>
                  Your subscription is cancelled immediately upon approval — you will not be charged again.
                  Access to the platform will end at the time of cancellation.
                </p>
              </section>

              <section id="contact">
                <h2>6. Contact</h2>
                <p>
                  If you have questions about this policy or your refund status, please reach out:
                </p>
                <ul>
                  <li><strong>Email:</strong> <a href="mailto:support@vantro.ai">support@vantro.ai</a></li>
                  <li><strong>Billing dashboard:</strong> <Link href="/dashboard/billing">Dashboard &rsaquo; Billing</Link></li>
                </ul>

                <div className="mt-8 p-4 rounded-xl bg-violet-600/10 border border-violet-500/20">
                  <p className="text-sm text-white/60 !mb-0">
                    <strong className="text-violet-300">Note:</strong> This policy may be updated from
                    time to time. The date at the top of this page reflects the most recent revision.
                    Continued use of the platform after a policy update constitutes acceptance of the
                    revised terms.
                  </p>
                </div>
              </section>
            </article>
          </div>
        </div>
      </div>
      <Footer />
    </>
  )
}
