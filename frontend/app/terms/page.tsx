import type { Metadata } from 'next'
import Link from 'next/link'
import Navbar from '@/components/Navbar'
import Footer from '@/components/Footer'

export const metadata: Metadata = {
  title: 'Terms of Service',
  description: 'The terms and conditions governing your use of the Vantro AI agent platform.',
  robots: { index: true, follow: true },
}

const TOC = [
  { id: 'acceptance',      label: '1. Acceptance of Terms'              },
  { id: 'description',     label: '2. Description of Services'         },
  { id: 'account',         label: '3. Account Registration'            },
  { id: 'acceptable-use',  label: '4. Acceptable Use Policy'           },
  { id: 'subscription',    label: '5. Subscription and Payment'        },
  { id: 'ip',              label: '6. Intellectual Property'           },
  { id: 'data',            label: '7. Data & Privacy'                  },
  { id: 'confidentiality', label: '8. Confidentiality'                 },
  { id: 'warranties',      label: '9. Warranties & Disclaimers'        },
  { id: 'liability',       label: '10. Limitation of Liability'        },
  { id: 'indemnification', label: '11. Indemnification'                },
  { id: 'termination',     label: '12. Term & Termination'             },
  { id: 'governing-law',   label: '13. Governing Law'                  },
  { id: 'disputes',        label: '14. Dispute Resolution'             },
  { id: 'general',         label: '15. General Provisions'             },
  { id: 'contact',         label: '16. Contact Information'            },
]

