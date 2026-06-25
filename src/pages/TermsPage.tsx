'use client';

import { ArrowLeft } from 'lucide-react';

const SECTIONS = [
  {
    title: '1. Acceptance of Terms',
    body: `By creating an account, accessing, or using the Vantro platform (the "Service"), you ("Customer", "you", or "your") agree to be bound by these Terms of Service ("Terms") and our Privacy Policy. If you are accepting on behalf of a company or other legal entity, you represent that you have the authority to bind that entity.\n\nIf you do not agree to these Terms, you may not access or use the Service. These Terms apply to all subscribers, users, and others who access or use the Service, including those who access it through our API.`,
  },
  {
    title: '2. Description of Service',
    body: `Vantro provides a multi-tenant SaaS platform that allows ecommerce businesses to deploy and manage a catalogue of autonomous AI agents for operations including marketing, sales, customer support, analytics, content generation, and related business functions (the "Service"). The Service includes access to the agent execution dashboard, the Vantro API, third-party integrations, and associated documentation.\n\nThe Service is organised around Organisations, Workspaces, and Credit Accounts. Each Workspace is independently scoped and isolated — data, credentials, and agent jobs from one Workspace are never accessible to another.\n\nWe reserve the right to modify, suspend, or discontinue any feature or aspect of the Service at any time. Where a change materially reduces functionality you actively rely on, we will provide at least 30 days' notice.`,
  },
  {
    title: '3. Account Registration and Security',
    body: `You must register for an account to access the Service. You agree to provide accurate, current, and complete information and to update it promptly if it changes. You are responsible for maintaining the confidentiality of your login credentials and for all activities conducted under your account.\n\nYou must immediately notify us at support@vantro.ai of any suspected unauthorised access to your account. Vantro will not be liable for any loss or damage arising from your failure to protect your credentials.\n\nYou may not share account access with others who have not been added as users under your Organisation. Each user accessing the Service must have their own account credentials.`,
  },
  {
    title: '4. Subscriptions, Credits, and Billing',
    body: `Plan Subscriptions: The Service is offered on subscription plans (Starter, Growth, Business, Enterprise). Subscriptions are billed in advance on a monthly cycle. Annual billing options, where available, are billed annually in advance.\n\nCredits: AI agent execution consumes credits from your Workspace's Credit Account. Credits are allocated at the start of each billing cycle in accordance with your plan. Unused credits do not roll over to the following cycle unless otherwise stated in your plan description. Additional credits may be purchased as top-up packs at rates displayed in the dashboard.\n\nPricing Changes: We reserve the right to change subscription pricing with at least 30 days' written notice of any price increase. Continued use of the Service after the effective date constitutes your acceptance of the new price.\n\nPayment: All fees are charged in USD and processed via Stripe. By providing a payment method, you authorise Vantro to charge that method for all amounts due. Failed payments may result in service suspension.\n\nRefund Policy: We offer a 72-hour refund window from the date of initial subscription purchase for new subscribers who have not consumed more than 10% of their plan's credit allocation. After 72 hours or if credits have been substantially consumed, all fees are non-refundable. Credit top-up packs are non-refundable once purchased. To request a refund within the eligible window, contact support@vantro.ai.\n\nDisputed Charges: Charge disputes must be raised within 30 days of the invoice date. We will investigate all disputes in good faith.`,
  },
  {
    title: '5. AI Agent Usage and Limitations',
    body: `Agent Catalogue: The Service provides access to a defined catalogue of AI agents. The agents available to you depend on your subscription plan tier. Vantro may add, modify, or retire agents over time with reasonable notice.\n\nHuman-in-the-Loop (HITL): Certain agent tasks — particularly those assessed as involving financial commitments, contractual decisions, or infrastructure scaling — are held in a "pending approval" state and require manual review and authorisation by an account owner or admin before execution proceeds. This is a safety feature and cannot be disabled.\n\nFinancial Governance: AI agents on the Vantro platform are strictly prohibited from independently committing to financial expenditure, entering into contracts or agreements, initiating advertising spend, scaling paid infrastructure, or taking any action that creates a legally binding obligation on your behalf. Every output assessed as containing such actions is flagged and routed for human review before any external action can occur. You acknowledge and agree that Vantro's agents are tools to assist human decision-makers, not autonomous actors with authority to bind your business.\n\nOutput Accuracy: AI-generated outputs are probabilistic and may contain inaccuracies or content that requires human review before use. You are solely responsible for reviewing, validating, and approving any agent output before acting on it or publishing it. Vantro makes no warranty regarding the accuracy, completeness, or fitness for purpose of agent outputs.`,
  },
  {
    title: '6. Acceptable Use',
    body: `You agree not to use the Service to:\n\n• Violate any applicable local, national, or international law or regulation.\n• Infringe the intellectual property, privacy, or other rights of any third party.\n• Generate, distribute, or facilitate the creation of fraudulent, deceptive, defamatory, or harmful content.\n• Attempt to reverse engineer, decompile, or extract source code, model weights, or system prompts from the Service.\n• Use the Service to train, fine-tune, or evaluate any competing AI model or system without our express written consent.\n• Conduct load tests, stress tests, or scraping operations that place unreasonable demands on Service infrastructure.\n• Attempt to gain unauthorised access to any part of the Service, or to the accounts, data, or systems of other users.\n• Submit inputs designed to manipulate, bypass, or override the behaviour of AI agents through prompt injection or similar techniques.\n\nVantro reserves the right to investigate suspected violations and to suspend or terminate accounts that violate these guidelines, with or without prior notice depending on the severity of the violation.`,
  },
  {
    title: '7. Intellectual Property',
    body: `Platform IP: The Service, including its software, design, agent catalogue, system prompts, infrastructure, and all associated documentation, is owned by Vantro and protected by copyright, trade secret, trademark, and other applicable intellectual property law. These Terms do not grant you any right, title, or interest in the Service beyond the limited licence to use it in accordance with your subscription.\n\nYour Data: You retain full ownership of all data, content, and materials you submit to the Service ("Customer Data"). By using the Service, you grant Vantro a limited, non-exclusive, royalty-free licence to process Customer Data solely to the extent necessary to provide and maintain the Service.\n\nAgent Outputs: Subject to these Terms, outputs generated by AI agents in response to your task submissions are assigned to you. Vantro does not claim ownership of agent outputs. You are responsible for ensuring outputs comply with applicable laws before use.\n\nFeedback: If you provide feedback, suggestions, or ideas about the Service, you grant Vantro a perpetual, irrevocable, royalty-free licence to use that feedback for any purpose without obligation to you.`,
  },
  {
    title: '8. Confidentiality',
    body: `Each party may have access to confidential information of the other party ("Confidential Information"), including business plans, technical architecture, pricing, Customer Data, and the specific identities of AI model providers used by the Service.\n\nEach party agrees to hold the other's Confidential Information in strict confidence; not to disclose it to third parties without prior written consent (except to employees or contractors who need to know and are bound by equivalent obligations); and to use it only for the purposes of these Terms.\n\nThis obligation does not apply to information that (a) is or becomes publicly available other than through breach of these Terms, (b) was independently developed without use of Confidential Information, or (c) must be disclosed by law or court order, provided the disclosing party gives prompt notice and reasonable cooperation.`,
  },
  {
    title: '9. Warranty Disclaimer',
    body: `THE SERVICE IS PROVIDED "AS IS" AND "AS AVAILABLE" WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO IMPLIED WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, TITLE, AND NON-INFRINGEMENT.\n\nVANTRO DOES NOT WARRANT THAT THE SERVICE WILL BE UNINTERRUPTED, ERROR-FREE, OR FREE FROM HARMFUL COMPONENTS; THAT DEFECTS WILL BE CORRECTED; OR THAT AI AGENT OUTPUTS WILL BE ACCURATE, COMPLETE, OR SUITABLE FOR YOUR INTENDED PURPOSE.\n\nSome jurisdictions do not allow the exclusion of implied warranties, so some of the above exclusions may not apply to you.`,
  },
  {
    title: '10. Limitation of Liability',
    body: `TO THE MAXIMUM EXTENT PERMITTED BY APPLICABLE LAW, VANTRO AND ITS OFFICERS, DIRECTORS, EMPLOYEES, AND AGENTS SHALL NOT BE LIABLE FOR ANY INDIRECT, INCIDENTAL, SPECIAL, CONSEQUENTIAL, EXEMPLARY, OR PUNITIVE DAMAGES — INCLUDING LOSS OF PROFITS, REVENUE, DATA, GOODWILL, OR THE COST OF SUBSTITUTE SERVICES — EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGES.\n\nIN ALL CASES, VANTRO'S TOTAL AGGREGATE LIABILITY TO YOU FOR ANY AND ALL CLAIMS ARISING UNDER OR RELATED TO THESE TERMS OR THE SERVICE SHALL NOT EXCEED THE TOTAL FEES PAID BY YOU TO VANTRO IN THE TWELVE (12) MONTHS IMMEDIATELY PRECEDING THE EVENT GIVING RISE TO THE CLAIM.\n\nThese limitations apply regardless of the theory of liability (contract, tort, strict liability, or otherwise). Some jurisdictions do not allow limitations of liability, so some of the above may not apply to you.`,
  },
  {
    title: '11. Indemnification',
    body: `You agree to indemnify, defend, and hold harmless Vantro and its officers, directors, employees, contractors, and agents from and against any and all claims, damages, losses, costs, and expenses (including reasonable legal fees) arising out of or relating to: (a) your use of the Service in violation of these Terms; (b) your Customer Data and any claim that it infringes any third-party rights; (c) your violation of any applicable law or regulation; or (d) any product or service you develop, market, or sell using outputs from the Service.\n\nVantro reserves the right to assume exclusive control over the defence of any matter subject to indemnification by you, at your expense.`,
  },
  {
    title: '12. Termination',
    body: `By You: You may cancel your subscription at any time through the account settings or by contacting support@vantro.ai. Cancellation takes effect at the end of the current billing cycle. No refunds are issued for unused time in the current cycle except within the 72-hour new-subscriber window described in Section 4.\n\nBy Vantro: We may suspend or terminate your access immediately, with or without notice, if you materially breach these Terms, fail to pay amounts due, or engage in conduct that poses a security risk or legal liability to Vantro or other users.\n\nEffect of Termination: Upon termination, your right to access the Service ceases immediately. We will retain and then delete your Customer Data in accordance with our Privacy Policy. Provisions that by their nature should survive termination (including Sections 7, 8, 9, 10, 11, and 13) shall survive.`,
  },
  {
    title: '13. Governing Law and Disputes',
    body: `These Terms are governed by and construed in accordance with the laws of the State of Delaware, United States, without regard to conflict-of-law principles.\n\nInformal Resolution: Before initiating any formal dispute process, both parties agree to attempt in good faith to resolve any dispute by contacting legal@vantro.ai. You and Vantro will have 30 days from the date of notice to attempt informal resolution.\n\nBinding Arbitration: If informal resolution fails, any dispute, claim, or controversy arising out of or relating to these Terms or the Service shall be resolved by binding individual arbitration administered by the American Arbitration Association (AAA) under its Commercial Arbitration Rules. The arbitration shall be conducted in English, with the seat in Wilmington, Delaware.\n\nClass Action Waiver: Any arbitration or court proceeding shall be conducted on an individual basis only. You waive any right to participate in a class, collective, or representative proceeding.\n\nException: Either party may seek injunctive or other equitable relief in a court of competent jurisdiction to prevent actual or threatened infringement of intellectual property rights or unauthorised disclosure of Confidential Information.`,
  },
  {
    title: '14. General Provisions',
    body: `Entire Agreement: These Terms, together with the Privacy Policy and any order form or subscription agreement, constitute the entire agreement between you and Vantro regarding the Service.\n\nSeverability: If any provision of these Terms is found invalid or unenforceable, that provision will be limited to the minimum extent necessary, and the remaining provisions will continue in full force.\n\nWaiver: Vantro's failure to enforce any right or provision shall not constitute a waiver of that right or provision.\n\nAssignment: You may not assign or transfer your rights or obligations under these Terms without our prior written consent. Vantro may assign these Terms in connection with a merger, acquisition, or sale of substantially all of its assets.\n\nForce Majeure: Neither party shall be liable for delays or failures in performance resulting from circumstances beyond its reasonable control, including acts of God, war, pandemic, governmental action, or infrastructure failure.\n\nNotices: Legal notices to Vantro must be sent to legal@vantro.ai. We will send notices to the email address on your account.`,
  },
];

