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

export default function GdprPage() {
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
          <h1 className="text-4xl font-bold text-white mb-3 tracking-tight">GDPR Rights</h1>
          <p className="text-sm" style={{ color: 'rgba(255,255,255,0.40)' }}>
            Last updated: <span className="text-white">June 2026</span>
          </p>
          <p className="mt-4 text-sm leading-relaxed" style={{ color: 'rgba(255,255,255,0.55)' }}>
            This page sets out the rights available to individuals located in the European Union and European
            Economic Area (&quot;EU/EEA&quot;) under the General Data Protection Regulation (EU) 2016/679 (&quot;GDPR&quot;).
            Vantro Pty Ltd is committed to processing your personal data lawfully, fairly, and transparently
            in accordance with the GDPR.
          </p>
        </div>

        <div
          className="rounded-2xl px-8 py-8 mb-10"
          style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.07)' }}
        >
          {/* 1 */}
          <Section id="applicability" title="1. Applicability">
            <p>
              The rights and information described on this page apply to individuals who reside in the EU or
              EEA and whose personal data is processed by Vantro. If you are not located in the EU/EEA,
              please refer to our general{' '}
              <Link href="/privacy" className="underline underline-offset-2 transition-colors hover:opacity-80" style={{ color: CYAN }}>
                Privacy Policy
              </Link>{' '}
              for information about how we handle personal data globally.
            </p>
            <p>
              For the purposes of the GDPR, Vantro Pty Ltd acts as the <strong className="text-white">data controller</strong> with
              respect to personal data collected from EU/EEA residents who use Vantro.ai.
            </p>
          </Section>

          {/* 2 */}
          <Section id="lawful-basis" title="2. Lawful Basis for Processing">
            <p>
              We only process your personal data where we have a valid lawful basis to do so. Depending on
              the context, we rely on one or more of the following legal bases under Article 6 of the GDPR:
            </p>
            <div className="mt-4 space-y-4">
              {[
                {
                  basis: 'Contractual Necessity',
                  color: ORANGE,
                  text: 'Processing is necessary to perform our contract with you — for example, to create and manage your account, process payments, provide access to AI agents, and deliver the services you have subscribed to.',
                },
                {
                  basis: 'Legitimate Interests',
                  color: CYAN,
                  text: 'We process certain data where it is in our legitimate interests and those interests are not overridden by your rights — for example, to improve the platform, detect fraud and abuse, and conduct internal analytics.',
                },
                {
                  basis: 'Legal Obligation',
                  color: '#22C55E',
                  text: 'We may process data where required by applicable law — for example, to comply with tax regulations, respond to lawful requests by public authorities, or retain transaction records.',
                },
                {
                  basis: 'Consent',
                  color: '#A855F7',
                  text: 'Where we rely on consent — for example, for marketing emails or optional analytics cookies — you may withdraw your consent at any time without affecting the lawfulness of processing carried out before withdrawal.',
                },
              ].map(({ basis, color, text }) => (
                <div
                  key={basis}
                  className="rounded-xl px-5 py-4"
                  style={{ background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.08)' }}
                >
                  <p className="font-semibold text-white mb-1 flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full shrink-0" style={{ background: color }} />
                    {basis}
                  </p>
                  <p style={{ color: 'rgba(255,255,255,0.60)' }}>{text}</p>
                </div>
              ))}
            </div>
          </Section>

          {/* 3 */}
          <Section id="your-rights" title="3. Your Rights Under the GDPR">
            <p>
              As a data subject under the GDPR, you have the following rights in relation to your personal data:
            </p>
            <div className="mt-4 space-y-4">
              {[
                {
                  right: 'Right of Access (Art. 15)',
                  color: ORANGE,
                  text: 'You have the right to obtain confirmation of whether we process personal data about you, and if so, to receive a copy of that data along with information about how it is processed.',
                },
                {
                  right: 'Right to Rectification (Art. 16)',
                  color: CYAN,
                  text: 'You have the right to have inaccurate personal data corrected without undue delay. You may also request that incomplete data be completed, including by providing a supplementary statement.',
                },
                {
                  right: 'Right to Erasure (Art. 17)',
                  color: '#22C55E',
                  text: 'You have the right to request deletion of your personal data where it is no longer necessary for the purposes for which it was collected, you withdraw consent (where consent is the basis), or you object to processing and there are no overriding legitimate grounds, among other circumstances.',
                },
                {
                  right: 'Right to Data Portability (Art. 20)',
                  color: '#A855F7',
                  text: 'Where processing is based on consent or contract and carried out by automated means, you have the right to receive your personal data in a structured, commonly used, and machine-readable format, and to transmit that data to another controller where technically feasible.',
                },
                {
                  right: 'Right to Object (Art. 21)',
                  color: '#F59E0B',
                  text: 'You have the right to object to processing of your personal data based on our legitimate interests, including profiling based on those interests. We will stop processing unless we can demonstrate compelling legitimate grounds that override your interests, or the processing is for the establishment or defence of legal claims.',
                },
                {
                  right: 'Right to Restriction (Art. 18)',
                  color: '#EC4899',
                  text: 'You have the right to request that we restrict processing of your personal data in certain circumstances — for example, where you contest the accuracy of the data or have objected to processing pending verification of our legitimate grounds.',
                },
              ].map(({ right, color, text }) => (
                <div
                  key={right}
                  className="rounded-xl px-5 py-4"
                  style={{ background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.08)' }}
                >
                  <p className="font-semibold text-white mb-1 flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full shrink-0" style={{ background: color }} />
                    {right}
                  </p>
                  <p style={{ color: 'rgba(255,255,255,0.60)' }}>{text}</p>
                </div>
              ))}
            </div>
            <p className="mt-4">
              To exercise any of these rights, please contact our Data Protection Officer using the details
              in Section 4 below. We will respond to all verifiable requests within{' '}
              <strong className="text-white">30 days</strong>. Where requests are complex or numerous, we may
              extend this period by a further two months, in which case we will notify you promptly.
            </p>
          </Section>

          {/* 4 */}
          <Section id="dpo" title="4. Data Protection Officer">
            <p>
              We have appointed a Data Protection Officer (&quot;DPO&quot;) who is responsible for overseeing compliance
              with this policy and the GDPR. If you have any questions about how we handle your personal data,
              wish to exercise your rights, or have a concern about our data practices, please contact our DPO:
            </p>
            <div
              className="mt-3 rounded-xl px-5 py-4 text-sm"
              style={{ background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.08)' }}
            >
              <p className="text-white font-semibold">Data Protection Officer — Vantro Pty Ltd</p>
              <p className="mt-1" style={{ color: 'rgba(255,255,255,0.55)' }}>
                Email:{' '}
                <a href="mailto:dpo@vantro.ai" className="underline underline-offset-2 transition-opacity hover:opacity-80" style={{ color: CYAN }}>
                  dpo@vantro.ai
                </a>
              </p>
              <p className="mt-1" style={{ color: 'rgba(255,255,255,0.40)' }}>
                Please include &quot;GDPR Rights Request&quot; in the subject line of your email.
              </p>
            </div>
          </Section>

          {/* 5 */}
          <Section id="international-transfers" title="5. International Data Transfers">
            <p>
              Vantro Pty Ltd is incorporated in Australia. When we transfer personal data from the EU/EEA to
              Australia or other third countries, we ensure that appropriate safeguards are in place in
              accordance with Chapter V of the GDPR. These safeguards may include:
            </p>
            <ul className="space-y-2 mt-2">
              {[
                'Standard Contractual Clauses (SCCs) approved by the European Commission.',
                'Adequacy decisions — Australia has frameworks that align with GDPR principles, and we rely on SCCs where an adequacy decision is not yet in effect.',
                'Binding Corporate Rules or other approved transfer mechanisms where applicable.',
              ].map((item, i) => (
                <li key={i} className="flex items-start gap-3 text-sm">
                  <span className="shrink-0 w-1.5 h-1.5 rounded-full mt-[0.45rem]" style={{ background: ORANGE }} />
                  {item}
                </li>
              ))}
            </ul>
            <p className="mt-3">
              You may request a copy of the relevant transfer mechanism by contacting our DPO at{' '}
              <a href="mailto:dpo@vantro.ai" className="underline underline-offset-2 transition-opacity hover:opacity-80" style={{ color: CYAN }}>
                dpo@vantro.ai
              </a>.
            </p>
          </Section>

          {/* 6 */}
          <Section id="right-to-complain" title="6. Right to Complain to a Supervisory Authority">
            <p>
              If you believe that our processing of your personal data violates the GDPR, you have the right
              to lodge a complaint with a supervisory authority. You may do so in the EU/EEA member state
              where you reside, where you work, or where the alleged infringement took place.
            </p>
            <p>
              A list of EU supervisory authorities and their contact details is available on the European Data
              Protection Board (EDPB) website at{' '}
              <a
                href="https://www.edpb.europa.eu"
                target="_blank"
                rel="noopener noreferrer"
                className="underline underline-offset-2 transition-opacity hover:opacity-80"
                style={{ color: CYAN }}
              >
                www.edpb.europa.eu
              </a>.
            </p>
            <p>
              We would, however, welcome the opportunity to address your concerns directly before you approach
              a supervisory authority. Please contact our DPO in the first instance.
            </p>
          </Section>

          {/* 7 */}
          <Section id="retention" title="7. Data Retention">
            <p>
              We retain personal data only for as long as necessary to fulfil the purposes for which it was
              collected, including to satisfy legal, accounting, or reporting requirements. When determining
              the appropriate retention period, we consider the amount and sensitivity of the data, the
              potential risk of harm from unauthorised use, the purposes for which we process it, and whether
              those purposes can be achieved by other means.
            </p>
            <p>
              Upon account closure, we will delete or anonymise your personal data within{' '}
              <strong className="text-white">90 days</strong>, except where we are required to retain it
              to comply with a legal obligation, resolve disputes, or enforce our agreements.
            </p>
          </Section>

          {/* 8 */}
          <Section id="contact" title="8. Contact">
            <p>
              For all GDPR-related enquiries, to exercise your rights, or for any questions about our data
              protection practices, please contact:
            </p>
            <div
              className="mt-3 rounded-xl px-5 py-4 text-sm"
              style={{ background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.08)' }}
            >
              <p className="text-white font-semibold">Vantro Pty Ltd</p>
              <p className="mt-1" style={{ color: 'rgba(255,255,255,0.55)' }}>
                DPO Email:{' '}
                <a href="mailto:dpo@vantro.ai" className="underline underline-offset-2 transition-opacity hover:opacity-80" style={{ color: CYAN }}>
                  dpo@vantro.ai
                </a>
              </p>
              <p className="mt-1" style={{ color: 'rgba(255,255,255,0.55)' }}>
                General Privacy:{' '}
                <a href="mailto:privacy@vantro.ai" className="underline underline-offset-2 transition-opacity hover:opacity-80" style={{ color: CYAN }}>
                  privacy@vantro.ai
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
              <Link href="/terms" className="hover:text-white transition-colors">Terms of Service</Link>
              <Link href="/cookies" className="hover:text-white transition-colors">Cookie Policy</Link>
              <Link href="/ccpa" className="hover:text-white transition-colors">CCPA</Link>
            </div>
          </div>
        </footer>
      </main>
    </div>
  );
}
