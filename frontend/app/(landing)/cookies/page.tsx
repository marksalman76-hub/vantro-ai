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

export default function CookiesPage() {
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
          <h1 className="text-4xl font-bold text-white mb-3 tracking-tight">Cookie Policy</h1>
          <p className="text-sm" style={{ color: 'rgba(255,255,255,0.40)' }}>
            Last updated: <span className="text-white">June 2026</span>
          </p>
          <p className="mt-4 text-sm leading-relaxed" style={{ color: 'rgba(255,255,255,0.55)' }}>
            This Cookie Policy explains how Vantro Pty Ltd (&quot;Vantro&quot;, &quot;we&quot;, &quot;us&quot;, or &quot;our&quot;) uses
            cookies and similar tracking technologies when you visit or use Vantro.ai. By continuing to use our
            platform, you consent to our use of cookies as described in this policy.
          </p>
        </div>

        <div
          className="rounded-2xl px-8 py-8 mb-10"
          style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.07)' }}
        >
          {/* 1 */}
          <Section id="what-are-cookies" title="1. What Are Cookies">
            <p>
              Cookies are small text files that are placed on your device (computer, smartphone, or tablet) when
              you visit a website. They are widely used to make websites work, to work more efficiently, and to
              provide information to site owners.
            </p>
            <p>
              Cookies allow us to recognise your device and store information about your preferences or past
              actions on our platform. They help us deliver a faster, more personalised experience each time
              you return.
            </p>
            <p>
              In addition to cookies, we may also use web beacons, pixel tags, and similar tracking technologies.
              For simplicity, we refer to all such technologies collectively as &quot;cookies&quot; throughout this policy.
            </p>
          </Section>

          {/* 2 */}
          <Section id="types-we-use" title="2. Types of Cookies We Use">
            <p>We use the following categories of cookies on Vantro.ai:</p>

            <div className="mt-4 space-y-5">
              {/* Essential */}
              <div
                className="rounded-xl px-5 py-4"
                style={{ background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.08)' }}
              >
                <p className="font-semibold text-white mb-1 flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full shrink-0" style={{ background: ORANGE }} />
                  Essential Cookies
                </p>
                <p style={{ color: 'rgba(255,255,255,0.60)' }}>
                  These cookies are strictly necessary for the platform to function. They enable core features
                  such as user authentication, session management, security tokens, and billing portal access.
                  Without these cookies, services you have requested cannot be provided. You cannot opt out
                  of essential cookies while continuing to use Vantro.ai.
                </p>
              </div>

              {/* Analytics */}
              <div
                className="rounded-xl px-5 py-4"
                style={{ background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.08)' }}
              >
                <p className="font-semibold text-white mb-1 flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full shrink-0" style={{ background: CYAN }} />
                  Analytics Cookies
                </p>
                <p style={{ color: 'rgba(255,255,255,0.60)' }}>
                  Analytics cookies help us understand how visitors interact with Vantro.ai. We use tools such
                  as Google Analytics and our own internal analytics to collect aggregated, anonymised data
                  about page views, session duration, navigation paths, feature usage, and error rates. This
                  data helps us improve the platform and identify areas for enhancement. You may opt out of
                  analytics cookies via our cookie preferences banner.
                </p>
              </div>

              {/* Marketing */}
              <div
                className="rounded-xl px-5 py-4"
                style={{ background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.08)' }}
              >
                <p className="font-semibold text-white mb-1 flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full shrink-0" style={{ background: '#A855F7' }} />
                  Marketing Cookies
                </p>
                <p style={{ color: 'rgba(255,255,255,0.60)' }}>
                  Marketing cookies are used to track visitors across websites and display relevant advertising.
                  We may use advertising platforms such as Meta Pixel, Google Ads, and LinkedIn Insight Tag to
                  measure the effectiveness of our campaigns and serve personalised advertisements to users who
                  have visited Vantro.ai. These cookies may be set by our trusted third-party advertising
                  partners. You may opt out of marketing cookies at any time.
                </p>
              </div>
            </div>
          </Section>

          {/* 3 */}
          <Section id="how-to-control" title="3. How to Control Cookies">
            <p>
              You have several options for controlling or limiting how cookies are used on your device:
            </p>
            <ul className="space-y-2 mt-2">
              {[
                'Cookie Preferences Banner — When you first visit Vantro.ai, a cookie consent banner allows you to accept all cookies, reject non-essential cookies, or customise your preferences by category.',
                'Browser Settings — Most web browsers allow you to manage cookies through their settings. You can typically configure your browser to block or delete cookies. Please note that disabling certain cookies may affect the functionality of Vantro.ai.',
                'Google Analytics Opt-Out — You can install the Google Analytics Opt-out Browser Add-on to prevent your data from being collected by Google Analytics.',
                'Do Not Track — Some browsers send "Do Not Track" signals. We respect these signals where technically feasible.',
              ].map((item, i) => (
                <li key={i} className="flex items-start gap-3 text-sm">
                  <span className="shrink-0 w-1.5 h-1.5 rounded-full mt-[0.45rem]" style={{ background: ORANGE }} />
                  {item}
                </li>
              ))}
            </ul>
            <p className="mt-3">
              Please be aware that blocking all cookies may impair your ability to log in, access certain
              features, or use the platform as intended.
            </p>
          </Section>

          {/* 4 */}
          <Section id="third-party-cookies" title="4. Third-Party Cookies">
            <p>
              Some cookies on Vantro.ai are set by third-party services we use to deliver certain features or
              measure platform performance. These third parties have their own privacy policies which govern
              how they use such information. We do not control these third-party cookies.
            </p>
            <p>
              Third-party services that may set cookies include, but are not limited to: Stripe (payment
              processing), Intercom (customer support), Google Analytics (analytics), and advertising
              platforms used for campaign measurement.
            </p>
          </Section>

          {/* 5 */}
          <Section id="updates" title="5. Updates to This Policy">
            <p>
              We may update this Cookie Policy from time to time to reflect changes in our practices or for
              other operational, legal, or regulatory reasons. When we make material changes, we will update
              the &quot;Last updated&quot; date at the top of this page and, where appropriate, notify you via email
              or an in-app notice.
            </p>
            <p>
              We encourage you to review this policy periodically to stay informed about our use of cookies.
            </p>
          </Section>

          {/* 6 */}
          <Section id="contact" title="6. Contact">
            <p>
              If you have any questions about our use of cookies or this Cookie Policy, please contact us at:
            </p>
            <div
              className="mt-3 rounded-xl px-5 py-4 text-sm"
              style={{ background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.08)' }}
            >
              <p className="text-white font-semibold">Vantro Pty Ltd</p>
              <p className="mt-1" style={{ color: 'rgba(255,255,255,0.55)' }}>
                Email:{' '}
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
              <Link href="/ccpa" className="hover:text-white transition-colors">CCPA</Link>
              <Link href="/gdpr" className="hover:text-white transition-colors">GDPR</Link>
            </div>
          </div>
        </footer>
      </main>
    </div>
  );
}
