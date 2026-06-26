import Link from 'next/link'

export default function PrivacyPage() {
  return (
    <div
      className="min-h-screen text-white"
      style={{
        background:
          'radial-gradient(ellipse 80% 60% at 50% -10%, rgba(255,107,53,0.10) 0%, transparent 60%), #0A0D14',
      }}
    >
      {/* Nav */}
      <nav
        className="sticky top-0 z-40 border-b border-white/[0.06] px-6 py-4 flex items-center"
        style={{
          backdropFilter: 'blur(20px) saturate(1.5)',
          background: 'rgba(10,13,20,0.85)',
        }}
      >
        <Link href="/" className="inline-flex items-center gap-2.5">
          <div
            className="w-9 h-9 rounded-xl flex items-center justify-center text-white font-black text-sm"
            style={{
              background: 'linear-gradient(135deg,#FF6B35,#00D9FF)',
              boxShadow: '0 0 20px rgba(255,107,53,0.40)',
            }}
          >
            V
          </div>
          <span className="text-xl font-bold tracking-tight text-white">
            Vantro<span style={{ color: '#FF6B35' }}>.ai</span>
          </span>
        </Link>
      </nav>

      {/* Content */}
      <main className="max-w-3xl mx-auto px-6 py-16">
        {/* Page title */}
        <div className="mb-12">
          <p className="text-xs font-semibold uppercase tracking-widest mb-3" style={{ color: '#FF6B35' }}>
            Legal
          </p>
          <h1 className="text-4xl font-bold text-white mb-3">Privacy Policy</h1>
          <p className="text-white/40 text-sm">Effective date: June 26, 2026</p>
        </div>

        <div className="space-y-12">

          {/* 1. Introduction */}
          <section>
            <h2 className="text-xl font-semibold text-white mb-4">1. Introduction</h2>
            <div className="space-y-3 text-white/60 leading-relaxed">
              <p>
                Vantro.ai (&ldquo;Vantro&rdquo;, &ldquo;we&rdquo;, &ldquo;us&rdquo;, or &ldquo;our&rdquo;) operates an AI agent platform for ecommerce businesses. This Privacy Policy explains how we collect, use, disclose, and protect information about you when you access our website at vantro.ai and use our services.
              </p>
              <p>
                This policy applies to all visitors, registered users, and customers of Vantro. By using our services you agree to the practices described here. If you do not agree, please discontinue use of the platform.
              </p>
              <p>
                We are committed to complying with applicable data protection laws, including the EU General Data Protection Regulation (&ldquo;GDPR&rdquo;) and the California Consumer Privacy Act (&ldquo;CCPA&rdquo;) as amended by the California Privacy Rights Act (&ldquo;CPRA&rdquo;).
              </p>
            </div>
          </section>

          <div className="border-t border-white/[0.07]" />

          {/* 2. Information We Collect */}
          <section>
            <h2 className="text-xl font-semibold text-white mb-4">2. Information We Collect</h2>
            <div className="space-y-5 text-white/60 leading-relaxed">
              <div>
                <p className="text-white/80 font-medium mb-1.5">Account data</p>
                <p>
                  When you register, we collect your name, email address, and password (stored as a secure hash). If you connect a store or third-party integration, we collect the credentials or tokens required for that connection.
                </p>
              </div>
              <div>
                <p className="text-white/80 font-medium mb-1.5">Usage data</p>
                <p>
                  We automatically collect information about how you interact with the platform: pages visited, agent tasks created, prompts submitted, credits consumed, timestamps, IP address, browser type, and device identifiers. This data is used to operate and improve the service.
                </p>
              </div>
              <div>
                <p className="text-white/80 font-medium mb-1.5">Payment information</p>
                <p>
                  All payment processing is handled by Stripe, Inc. We do not store full card numbers or CVV codes on our servers. We receive and store non-sensitive billing metadata from Stripe, such as the last four digits of your card, card brand, billing address, subscription status, and transaction history.
                </p>
              </div>
              <div>
                <p className="text-white/80 font-medium mb-1.5">Content you provide</p>
                <p>
                  We store the inputs you provide to AI agents (prompts, product data, brand guidelines) and the outputs generated on your behalf. This content is used solely to deliver the service to you.
                </p>
              </div>
              <div>
                <p className="text-white/80 font-medium mb-1.5">Cookies and similar technologies</p>
                <p>
                  We use essential session cookies to keep you logged in and to protect against cross-site request forgery. We do not use advertising cookies, third-party tracking pixels, or behavioural analytics cookies. See Section 8 for details.
                </p>
              </div>
            </div>
          </section>

          <div className="border-t border-white/[0.07]" />

          {/* 3. How We Use Your Information */}
          <section>
            <h2 className="text-xl font-semibold text-white mb-4">3. How We Use Your Information</h2>
            <div className="space-y-3 text-white/60 leading-relaxed">
              <p>We use the information we collect to:</p>
              <ul className="space-y-2 pl-4">
                {[
                  'Create and manage your account and authenticate your sessions.',
                  'Deliver the AI agent platform, process your prompts, and return generated content.',
                  'Process payments and manage your subscription through Stripe.',
                  'Monitor credit usage and enforce plan limits.',
                  'Detect and prevent fraud, abuse, and security incidents.',
                  'Send transactional emails (account activation, billing receipts, agent task confirmations).',
                  'Send optional product updates and announcements — you may opt out at any time.',
                  'Analyse aggregate, anonymised usage patterns to improve platform performance and features.',
                  'Comply with legal obligations, respond to lawful requests, and enforce our Terms of Service.',
                ].map((item) => (
                  <li key={item} className="flex items-start gap-2.5">
                    <span
                      className="mt-1.5 w-1.5 h-1.5 rounded-full flex-shrink-0"
                      style={{ background: '#FF6B35' }}
                    />
                    {item}
                  </li>
                ))}
              </ul>
            </div>
          </section>

          <div className="border-t border-white/[0.07]" />

          {/* 4. Legal Basis for Processing (GDPR) */}
          <section>
            <h2 className="text-xl font-semibold text-white mb-4">4. Legal Basis for Processing (GDPR)</h2>
            <p className="text-white/60 leading-relaxed mb-5">
              If you are located in the European Economic Area (EEA) or the United Kingdom, we process your personal data under the following legal bases:
            </p>
            <div className="space-y-4 text-white/60 leading-relaxed">
              <div>
                <p className="text-white/80 font-medium mb-1">Contract performance (Art. 6(1)(b) GDPR)</p>
                <p>Processing your account data, usage data, and payment metadata is necessary to provide the services you have contracted for. Without this processing we cannot operate your account.</p>
              </div>
              <div>
                <p className="text-white/80 font-medium mb-1">Legitimate interests (Art. 6(1)(f) GDPR)</p>
                <p>We process usage analytics and security logs on the basis of our legitimate interests in operating a secure, reliable platform and in understanding how the service is used. We have balanced these interests against your rights and concluded they do not override your fundamental interests.</p>
              </div>
              <div>
                <p className="text-white/80 font-medium mb-1">Legal obligation (Art. 6(1)(c) GDPR)</p>
                <p>We may process data where necessary to comply with a legal obligation, such as retaining billing records for tax purposes or responding to a lawful court order.</p>
              </div>
              <div>
                <p className="text-white/80 font-medium mb-1">Consent (Art. 6(1)(a) GDPR)</p>
                <p>Where we send optional marketing communications, we do so on the basis of your consent. You may withdraw consent at any time by clicking &ldquo;Unsubscribe&rdquo; in any such email or by contacting us at privacy@vantro.ai.</p>
              </div>
            </div>
          </section>

          <div className="border-t border-white/[0.07]" />

          {/* 5. Your Rights */}
          <section>
            <h2 className="text-xl font-semibold text-white mb-4">5. Your Rights</h2>

            <div className="space-y-6 text-white/60 leading-relaxed">
              <div>
                <p
                  className="text-sm font-semibold uppercase tracking-widest mb-3"
                  style={{ color: '#00D9FF' }}
                >
                  GDPR rights (EEA &amp; UK residents)
                </p>
                <ul className="space-y-2.5">
                  {[
                    ['Right of access', 'You may request a copy of the personal data we hold about you.'],
                    ['Right to rectification', 'You may ask us to correct inaccurate or incomplete data.'],
                    ['Right to erasure', 'You may request deletion of your personal data, subject to legal retention requirements.'],
                    ['Right to data portability', 'You may request your data in a structured, machine-readable format.'],
                    ['Right to restriction', 'You may ask us to restrict processing of your data in certain circumstances.'],
                    ['Right to object', 'You may object to processing based on legitimate interests, including for direct marketing.'],
                    ['Right to lodge a complaint', 'You have the right to file a complaint with your national data protection authority.'],
                  ].map(([right, desc]) => (
                    <li key={right} className="flex items-start gap-2.5">
                      <span
                        className="mt-1.5 w-1.5 h-1.5 rounded-full flex-shrink-0"
                        style={{ background: '#00D9FF' }}
                      />
                      <span>
                        <span className="text-white/80 font-medium">{right}:</span>{' '}{desc}
                      </span>
                    </li>
                  ))}
                </ul>
              </div>

              <div>
                <p
                  className="text-sm font-semibold uppercase tracking-widest mb-3"
                  style={{ color: '#FF6B35' }}
                >
                  CCPA rights (California residents)
                </p>
                <ul className="space-y-2.5">
                  {[
                    ['Right to know', 'You may request disclosure of the categories and specific pieces of personal information we have collected about you.'],
                    ['Right to delete', 'You may request deletion of personal information we have collected, subject to certain exceptions.'],
                    ['Right to correct', 'You may request correction of inaccurate personal information.'],
                    ['Right to opt out of sale', 'Vantro does not sell personal information. No opt-out is required, but you are entitled to this right.'],
                    ['Right to non-discrimination', 'We will not discriminate against you for exercising any CCPA rights, including by denying services or charging different prices.'],
                  ].map(([right, desc]) => (
                    <li key={right} className="flex items-start gap-2.5">
                      <span
                        className="mt-1.5 w-1.5 h-1.5 rounded-full flex-shrink-0"
                        style={{ background: '#FF6B35' }}
                      />
                      <span>
                        <span className="text-white/80 font-medium">{right}:</span>{' '}{desc}
                      </span>
                    </li>
                  ))}
                </ul>
              </div>

              <p>
                To exercise any of these rights, email{' '}
                <a
                  href="mailto:privacy@vantro.ai"
                  className="underline underline-offset-2 transition-opacity hover:opacity-70"
                  style={{ color: '#FF6B35' }}
                >
                  privacy@vantro.ai
                </a>
                . We will respond within 30 days (or 45 days where permitted by law).
              </p>
            </div>
          </section>

          <div className="border-t border-white/[0.07]" />

          {/* 6. Data Retention */}
          <section>
            <h2 className="text-xl font-semibold text-white mb-4">6. Data Retention</h2>
            <div className="space-y-3 text-white/60 leading-relaxed">
              <p>
                We retain your account data, agent content, and usage logs for as long as your account is active. When you delete your account, we begin a 90-day retention window during which data is flagged for deletion but not yet purged. This window allows for recovery in the event of accidental deletion. After 90 days, personal data is permanently deleted from production systems and queued for deletion from backups on their regular rotation cycle.
              </p>
              <p>
                Billing records and transaction logs are retained for a minimum of 7 years to comply with tax and financial reporting obligations, even after account deletion.
              </p>
              <p>
                Anonymised and aggregated usage statistics that cannot be used to identify you may be retained indefinitely for product analytics.
              </p>
            </div>
          </section>

          <div className="border-t border-white/[0.07]" />

          {/* 7. Third-Party Services */}
          <section>
            <h2 className="text-xl font-semibold text-white mb-4">7. Third-Party Services</h2>
            <p className="text-white/60 leading-relaxed mb-5">
              We share data with the following third-party sub-processors where necessary to operate the platform. Each is bound by contractual data protection obligations.
            </p>
            <div className="space-y-4">
              {[
                {
                  name: 'Stripe, Inc.',
                  role: 'Payment processing',
                  detail:
                    'Stripe processes payment card data on our behalf. Your card details are transmitted directly to Stripe and are never stored on Vantro servers. Stripe is PCI DSS Level 1 certified. Privacy policy: stripe.com/privacy.',
                },
                {
                  name: 'Anthropic, PBC',
                  role: 'AI model inference',
                  detail:
                    'Prompts and context you submit to AI agents are sent to Anthropic\'s Claude API to generate responses. Anthropic\'s API usage data practices are governed by their usage policy. We do not share identifying account information with Anthropic — only the content of agent requests.',
                },
                {
                  name: 'Vercel, Inc.',
                  role: 'Cloud hosting & edge delivery',
                  detail:
                    'Our frontend application is hosted on Vercel\'s infrastructure. Vercel may process request logs, including IP addresses, as part of its standard hosting operations. Vercel is SOC 2 Type II certified.',
                },
              ].map(({ name, role, detail }) => (
                <div
                  key={name}
                  className="rounded-xl p-5"
                  style={{
                    background: 'rgba(255,255,255,0.03)',
                    border: '1px solid rgba(255,255,255,0.07)',
                  }}
                >
                  <div className="flex items-center gap-2 mb-2">
                    <p className="text-white font-semibold text-sm">{name}</p>
                    <span
                      className="text-xs px-2 py-0.5 rounded-full"
                      style={{
                        background: 'rgba(255,107,53,0.15)',
                        color: '#FF6B35',
                        border: '1px solid rgba(255,107,53,0.25)',
                      }}
                    >
                      {role}
                    </span>
                  </div>
                  <p className="text-white/55 text-sm leading-relaxed">{detail}</p>
                </div>
              ))}
            </div>
            <p className="text-white/60 text-sm leading-relaxed mt-5">
              We do not sell personal data to any third party for advertising or marketing purposes.
            </p>
          </section>

          <div className="border-t border-white/[0.07]" />

          {/* 8. Cookies */}
          <section>
            <h2 className="text-xl font-semibold text-white mb-4">8. Cookies</h2>
            <div className="space-y-3 text-white/60 leading-relaxed">
              <p>
                Vantro uses only essential cookies. Essential cookies are strictly necessary for the platform to function — they maintain your authenticated session and protect against security attacks such as CSRF. These cookies are set by vantro.ai and are not used for tracking.
              </p>
              <p>
                We do not use third-party advertising cookies, social media tracking pixels, or behavioural analytics services that place cookies on your device. We do not use Google Analytics, Facebook Pixel, or similar tracking technologies.
              </p>
              <p>
                Because we only use essential cookies, no cookie consent banner is required under ePrivacy Directive exemptions for strictly necessary cookies. If you block essential cookies via your browser settings, the platform will not function correctly.
              </p>
            </div>
          </section>

          <div className="border-t border-white/[0.07]" />

          {/* 9. California Residents (CCPA) */}
          <section>
            <h2 className="text-xl font-semibold text-white mb-2">9. California Residents</h2>
            <p
              className="text-xs font-semibold uppercase tracking-widest mb-4"
              style={{ color: '#FF6B35' }}
            >
              CCPA / CPRA Notice
            </p>
            <div className="space-y-3 text-white/60 leading-relaxed">
              <p>
                <span className="text-white font-semibold">We do not sell personal information.</span> Vantro has not sold and does not sell personal information to third parties as defined under the CCPA. You therefore do not need to opt out of a sale.
              </p>
              <p>
                We do not share personal information with third parties for cross-context behavioural advertising purposes.
              </p>
              <p>
                In the preceding 12 months, we have collected the following categories of personal information: identifiers (name, email, IP address), commercial information (subscription and billing records), internet or other electronic network activity information (usage logs), and inferences drawn to create a profile about service usage patterns.
              </p>
              <p>
                We collect this information for the business purposes described in Section 3. We disclose personal information only to the service providers listed in Section 7.
              </p>
              <p>
                To submit a verifiable consumer request under the CCPA, or to designate an authorised agent to act on your behalf, contact us at{' '}
                <a
                  href="mailto:privacy@vantro.ai"
                  className="underline underline-offset-2 transition-opacity hover:opacity-70"
                  style={{ color: '#FF6B35' }}
                >
                  privacy@vantro.ai
                </a>
                . We will not discriminate against you for exercising your CCPA rights.
              </p>
            </div>
          </section>

          <div className="border-t border-white/[0.07]" />

          {/* 10. Contact */}
          <section>
            <h2 className="text-xl font-semibold text-white mb-4">10. Contact</h2>
            <div className="space-y-3 text-white/60 leading-relaxed">
              <p>
                For all privacy-related enquiries, requests to exercise your rights, or concerns about this policy, please contact our privacy team:
              </p>
              <div
                className="rounded-xl px-5 py-4 text-sm"
                style={{
                  background: 'rgba(255,107,53,0.06)',
                  border: '1px solid rgba(255,107,53,0.18)',
                }}
              >
                <p className="text-white font-medium mb-1">Vantro.ai — Privacy</p>
                <a
                  href="mailto:privacy@vantro.ai"
                  className="transition-opacity hover:opacity-70"
                  style={{ color: '#FF6B35' }}
                >
                  privacy@vantro.ai
                </a>
              </div>
              <p>
                We will acknowledge your request within 5 business days and aim to resolve it within 30 days. If we require more time, we will inform you of the reason and the expected completion date.
              </p>
              <p>
                If you are an EEA resident and believe we have not handled your data correctly, you also have the right to lodge a complaint with your local supervisory authority.
              </p>
            </div>
          </section>

          <div className="border-t border-white/[0.07]" />

          {/* Footer note */}
          <p className="text-white/25 text-xs leading-relaxed">
            We may update this Privacy Policy from time to time. When we do, we will revise the &ldquo;Effective date&rdquo; at the top of this page. Material changes will be communicated to registered users by email at least 14 days before they take effect.
          </p>

        </div>
      </main>
    </div>
  )
}
