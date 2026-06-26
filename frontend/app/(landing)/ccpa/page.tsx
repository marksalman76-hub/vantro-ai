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

export default function CcpaPage() {
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
          <h1 className="text-4xl font-bold text-white mb-3 tracking-tight">CCPA Privacy Rights</h1>
          <p className="text-sm" style={{ color: 'rgba(255,255,255,0.40)' }}>
            Last updated: <span className="text-white">June 2026</span>
          </p>
          <p className="mt-4 text-sm leading-relaxed" style={{ color: 'rgba(255,255,255,0.55)' }}>
            This page describes the rights available to California residents under the California Consumer
            Privacy Act of 2018 (&quot;CCPA&quot;), as amended by the California Privacy Rights Act (&quot;CPRA&quot;). If you
            are a resident of California, you have specific rights regarding your personal information.
          </p>
        </div>

        <div
          className="rounded-2xl px-8 py-8 mb-10"
          style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.07)' }}
        >
          {/* 1 */}
          <Section id="applicability" title="1. Applicability">
            <p>
              The rights described in this notice apply only to individuals who are residents of the State of
              California. If you are not a California resident, please refer to our general{' '}
              <Link href="/privacy" className="underline underline-offset-2 transition-colors hover:opacity-80" style={{ color: CYAN }}>
                Privacy Policy
              </Link>{' '}
              for information about how we handle personal data.
            </p>
            <p>
              Vantro Pty Ltd (&quot;Vantro&quot;, &quot;we&quot;, &quot;us&quot;, or &quot;our&quot;) is committed to complying with the CCPA
              and to respecting the privacy rights of California consumers. This page supplements our
              Privacy Policy and addresses CCPA-specific requirements.
            </p>
          </Section>

          {/* 2 */}
          <Section id="your-rights" title="2. Your Rights Under the CCPA">
            <p>As a California resident, you have the following rights with respect to your personal information:</p>

            <div className="mt-4 space-y-4">
              {[
                {
                  title: 'Right to Know',
                  color: ORANGE,
                  text: 'You have the right to request that we disclose what personal information we collect, use, disclose, and sell about you. This includes the categories of personal information collected, the purposes for collection, the categories of third parties with whom we share it, and the specific pieces of personal information we hold about you.',
                },
                {
                  title: 'Right to Delete',
                  color: CYAN,
                  text: 'You have the right to request that we delete personal information we have collected from you, subject to certain exceptions. We may retain information where necessary to complete a transaction, detect security incidents, comply with a legal obligation, or exercise free speech, among other permitted purposes.',
                },
                {
                  title: 'Right to Opt-Out of Sale or Sharing',
                  color: '#A855F7',
                  text: 'You have the right to opt out of the sale or sharing of your personal information with third parties for cross-context behavioural advertising. We do not sell your personal information in the traditional sense. However, if any of our advertising practices qualify as "sharing" under the CPRA, you may opt out using the "Do Not Sell or Share My Personal Information" link on our website.',
                },
                {
                  title: 'Right to Non-Discrimination',
                  color: '#22C55E',
                  text: 'We will not discriminate against you for exercising any of your CCPA rights. We will not deny you goods or services, charge you different prices, provide a different level of quality of service, or suggest that you may receive a different price or quality because you exercised your rights.',
                },
                {
                  title: 'Right to Correct',
                  color: '#F59E0B',
                  text: 'You have the right to request that we correct inaccurate personal information that we maintain about you. We will use commercially reasonable efforts to correct such information upon a verified request.',
                },
                {
                  title: 'Right to Limit Use of Sensitive Personal Information',
                  color: '#EC4899',
                  text: 'If we collect sensitive personal information (such as login credentials, financial account information, or precise geolocation), you have the right to limit our use and disclosure of that information to what is necessary to perform the services you have requested.',
                },
              ].map(({ title, color, text }) => (
                <div
                  key={title}
                  className="rounded-xl px-5 py-4"
                  style={{ background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.08)' }}
                >
                  <p className="font-semibold text-white mb-1 flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full shrink-0" style={{ background: color }} />
                    {title}
                  </p>
                  <p style={{ color: 'rgba(255,255,255,0.60)' }}>{text}</p>
                </div>
              ))}
            </div>
          </Section>

          {/* 3 */}
          <Section id="how-to-exercise" title="3. How to Exercise Your Rights">
            <p>
              To exercise any of the rights described above, you or your authorised agent may submit a
              verifiable consumer request by any of the following methods:
            </p>
            <ul className="space-y-2 mt-2">
              {[
                'Email us at privacy@vantro.ai with the subject line "CCPA Rights Request".',
                'Log in to your Vantro account and submit a request through your account settings under "Privacy & Data".',
                'If acting through an authorised agent, the agent must provide written permission signed by you and we may require you to verify your identity directly with us.',
              ].map((item, i) => (
                <li key={i} className="flex items-start gap-3 text-sm">
                  <span className="shrink-0 w-1.5 h-1.5 rounded-full mt-[0.45rem]" style={{ background: ORANGE }} />
                  {item}
                </li>
              ))}
            </ul>
            <p className="mt-3">
              We will respond to a verifiable consumer request within <strong className="text-white">45 days</strong> of
              receipt. If we require additional time (up to a further 45 days), we will inform you of the
              reason and extension period in writing. We do not charge a fee for processing your request
              unless it is excessive, repetitive, or manifestly unfounded.
            </p>
            <p>
              To verify your identity, we may ask you to provide information that matches what we already
              hold on file, such as your email address, account details, or the last four digits of a payment
              method. We will not use the information you provide solely to verify your identity for any
              other purpose.
            </p>
          </Section>

          {/* 4 */}
          <Section id="personal-information-collected" title="4. Categories of Personal Information Collected">
            <p>
              In the preceding 12 months, we have collected the following categories of personal information
              from California consumers:
            </p>
            <ul className="space-y-2 mt-2">
              {[
                'Identifiers — such as name, email address, IP address, and account username.',
                'Commercial information — including subscription plan, purchase history, and credit usage.',
                'Internet or network activity — such as browsing history within the platform, feature interactions, and log data.',
                'Inferences — derived from usage data to understand preferences and improve the platform experience.',
                'Professional or employment-related information — such as business name and industry, if provided.',
              ].map((item, i) => (
                <li key={i} className="flex items-start gap-3 text-sm">
                  <span className="shrink-0 w-1.5 h-1.5 rounded-full mt-[0.45rem]" style={{ background: CYAN }} />
                  {item}
                </li>
              ))}
            </ul>
            <p className="mt-3">
              We collect this information for business purposes including providing and improving our services,
              processing payments, communicating with you, security and fraud prevention, and complying with
              legal obligations.
            </p>
          </Section>

          {/* 5 */}
          <Section id="contact" title="5. Contact">
            <p>
              For all CCPA-related enquiries, requests, or questions, please contact our Privacy team:
            </p>
            <div
              className="mt-3 rounded-xl px-5 py-4 text-sm"
              style={{ background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.08)' }}
            >
              <p className="text-white font-semibold">Vantro Pty Ltd — Privacy Team</p>
              <p className="mt-1" style={{ color: 'rgba(255,255,255,0.55)' }}>
                Email:{' '}
                <a href="mailto:privacy@vantro.ai" className="underline underline-offset-2 transition-opacity hover:opacity-80" style={{ color: CYAN }}>
                  privacy@vantro.ai
                </a>
              </p>
              <p className="mt-1" style={{ color: 'rgba(255,255,255,0.40)' }}>
                Please include &quot;CCPA Rights Request&quot; in the subject line of your email.
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
              <Link href="/terms" className="hover:text-white transition-colors">Terms of Service</Link>
              <Link href="/cookies" className="hover:text-white transition-colors">Cookie Policy</Link>
              <Link href="/gdpr" className="hover:text-white transition-colors">GDPR</Link>
            </div>
          </div>
        </footer>
      </main>
    </div>
  );
}
