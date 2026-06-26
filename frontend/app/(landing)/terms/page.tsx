import Link from 'next/link';

const ORANGE = '#FF6B35';
const CYAN = '#00D9FF';
const BG = '#0A0D14';

function Section({ id, title, children }: { id: string; title: string; children: React.ReactNode }) {
  return (
    <section id={id} className="mb-10">
      <h2 className="text-xl font-bold text-white mb-3" style={{ borderLeft: `3px solid ${ORANGE}`, paddingLeft: '0.75rem' }}>
        {title}
      </h2>
      <div className="text-white/70 leading-relaxed space-y-3 text-sm">
        {children}
      </div>
    </section>
  );
}

export default function TermsPage() {
  return (
    <div className="min-h-screen text-white" style={{ background: BG }}>
      {/* Nav */}
      <nav
        className="sticky top-0 z-40 border-b px-6 py-4 flex items-center"
        style={{ borderColor: 'rgba(255,255,255,0.06)', backdropFilter: 'blur(20px) saturate(1.5)', background: 'rgba(10,13,20,0.88)' }}
      >
        <Link href="/" className="flex items-center gap-2.5 group">
          <div
            className="w-7 h-7 rounded-lg flex items-center justify-center text-white font-black text-xs"
            style={{ background: `linear-gradient(135deg,${ORANGE},${CYAN})`, boxShadow: `0 0 16px rgba(255,107,53,0.40)` }}
          >
            V
          </div>
          <span className="text-lg font-bold tracking-tight">
            Vantro<span style={{ color: ORANGE }}>.ai</span>
          </span>
        </Link>
      </nav>

      {/* Body */}
      <main className="max-w-3xl mx-auto px-6 py-16">
        {/* Page header */}
        <div className="mb-12">
          <p className="text-xs font-semibold uppercase tracking-widest mb-3" style={{ color: ORANGE }}>
            Legal
          </p>
          <h1 className="text-4xl font-bold text-white mb-3 tracking-tight">Terms of Service</h1>
          <p className="text-sm" style={{ color: 'rgba(255,255,255,0.40)' }}>
            Effective date: <span className="text-white">June 26, 2026</span>
          </p>
          <p className="mt-4 text-sm leading-relaxed" style={{ color: 'rgba(255,255,255,0.55)' }}>
            Please read these Terms of Service (&quot;Terms&quot;) carefully before using Vantro.ai. By accessing or using
            the platform, you agree to be bound by these Terms. If you do not agree, do not use the service.
          </p>
        </div>

        <div
          className="rounded-2xl px-8 py-8 mb-10"
          style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.07)' }}
        >
          {/* 1 */}
          <Section id="acceptance" title="1. Acceptance of Terms">
            <p>
              By creating an account or otherwise accessing Vantro.ai (&quot;Vantro&quot;, &quot;we&quot;, &quot;us&quot;, or &quot;our&quot;), you
              (&quot;you&quot; or &quot;User&quot;) confirm that you have read, understood, and agree to these Terms and our{' '}
              <Link href="/privacy" className="underline underline-offset-2 transition-colors hover:opacity-80" style={{ color: CYAN }}>
                Privacy Policy
              </Link>
              . These Terms form a legally binding agreement between you and Vantro Pty Ltd.
            </p>
            <p>
              If you are accepting on behalf of an organisation, you represent that you have authority to bind that
              organisation to these Terms.
            </p>
          </Section>

          {/* 2 */}
          <Section id="description" title="2. Description of Service">
            <p>
              Vantro.ai is an AI agent platform designed for ecommerce businesses. The platform provides access to
              22 specialised AI agents spanning content creation, SEO, paid advertising, email marketing, lead
              generation, customer success, growth strategy, competitive intelligence, and more.
            </p>
            <p>
              Agents are accessed via a credit-based system. Credits are consumed when tasks are run and when
              AI-generated video or other media is produced. The platform is delivered as a software-as-a-service
              (SaaS) product and is subject to reasonable maintenance windows and updates.
            </p>
          </Section>

          {/* 3 */}
          <Section id="registration" title="3. Account Registration">
            <p>
              To use Vantro you must register for an account. You agree to provide accurate, complete, and
              current information during registration and to keep that information up to date.
            </p>
            <p>
              You may register only one account per individual or organisation. You are solely responsible for
              maintaining the confidentiality of your login credentials and for all activity that occurs under your
              account. Notify us immediately at{' '}
              <a href="mailto:legal@vantro.ai" className="underline underline-offset-2" style={{ color: CYAN }}>
                legal@vantro.ai
              </a>{' '}
              if you suspect unauthorised access.
            </p>
            <p>
              We reserve the right to suspend or terminate accounts that contain false information or that are
              used in violation of these Terms.
            </p>
          </Section>

          {/* 4 */}
          <Section id="billing" title="4. Subscription & Billing">
            <p>Vantro offers the following paid subscription plans, billed monthly:</p>
            <ul className="list-none space-y-2 pl-0 mt-2">
              {[
                { plan: 'Starter', price: '$99 / month', detail: '50 credits included' },
                { plan: 'Growth', price: '$279 / month', detail: '150 credits included' },
                { plan: 'Business', price: '$399 / month', detail: '300 credits included' },
              ].map(({ plan, price, detail }) => (
                <li key={plan} className="flex items-start gap-3">
                  <span className="mt-0.5 shrink-0 w-1.5 h-1.5 rounded-full" style={{ background: ORANGE, marginTop: '0.45rem' }} />
                  <span>
                    <span className="font-semibold text-white">{plan}</span>{' — '}{price} &nbsp;
                    <span style={{ color: 'rgba(255,255,255,0.40)' }}>({detail})</span>
                  </span>
                </li>
              ))}
            </ul>
            <p className="mt-3">
              All payments are processed securely via Stripe. Your subscription renews automatically on the same
              day each month unless cancelled. Credits reset at the start of each billing cycle and do not roll over.
            </p>
            <p>
              You may cancel your subscription at any time from your billing dashboard. Cancellation takes effect
              at the end of the current billing period. <strong className="text-white">No refunds are issued for
              partially used billing cycles or consumed credits.</strong> One-time credit top-up purchases are also
              non-refundable once credits have been applied to your account.
            </p>
            <p>
              We reserve the right to update pricing with at least 30 days&apos; notice to the email address on your
              account. Continued use after the effective date constitutes acceptance of the new pricing.
            </p>
          </Section>

          {/* 5 */}
          <Section id="acceptable-use" title="5. Acceptable Use">
            <p>You agree not to use Vantro to:</p>
            <ul className="space-y-2 mt-2">
              {[
                'Engage in or facilitate any illegal activity, including but not limited to fraud, spam, or copyright infringement.',
                'Scrape, crawl, or systematically harvest data from the platform or its outputs beyond your own authorised usage.',
                'Resell, sublicense, or otherwise grant third parties access to the platform or your account credentials.',
                'Abuse, overload, or attempt to circumvent usage limits or credit systems.',
                'Use AI agents to generate content that is defamatory, discriminatory, or otherwise harmful.',
                'Attempt to reverse-engineer, decompile, or extract proprietary logic from Vantro\'s AI models or infrastructure.',
              ].map((item, i) => (
                <li key={i} className="flex items-start gap-3 text-sm">
                  <span className="shrink-0 w-1.5 h-1.5 rounded-full mt-[0.45rem]" style={{ background: ORANGE }} />
                  {item}
                </li>
              ))}
            </ul>
            <p className="mt-3">
              Violations of this section may result in immediate account suspension or termination without refund.
            </p>
          </Section>

          {/* 6 */}
          <Section id="ip" title="6. Intellectual Property">
            <p>
              <strong className="text-white">Vantro&apos;s platform:</strong> All software, models, interfaces, trademarks, and
              branding that comprise Vantro.ai are and remain the exclusive intellectual property of Vantro Pty Ltd.
              These Terms do not transfer any ownership rights to you.
            </p>
            <p>
              <strong className="text-white">Your content:</strong> You retain ownership of all content, data, and
              materials you upload to or create through the platform (&quot;User Content&quot;). By using the platform you
              grant Vantro a limited, non-exclusive, royalty-free licence to process your User Content solely for
              the purpose of delivering the service to you. We do not use your User Content to train our models
              without your explicit consent.
            </p>
          </Section>

          {/* 7 */}
          <Section id="ai-content" title="7. AI-Generated Content">
            <p>
              Outputs produced by Vantro&apos;s AI agents (&quot;AI Outputs&quot;) are generated automatically and may not
              always be accurate, complete, or suitable for your specific context. You are solely responsible for
              reviewing, editing, and making decisions based on AI Outputs.
            </p>
            <p>
              We do not guarantee that AI Outputs are free from errors, bias, or legal risk. Before publishing or
              acting on any AI Output, you should verify its accuracy and compliance with applicable laws and
              regulations in your jurisdiction.
            </p>
            <p>
              Vantro disclaims all liability for any harm arising from your reliance on or use of AI Outputs.
            </p>
          </Section>

          {/* 8 */}
          <Section id="liability" title="8. Limitation of Liability">
            <p>
              To the maximum extent permitted by applicable law, Vantro&apos;s total cumulative liability to you for
              any claims arising under or related to these Terms shall not exceed the fees you paid to Vantro in
              the <strong className="text-white">three (3) months immediately preceding</strong> the event giving rise to the claim.
            </p>
            <p>
              In no event shall Vantro be liable for any indirect, incidental, special, consequential, or punitive
              damages, including loss of profits, data, or business opportunities, even if advised of the
              possibility of such damages.
            </p>
            <p>
              The platform is provided &quot;as is&quot; and &quot;as available&quot; without warranties of any kind, express or
              implied, including but not limited to merchantability, fitness for a particular purpose, or
              non-infringement.
            </p>
          </Section>

          {/* 9 */}
          <Section id="termination" title="9. Termination">
            <p>
              <strong className="text-white">By you:</strong> You may cancel your account at any time via your billing
              dashboard. Cancellation stops future charges but does not entitle you to a refund for the current
              billing period.
            </p>
            <p>
              <strong className="text-white">By us:</strong> We may suspend or terminate your account immediately,
              without notice or refund, if you materially breach these Terms, engage in fraudulent activity, or
              your use poses a risk to other users or the platform&apos;s integrity. We may also terminate accounts
              that have been inactive for more than 12 consecutive months after providing 30 days&apos; notice.
            </p>
            <p>
              Upon termination, your right to access the platform ceases immediately. Sections 6, 7, 8, and 10
              survive termination.
            </p>
          </Section>

          {/* 10 */}
          <Section id="governing-law" title="10. Governing Law">
            <p>
              These Terms are governed by and construed in accordance with the laws of the state of Victoria,
              Australia, without regard to conflict of law principles. You irrevocably submit to the exclusive
              jurisdiction of the courts of Victoria, Australia, for resolution of any dispute arising under or
              in connection with these Terms.
            </p>
          </Section>

          {/* 11 */}
          <Section id="contact" title="11. Contact">
            <p>
              For legal enquiries, notices, or questions regarding these Terms, please contact us at:
            </p>
            <div
              className="mt-3 rounded-xl px-5 py-4 text-sm"
              style={{ background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.08)' }}
            >
              <p className="text-white font-semibold">Vantro Pty Ltd</p>
              <p className="mt-1" style={{ color: 'rgba(255,255,255,0.55)' }}>
                Email:{' '}
                <a href="mailto:legal@vantro.ai" className="underline underline-offset-2 transition-opacity hover:opacity-80" style={{ color: CYAN }}>
                  legal@vantro.ai
                </a>
              </p>
            </div>
          </Section>
        </div>

        {/* Footer */}
        <footer className="border-t pt-8" style={{ borderColor: 'rgba(255,255,255,0.07)' }}>
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4 text-xs" style={{ color: 'rgba(255,255,255,0.35)' }}>
            <p>© {new Date().getFullYear()} Vantro Pty Ltd. All rights reserved.</p>
            <div className="flex items-center gap-5">
              <Link href="/privacy" className="hover:text-white transition-colors">Privacy Policy</Link>
              <Link href="/terms" className="hover:text-white transition-colors" style={{ color: 'rgba(255,255,255,0.60)' }}>Terms of Service</Link>
              <Link href="/privacy#ccpa" className="hover:text-white transition-colors">CCPA</Link>
              <Link href="/privacy#gdpr" className="hover:text-white transition-colors">GDPR</Link>
            </div>
          </div>
        </footer>
      </main>
    </div>
  );
}