export default function TermsPage() {
  return (
    <>
      <Navbar />
      <div className="min-h-screen bg-dark pt-20">
        {/* Hero */}
        <div className="bg-gradient-to-b from-dark-950 to-dark border-b border-white/[0.06] py-14 px-4">
          <div className="max-w-3xl mx-auto">
            <p className="text-xs font-semibold text-violet-400 uppercase tracking-widest mb-3">Legal</p>
            <h1 className="text-4xl sm:text-5xl font-bold text-white mb-4">Terms of Service</h1>
            <p className="text-white/55 text-lg">Last updated: <time dateTime="2026-06-19">June 19, 2026</time></p>
            <p className="mt-4 text-white/60 leading-relaxed max-w-2xl">
              These Terms of Service ("Terms") govern your access to and use of the Vantro platform and services. Please read them carefully before using our services.
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

              <section id="acceptance">
                <h2>1. Acceptance of Terms</h2>
                <p>
                  By accessing or using the Vantro platform, website, or any related services (collectively, the "Services"), you agree to be bound by these Terms of Service and our <Link href="/privacy">Privacy Policy</Link>, which is incorporated herein by reference. If you are using the Services on behalf of an organisation, you represent that you have the authority to bind that organisation to these Terms.
                </p>
                <p>
                  If you do not agree to these Terms, you must not access or use our Services. Your continued use of the Services following any changes to these Terms constitutes acceptance of those changes.
                </p>
                <p>
                  You must be at least 18 years of age (or the age of legal majority in your jurisdiction) to create an account or use our Services.
                </p>
              </section>

              <section id="description">
                <h2>2. Description of Services</h2>
                <p>
                  Vantro provides an AI agent platform that enables businesses to deploy, configure, and manage autonomous AI agents for tasks including, but not limited to, sales outreach, customer support, data analysis, marketing, legal research, and operational workflows.
                </p>
                <p>
                  Our Services are provided on a subscription basis, with plans offering varying levels of capability, agent availability, and usage limits. We reserve the right to modify, suspend, or discontinue any aspect of the Services at any time, with reasonable notice to active subscribers.
                </p>
                <p>
                  The Services are provided "as is" and are intended for business use. They are not a substitute for professional advice in regulated fields including law, medicine, finance, or accountancy. AI-generated outputs should be reviewed by qualified professionals before being relied upon for high-stakes decisions.
                </p>
              </section>

              <section id="account">
                <h2>3. Account Registration</h2>
                <p>
                  To access the Vantro platform, you must create an account. You agree to:
                </p>
                <ul>
                  <li>Provide accurate, current, and complete information during registration</li>
                  <li>Maintain the security and confidentiality of your login credentials</li>
                  <li>Promptly notify us of any unauthorised access to your account at <a href="mailto:security@vantro.ai">security@vantro.ai</a></li>
                  <li>Accept responsibility for all activities that occur under your account</li>
                  <li>Not share your account credentials with third parties unless using our team management features</li>
                </ul>
                <p>
                  Each account may be used by a single individual. For team access, please use our multi-seat subscription options. We reserve the right to suspend or terminate accounts that violate these Terms or that we reasonably believe are being used fraudulently.
                </p>
              </section>

              <section id="acceptable-use">
                <h2>4. Acceptable Use Policy</h2>
                <p>
                  You agree to use the Services only for lawful purposes and in accordance with these Terms. You must not use the Services to:
                </p>
                <ul>
                  <li>Engage in any activity that is illegal, fraudulent, deceptive, or harmful</li>
                  <li>Generate or distribute spam, unsolicited communications, or malware</li>
                  <li>Violate the intellectual property rights of third parties</li>
                  <li>Harass, abuse, threaten, or defame any individual or organisation</li>
                  <li>Process sensitive personal data (health records, financial account numbers, government IDs) without appropriate safeguards and legal authority</li>
                  <li>Attempt to reverse-engineer, decompile, or circumvent the security measures of our platform</li>
                  <li>Interfere with or disrupt the integrity or performance of the Services or underlying infrastructure</li>
                  <li>Use the Services to train competing AI models or build derivative products without prior written consent</li>
                  <li>Misrepresent the source or nature of AI-generated outputs in a way that could mislead or harm recipients</li>
                  <li>Violate any applicable export control laws or regulations</li>
                </ul>
                <p>
                  Violation of this policy may result in immediate suspension or termination of your account, at our sole discretion, without refund.
                </p>
              </section>

              <section id="subscription">
                <h2>5. Subscription and Payment</h2>
                <h3>Billing</h3>
                <p>
                  Paid subscriptions are billed in advance on a monthly or annual basis, depending on your selected plan. All prices are in US dollars and exclude applicable taxes unless stated otherwise. You authorise us to charge your payment method on the billing cycle you select.
                </p>
                <h3>Free Trials</h3>
                <p>
                  We may offer free trials at our discretion. Free trials automatically convert to paid subscriptions at the end of the trial period unless cancelled beforehand. We will notify you at least 3 days before a trial ends.
                </p>
                <h3>Upgrades and Downgrades</h3>
                <p>
                  You may upgrade your plan at any time; charges take effect immediately on a pro-rated basis. Downgrades take effect at the start of the next billing cycle.
                </p>
                <h3>Refunds</h3>
                <p>
                  Annual subscriptions are eligible for a full refund within 14 days of purchase if you have not used the Services in that period. Monthly subscriptions are non-refundable. In the event of a service outage exceeding our stated SLA, you may be eligible for a pro-rated service credit.
                </p>
                <h3>Late Payments</h3>
                <p>
                  If a payment fails, we will attempt to collect payment on three additional occasions over 7 days before suspending access. Suspended accounts retain their data for 60 days before permanent deletion.
                </p>
              </section>

              <section id="ip">
                <h2>6. Intellectual Property Rights</h2>
                <h3>Vantro's Intellectual Property</h3>
                <p>
                  The Vantro platform, including all underlying software, algorithms, AI models, user interfaces, documentation, trademarks, and trade secrets, is the exclusive property of Vantro Inc. and is protected by copyright, patent, trademark, and other intellectual property laws. Nothing in these Terms grants you ownership of any Vantro IP.
                </p>
                <h3>Your Content and Data</h3>
                <p>
                  You retain full ownership of any content, data, documents, or configurations you provide to the platform ("Customer Data"). By using the Services, you grant Vantro a limited, non-exclusive, worldwide, royalty-free licence to process your Customer Data solely to the extent necessary to provide the Services to you.
                </p>
                <p>
                  We will not use your Customer Data to train our AI models without your explicit, opt-in consent.
                </p>
                <h3>AI-Generated Outputs</h3>
                <p>
                  You own the outputs generated by your AI agents, subject to any applicable laws regarding AI authorship in your jurisdiction. You are responsible for reviewing and taking accountability for agent outputs before acting on them or distributing them.
                </p>
              </section>

              <section id="data">
                <h2>7. Data and Privacy</h2>
                <p>
                  Our collection and use of personal data is governed by our <Link href="/privacy">Privacy Policy</Link>. For enterprise customers requiring a Data Processing Agreement (DPA) in compliance with GDPR or other data protection laws, please contact <a href="mailto:privacy@vantro.ai">privacy@vantro.ai</a>.
                </p>
                <p>
                  We maintain commercially reasonable technical and organisational security measures to protect your data. Our current security posture is described in our Security page. In the event of a data breach affecting your personal data, we will notify you in accordance with applicable law.
                </p>
              </section>

              <section id="confidentiality">
                <h2>8. Confidentiality</h2>
                <p>
                  Each party ("disclosing party") may share non-public, proprietary, or confidential information ("Confidential Information") with the other party ("receiving party") in connection with the Services. The receiving party agrees to:
                </p>
                <ul>
                  <li>Protect Confidential Information using at least the same care it uses to protect its own confidential information (no less than reasonable care)</li>
                  <li>Use Confidential Information only to fulfil its obligations or exercise its rights under these Terms</li>
                  <li>Not disclose Confidential Information to third parties without prior written consent, except to employees or contractors with a need to know who are bound by appropriate confidentiality obligations</li>
                </ul>
                <p>
                  These obligations do not apply to information that is or becomes publicly available through no fault of the receiving party, was independently developed, or must be disclosed by law.
                </p>
              </section>

              <section id="warranties">
                <h2>9. Warranties and Disclaimers</h2>
                <p>
                  <strong>Our warranties:</strong> We warrant that the Services will perform materially in accordance with our documentation and that we will not knowingly introduce malware into the platform.
                </p>
                <p>
                  <strong>Disclaimer of other warranties:</strong> EXCEPT AS EXPRESSLY SET OUT IN THESE TERMS, THE SERVICES ARE PROVIDED "AS IS" AND "AS AVAILABLE" WITHOUT WARRANTIES OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, NON-INFRINGEMENT, AND ACCURACY OF AI-GENERATED CONTENT.
                </p>
                <p>
                  We do not warrant that the Services will be uninterrupted, error-free, or free of harmful components, or that the information obtained through the Services will be accurate, complete, or reliable. AI systems can produce incorrect, biased, or outdated outputs.
                </p>
              </section>

              <section id="liability">
                <h2>10. Limitation of Liability</h2>
                <p>
                  TO THE FULLEST EXTENT PERMITTED BY APPLICABLE LAW, IN NO EVENT SHALL VANTRO INC., ITS DIRECTORS, EMPLOYEES, AGENTS, OR LICENSORS BE LIABLE FOR ANY INDIRECT, INCIDENTAL, SPECIAL, CONSEQUENTIAL, PUNITIVE, OR EXEMPLARY DAMAGES, INCLUDING BUT NOT LIMITED TO LOSS OF PROFITS, REVENUE, DATA, BUSINESS, GOODWILL, OR ANTICIPATED SAVINGS, EVEN IF VANTRO HAS BEEN ADVISED OF THE POSSIBILITY OF SUCH DAMAGES.
                </p>
                <p>
                  VANTRO'S TOTAL CUMULATIVE LIABILITY ARISING OUT OF OR RELATED TO THESE TERMS OR THE SERVICES, WHETHER IN CONTRACT, TORT (INCLUDING NEGLIGENCE), OR OTHERWISE, SHALL NOT EXCEED THE GREATER OF: (A) THE FEES PAID BY YOU TO VANTRO IN THE 12 MONTHS PRECEDING THE CLAIM, OR (B) ONE HUNDRED US DOLLARS (USD $100).
                </p>
                <p>
                  Some jurisdictions do not allow the exclusion of implied warranties or limitation of liability for consequential damages. In those jurisdictions, our liability is limited to the maximum extent permitted by law.
                </p>
              </section>

              <section id="indemnification">
                <h2>11. Indemnification</h2>
                <p>
                  You agree to defend, indemnify, and hold harmless Vantro Inc. and its officers, directors, employees, and agents from and against any claims, liabilities, damages, losses, and expenses (including reasonable legal fees) arising out of or in any way connected with:
                </p>
                <ul>
                  <li>Your access to or use of the Services</li>
                  <li>Your violation of these Terms</li>
                  <li>Your infringement of any third-party rights, including intellectual property or privacy rights</li>
                  <li>Any outputs generated by your AI agents and the actions you or your organisation take based on those outputs</li>
                </ul>
              </section>

              <section id="termination">
                <h2>12. Term and Termination</h2>
                <p>
                  These Terms are effective from the date you first access the Services and continue until terminated. You may terminate your account at any time by following the account deletion steps in your dashboard settings.
                </p>
                <p>
                  We may suspend or terminate your access to the Services immediately, with or without notice, if we determine that you have violated these Terms, if your account is subject to repeated payment failures, or if continued provision of Services would expose Vantro or others to legal, reputational, or security risk.
                </p>
                <p>
                  Upon termination: (a) all licences granted to you will immediately cease; (b) you must cease all use of the Services; (c) we will delete or return your Customer Data within 30 days of your request, subject to any legal retention obligations; (d) any accrued payment obligations survive termination.
                </p>
                <p>
                  Sections 6, 8, 9, 10, 11, and 13 survive termination of these Terms.
                </p>
              </section>

              <section id="governing-law">
                <h2>13. Governing Law and Jurisdiction</h2>
                <p>
                  These Terms are governed by and construed in accordance with the laws of the State of California, United States, without regard to its conflict-of-law principles. Any legal action or proceeding arising under these Terms shall be subject to the exclusive jurisdiction of the courts located in San Francisco County, California.
                </p>
                <p>
                  If you are a consumer resident in the EU or UK, you may also benefit from mandatory provisions of the consumer protection laws of your country of residence.
                </p>
              </section>

              <section id="disputes">
                <h2>14. Dispute Resolution</h2>
                <p>
                  We encourage you to contact us first at <a href="mailto:legal@vantro.ai">legal@vantro.ai</a> before initiating formal legal proceedings. We will make good-faith efforts to resolve disputes informally within 30 days.
                </p>
                <p>
                  If informal resolution fails, you agree that any dispute, claim, or controversy arising out of or relating to these Terms or the Services shall be settled by binding arbitration administered by the American Arbitration Association (AAA) under its Commercial Arbitration Rules, with proceedings conducted in San Francisco, California. The arbitrator's decision shall be final and binding.
                </p>
                <p>
                  <strong>Class action waiver:</strong> You and Vantro agree that any dispute resolution proceedings will be conducted only on an individual basis and not as a class, collective, or representative action. You waive any right to participate in a class action lawsuit or class-wide arbitration.
                </p>
                <p>
                  This arbitration clause does not prevent either party from seeking emergency injunctive relief from a court of competent jurisdiction to prevent irreparable harm.
                </p>
              </section>

              <section id="general">
                <h2>15. General Provisions</h2>
                <ul>
                  <li><strong>Entire agreement:</strong> These Terms, together with our Privacy Policy and any order forms or SOWs, constitute the entire agreement between you and Vantro regarding the Services and supersede all prior agreements.</li>
                  <li><strong>Waiver:</strong> A failure or delay by Vantro to exercise a right under these Terms does not constitute a waiver of that right.</li>
                  <li><strong>Severability:</strong> If any provision of these Terms is found to be unenforceable, the remaining provisions will continue in full force and effect.</li>
                  <li><strong>Assignment:</strong> You may not assign or transfer these Terms or any rights hereunder without our prior written consent. Vantro may assign these Terms in connection with a merger, acquisition, or sale of substantially all assets.</li>
                  <li><strong>Notices:</strong> Legal notices to Vantro must be sent to <a href="mailto:legal@vantro.ai">legal@vantro.ai</a>. Notices to you will be sent to the email address on your account.</li>
                  <li><strong>Force majeure:</strong> Neither party shall be liable for delays or failures caused by events beyond its reasonable control, including natural disasters, pandemic, war, or government action.</li>
                  <li><strong>No partnership:</strong> Nothing in these Terms creates a partnership, joint venture, agency, or employment relationship between you and Vantro.</li>
                </ul>
              </section>

              <section id="contact">
                <h2>16. Contact Information</h2>
                <p>If you have any questions about these Terms of Service, please contact us:</p>
                <ul>
                  <li><strong>General enquiries:</strong> <a href="mailto:hello@vantro.ai">hello@vantro.ai</a></li>
                  <li><strong>Legal matters:</strong> <a href="mailto:legal@vantro.ai">legal@vantro.ai</a></li>
                  <li><strong>Privacy matters:</strong> <a href="mailto:privacy@vantro.ai">privacy@vantro.ai</a></li>
                  <li><strong>Postal address:</strong> Vantro Inc., Attn: Legal Team, 123 Market Street, San Francisco, CA 94105, USA</li>
                </ul>

                <div className="mt-8 p-4 rounded-xl bg-violet-600/10 border border-violet-500/20">
                  <p className="text-sm text-white/60 !mb-0">
                    <strong className="text-violet-300">Note:</strong> These Terms of Service are provided as a template and should be reviewed by a qualified legal professional before publication to ensure compliance with all applicable laws and regulations in your jurisdiction.
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