export function TermsPage() {
  return (
    <div
      style={{
        minHeight: '100vh',
        backgroundColor: 'oklch(0.12 0 0)',
        fontFamily: "'Inter', sans-serif",
        color: 'oklch(0.97 0 0)',
      }}
    >
      {/* Top bar */}
      <div
        style={{
          borderBottom: '1px solid rgba(255,255,255,0.08)',
          padding: '20px 48px',
          display: 'flex',
          alignItems: 'center',
        }}
      >
        <a
          href="/"
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: 8,
            color: 'oklch(0.70 0 0)',
            textDecoration: 'none',
            fontSize: 14,
            transition: 'color 0.15s',
          }}
          onMouseEnter={e => { (e.currentTarget as HTMLAnchorElement).style.color = 'oklch(0.97 0 0)' }}
          onMouseLeave={e => { (e.currentTarget as HTMLAnchorElement).style.color = 'oklch(0.70 0 0)' }}
        >
          <ArrowLeft size={16} />
          <span style={{ marginLeft: 4 }}>Back to Vantro.ai</span>
        </a>
      </div>

      {/* Content */}
      <div style={{ maxWidth: 720, margin: '0 auto', padding: '72px 48px 120px' }}>
        <p
          style={{
            fontFamily: 'JetBrains Mono, monospace',
            fontSize: 11,
            letterSpacing: '0.15em',
            textTransform: 'uppercase',
            color: 'oklch(0.60 0 0)',
            marginBottom: 16,
          }}
        >
          Legal
        </p>
        <h1
          style={{
            fontFamily: "'Space Grotesk', sans-serif",
            fontSize: 'clamp(2rem, 4vw, 3rem)',
            fontWeight: 700,
            letterSpacing: '-0.02em',
            marginBottom: 12,
            lineHeight: 1.1,
          }}
        >
          Terms of Service
        </h1>
        <p style={{ color: 'oklch(0.60 0 0)', fontSize: 14, marginBottom: 64 }}>
          Last updated: June 25, 2026
        </p>

        <p style={{ color: 'oklch(0.75 0 0)', fontSize: 16, lineHeight: 1.75, marginBottom: 56 }}>
          Please read these Terms of Service carefully before using Vantro. These Terms govern your
          access to and use of our platform, including any associated services, APIs, and content.
        </p>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 48 }}>
          {SECTIONS.map((section) => (
            <div key={section.title}>
              <h2
                style={{
                  fontFamily: "'Space Grotesk', sans-serif",
                  fontSize: 18,
                  fontWeight: 600,
                  marginBottom: 16,
                  color: 'oklch(0.97 0 0)',
                }}
              >
                {section.title}
              </h2>
              {section.body.split('\n\n').map((para, i) => (
                <p
                  key={i}
                  style={{
                    color: 'oklch(0.72 0 0)',
                    fontSize: 15,
                    lineHeight: 1.75,
                    marginBottom: 12,
                  }}
                >
                  {para}
                </p>
              ))}
            </div>
          ))}
        </div>

        <div
          style={{
            marginTop: 64,
            padding: 24,
            borderRadius: 12,
            border: '1px solid rgba(255,255,255,0.08)',
            background: 'rgba(255,255,255,0.03)',
          }}
        >
          <p style={{ color: 'oklch(0.72 0 0)', fontSize: 14, lineHeight: 1.7, margin: 0 }}>
            Questions about these Terms? Contact us at{' '}
            <a
              href="mailto:legal@vantro.ai"
              style={{ color: 'oklch(0.97 0 0)', textDecoration: 'underline' }}
            >
              legal@vantro.ai
            </a>
          </p>
        </div>
      </div>
    </div>
  );
}
