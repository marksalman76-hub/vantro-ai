import type { Metadata } from 'next'
import Link from 'next/link'
import Navbar from '@/components/Navbar'
import Footer from '@/components/Footer'

export const metadata: Metadata = {
  title: 'Privacy Policy',
  description: 'Learn how Vantro collects, uses, and protects your personal information.',
  robots: { index: true, follow: true },
}

const TOC = [
  { id: 'introduction',       label: '1. Introduction'                      },
  { id: 'information',        label: '2. Information We Collect'            },
  { id: 'use',                label: '3. How We Use Your Information'       },
  { id: 'legal-basis',        label: '4. Legal Basis for Processing'        },
  { id: 'sharing',            label: '5. Information Sharing & Disclosure'  },
  { id: 'retention',          label: '6. Data Retention'                    },
  { id: 'rights',             label: '7. Your Privacy Rights'               },
  { id: 'cookies',            label: '8. Cookies & Tracking Technologies'   },
  { id: 'security',           label: '9. Security'                          },
  { id: 'international',      label: '10. International Data Transfers'     },
  { id: 'children',           label: '11. Children\'s Privacy'              },
  { id: 'changes',            label: '12. Changes to This Policy'           },
  { id: 'contact',            label: '13. Contact Us'                       },
]

export default function PrivacyPage() {
  return (
    <>
      <Navbar />
      <div className="min-h-screen bg-dark pt-20">
        {/* Hero */}
        <div className="bg-gradient-to-b from-dark-950 to-dark border-b border-white/[0.06] py-14 px-4">
          <div className="max-w-3xl mx-auto">
            <p className="text-xs font-semibold text-violet-400 uppercase tracking-widest mb-3">Legal</p>
            <h1 className="text-4xl sm:text-5xl font-bold text-white mb-4">Privacy Policy</h1>
            <p className="text-white/55 text-lg">Last updated: <time dateTime="2026-06-19">June 19, 2026</time></p>
            <p className="mt-4 text-white/60 leading-relaxed max-w-2xl">
              Vantro Inc. ("Vantro", "we", "us", or "our") is committed to protecting your privacy. This Privacy Policy explains how we collect, use, disclose, and safeguard your information when you use our platform and services.
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

              <section id="introduction">
                <h2>1. Introduction</h2>
                <p>
                  Welcome to Vantro. We operate an AI agent platform that enables businesses to deploy autonomous agents for sales, support, research, and operations. By accessing or using our services, you agree to the collection and use of information in accordance with this policy.
                </p>
                <p>
                  This policy applies to all users of the Vantro platform, website visitors, trial users, and paying customers. It covers information collected through our website at vantro.ai, our web application, and any associated APIs or integrations.
                </p>
                <p>
                  If you have questions about this policy, please contact us at <a href="mailto:privacy@vantro.ai">privacy@vantro.ai</a> before using our services.
                </p>
              </section>

              <section id="information">
                <h2>2. Information We Collect</h2>
                <h3>Information You Provide Directly</h3>
                <ul>
                  <li><strong>Account information:</strong> When you create an account, we collect your name, email address, company name, job title, and password.</li>
                  <li><strong>Payment information:</strong> Billing details are processed by our payment processor (Stripe). We store only the last 4 digits of your card and billing address for record-keeping. We never store full card numbers.</li>
                  <li><strong>Business information:</strong> During onboarding, you may provide company size, industry, and use-case details to personalise your agent configuration.</li>
                  <li><strong>Communications:</strong> When you contact support, submit a form, or email us, we retain those communications and any information contained within them.</li>
                  <li><strong>User content:</strong> Any prompts, instructions, or data you provide to configure your AI agents, including brand guidelines, tone-of-voice documents, and training examples.</li>
                </ul>

                <h3>Information Collected Automatically</h3>
                <ul>
                  <li><strong>Usage data:</strong> Pages visited, features used, agent interactions, session duration, and click patterns within the platform.</li>
                  <li><strong>Device information:</strong> Browser type and version, operating system, screen resolution, and device identifiers.</li>
                  <li><strong>Network information:</strong> IP address, approximate geolocation (country/city level), ISP, and referring URL.</li>
                  <li><strong>Performance data:</strong> Page load times, error rates, and API response times to help us improve reliability.</li>
                </ul>

                <h3>Information from Third Parties</h3>
                <ul>
                  <li><strong>Integrations:</strong> If you connect Vantro to third-party services (CRMs, helpdesks, communication platforms), we receive data from those services as necessary to fulfil the integration's purpose.</li>
                  <li><strong>Single Sign-On (SSO):</strong> If you authenticate via Google, Microsoft, or another OAuth provider, we receive your name, email, and profile picture from that provider.</li>
                  <li><strong>Analytics partners:</strong> Aggregated, anonymised data from services such as Google Analytics to understand overall site performance.</li>
                </ul>
              </section>

              <section id="use">
                <h2>3. How We Use Your Information</h2>
                <p>We use the information we collect for the following purposes:</p>
                <ul>
                  <li><strong>Service delivery:</strong> To provision, operate, maintain, and improve the Vantro platform and your AI agents.</li>
                  <li><strong>Account management:</strong> To create and manage your account, authenticate you, and process payments.</li>
                  <li><strong>Customer support:</strong> To respond to your enquiries, troubleshoot problems, and provide technical assistance.</li>
                  <li><strong>Product improvement:</strong> To understand how users interact with the platform, identify bugs, and prioritise feature development. We use anonymised and aggregated data wherever possible.</li>
                  <li><strong>Communications:</strong> To send transactional emails (password resets, invoices, security alerts) and, with your consent, product updates and marketing communications. You can unsubscribe from marketing emails at any time.</li>
                  <li><strong>Security and fraud prevention:</strong> To detect, prevent, and respond to fraud, abuse, security incidents, and other harmful activities.</li>
                  <li><strong>Legal compliance:</strong> To meet our obligations under applicable law, respond to legal process, and enforce our terms of service.</li>
                  <li><strong>Personalisation:</strong> To tailor your experience, including suggested agent configurations based on your industry and use case.</li>
                </ul>
              </section>

              <section id="legal-basis">
                <h2>4. Legal Basis for Processing (GDPR)</h2>
                <p>
                  If you are located in the European Economic Area (EEA), United Kingdom, or Switzerland, we process your personal data under the following legal bases as defined by the General Data Protection Regulation (GDPR):
                </p>
                <ul>
                  <li><strong>Contract performance:</strong> Processing your account data and payment information is necessary to provide the services you have signed up for.</li>
                  <li><strong>Legitimate interests:</strong> We process usage data and improve our platform based on legitimate interests in operating a reliable, secure, and improving service. We balance these interests against your privacy rights.</li>
                  <li><strong>Consent:</strong> Where we send marketing communications or deploy non-essential cookies, we rely on your consent. You may withdraw consent at any time.</li>
                  <li><strong>Legal obligation:</strong> Where applicable law requires us to retain or disclose information (e.g., tax records, responses to legal process).</li>
                </ul>
                <p>
                  To exercise any rights under GDPR, or to raise a concern, please contact <a href="mailto:privacy@vantro.ai">privacy@vantro.ai</a>. You also have the right to lodge a complaint with your national supervisory authority.
                </p>
              </section>

              <section id="sharing">
                <h2>5. Information Sharing and Disclosure</h2>
                <p>We do not sell, rent, or trade your personal information. We may share it in the following limited circumstances:</p>
                <ul>
                  <li><strong>Service providers:</strong> We engage trusted third-party vendors to help operate our platform — including cloud infrastructure (AWS), payment processing (Stripe), email delivery (SendGrid), analytics (Google Analytics), and customer support tooling. These providers are contractually bound to use your data only as directed by us and to maintain appropriate security standards.</li>
                  <li><strong>Business transfers:</strong> If Vantro is involved in a merger, acquisition, or sale of assets, your information may be transferred as part of that transaction. We will notify you via email and a prominent notice on our site at least 30 days before any such transfer if it affects your personal data.</li>
                  <li><strong>Legal requirements:</strong> We may disclose your information if required to do so by law, court order, or governmental authority, or if we believe disclosure is necessary to protect the rights, property, or safety of Vantro, our users, or the public.</li>
                  <li><strong>Your consent:</strong> We may share information with third parties when you have explicitly consented to the sharing.</li>
                  <li><strong>Aggregated or anonymised data:</strong> We may share aggregated, non-personally-identifiable information for industry research, analysis, or marketing purposes.</li>
                </ul>
              </section>

              <section id="retention">
                <h2>6. Data Retention</h2>
                <p>
                  We retain personal data only for as long as necessary to fulfil the purposes described in this policy, unless a longer retention period is required by law.
                </p>
                <ul>
                  <li><strong>Active accounts:</strong> We retain your account data for as long as your account is active and for a reasonable period thereafter in case you wish to reactivate.</li>
                  <li><strong>Deleted accounts:</strong> When you request account deletion, we delete or anonymise your personal data within 30 days, except for data we are legally required to retain (e.g., billing records retained for 7 years for tax compliance).</li>
                  <li><strong>Usage logs:</strong> Raw usage logs are retained for 90 days and then aggregated or deleted.</li>
                  <li><strong>Support communications:</strong> Support tickets and related communications are retained for 3 years after resolution.</li>
                  <li><strong>Marketing data:</strong> If you unsubscribe from marketing communications, we retain a record of your preference to ensure we do not contact you again.</li>
                </ul>
              </section>

              <section id="rights">
                <h2>7. Your Privacy Rights</h2>
                <p>
                  Depending on your location, you may have the following rights regarding your personal data:
                </p>
                <ul>
                  <li><strong>Right of access:</strong> You can request a copy of the personal data we hold about you.</li>
                  <li><strong>Right to rectification:</strong> You can request correction of inaccurate or incomplete data.</li>
                  <li><strong>Right to erasure:</strong> You can request deletion of your personal data ("right to be forgotten"), subject to legal retention obligations.</li>
                  <li><strong>Right to portability:</strong> You can request your data in a machine-readable format (e.g., JSON or CSV) to transfer to another provider.</li>
                  <li><strong>Right to restrict processing:</strong> You can request that we limit how we use your data in certain circumstances.</li>
                  <li><strong>Right to object:</strong> You can object to processing based on legitimate interests, including profiling.</li>
                  <li><strong>Right to withdraw consent:</strong> Where processing is based on consent, you can withdraw at any time without affecting prior lawful processing.</li>
                  <li><strong>CCPA rights (California residents):</strong> You have the right to know what personal information is collected, to request deletion, to opt out of the sale of personal information (we do not sell personal information), and to non-discrimination for exercising your rights.</li>
                </ul>
                <p>
                  To exercise any of these rights, email <a href="mailto:privacy@vantro.ai">privacy@vantro.ai</a> with the subject line "Privacy Rights Request". We will respond within 30 days. We may ask you to verify your identity before processing your request.
                </p>
              </section>

              <section id="cookies">
                <h2>8. Cookies and Tracking Technologies</h2>
                <p>
                  We use cookies and similar tracking technologies on our website and platform. Cookies are small text files stored on your device that help us provide and improve our services.
                </p>
                <h3>Types of Cookies We Use</h3>
                <ul>
                  <li><strong>Essential cookies:</strong> Required for the website and platform to function. These cannot be disabled. Examples include authentication tokens and session identifiers.</li>
                  <li><strong>Analytics cookies:</strong> Help us understand how visitors interact with our website (e.g., Google Analytics). These are only set with your consent. Data is anonymised before aggregation.</li>
                  <li><strong>Marketing cookies:</strong> Used to show you relevant advertising on third-party platforms. These are only set with your explicit consent.</li>
                  <li><strong>Preference cookies:</strong> Remember your settings and choices (e.g., language, cookie consent choices) to improve your experience across visits.</li>
                </ul>
                <p>
                  You can manage your cookie preferences at any time via the cookie consent banner or by adjusting your browser settings. Note that disabling certain cookies may affect the functionality of our platform.
                </p>
                <p>
                  We use Google Analytics with IP anonymisation enabled. You can opt out of Google Analytics tracking across all websites by installing the <a href="https://tools.google.com/dlpage/gaoptout" target="_blank" rel="noopener noreferrer">Google Analytics Opt-out Browser Add-on</a>.
                </p>
              </section>

              <section id="security">
                <h2>9. Security</h2>
                <p>
                  We implement industry-standard technical and organisational measures to protect your personal data against unauthorised access, disclosure, alteration, and destruction. These measures include:
                </p>
                <ul>
                  <li>Encryption of data in transit using TLS 1.2 or higher</li>
                  <li>Encryption of sensitive data at rest using AES-256</li>
                  <li>Access controls and principle of least privilege for internal systems</li>
                  <li>Regular security assessments and penetration testing</li>
                  <li>SOC 2 Type II certified infrastructure</li>
                  <li>Audit logging of all data access events</li>
                </ul>
                <p>
                  Despite these measures, no method of internet transmission or electronic storage is 100% secure. In the event of a data breach that is likely to result in a risk to your rights, we will notify you and relevant authorities as required by applicable law, within 72 hours of becoming aware of the breach.
                </p>
              </section>

              <section id="international">
                <h2>10. International Data Transfers</h2>
                <p>
                  Vantro is based in the United States. If you access our services from the EEA, UK, or other regions, your information may be transferred to and processed in the US and other countries where our servers and service providers are located.
                </p>
                <p>
                  For transfers from the EEA or UK to the US, we rely on the EU-US Data Privacy Framework and Standard Contractual Clauses (SCCs) approved by the European Commission to ensure your data receives adequate protection. A copy of the applicable SCCs is available upon request.
                </p>
              </section>

              <section id="children">
                <h2>11. Children's Privacy</h2>
                <p>
                  Our services are not directed to individuals under the age of 16 (or the applicable age of digital consent in your jurisdiction). We do not knowingly collect personal data from children. If you believe we have inadvertently collected information from a child, please contact us immediately at <a href="mailto:privacy@vantro.ai">privacy@vantro.ai</a> and we will promptly delete the information.
                </p>
              </section>

              <section id="changes">
                <h2>12. Changes to This Policy</h2>
                <p>
                  We may update this Privacy Policy periodically to reflect changes in our practices, technology, legal requirements, or for other operational reasons. When we make material changes, we will:
                </p>
                <ul>
                  <li>Post the updated policy on this page with a revised "Last updated" date</li>
                  <li>Notify registered users by email at least 14 days before changes take effect (for material changes)</li>
                  <li>Where required by law, obtain your consent before applying changes</li>
                </ul>
                <p>
                  Your continued use of our services after the effective date of any changes constitutes your acceptance of the updated policy. We encourage you to review this page periodically.
                </p>
              </section>

              <section id="contact">
                <h2>13. Contact Us</h2>
                <p>
                  If you have questions, concerns, or requests regarding this Privacy Policy or our data practices, please contact us:
                </p>
                <ul>
                  <li><strong>Email:</strong> <a href="mailto:privacy@vantro.ai">privacy@vantro.ai</a></li>
                  <li><strong>Post:</strong> Vantro Inc., Attn: Privacy Team, 123 Market Street, San Francisco, CA 94105, USA</li>
                  <li><strong>Response time:</strong> We aim to respond to all privacy enquiries within 5 business days.</li>
                </ul>
                <p>
                  For EU/UK residents, our EU Representative is available at <a href="mailto:eu-privacy@vantro.ai">eu-privacy@vantro.ai</a>.
                </p>

                <div className="mt-8 p-4 rounded-xl bg-violet-600/10 border border-violet-500/20">
                  <p className="text-sm text-white/60 !mb-0">
                    <strong className="text-violet-300">Note:</strong> This Privacy Policy is provided as a template and should be reviewed by a qualified legal professional before publication to ensure compliance with all applicable laws and regulations in your jurisdiction.
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
