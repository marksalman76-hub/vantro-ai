import Link from 'next/link'
import { X, Globe, Briefcase, Github } from 'lucide-react'

type NavItem = { label: string; href: string }

const LINKS: Record<string, NavItem[]> = {
  Product: [
    { label: 'Features',     href: '/#features'  },
    { label: 'How it works', href: '/#how'       },
    { label: 'Integrations', href: '/#integrations' },
    { label: 'Pricing',      href: '/pricing'    },
    { label: 'Changelog',    href: '#'           },
  ],
  Company: [
    { label: 'About',    href: '#' },
    { label: 'Blog',     href: '#' },
    { label: 'Careers',  href: '#' },
    { label: 'Press',    href: '#' },
    { label: 'Contact',  href: '#' },
  ],
  Legal: [
    { label: 'Privacy Policy',   href: '/privacy'          },
    { label: 'Terms of Service', href: '/terms'            },
    { label: 'Refund Policy',    href: '/refund-policy'    },
    { label: 'Cookie Policy',    href: '/privacy#cookies'  },
  ],
  Resources: [
    { label: 'Docs',          href: '#' },
    { label: 'API Reference', href: '#' },
    { label: 'Case Studies',  href: '#' },
    { label: 'Support',       href: '#' },
    { label: 'Status',        href: '#' },
  ],
}

const SOCIAL = [
  { icon: X,         label: 'Twitter / X', href: '#' },
  { icon: Briefcase, label: 'LinkedIn',     href: '#' },
  { icon: Github,    label: 'GitHub',       href: '#' },
  { icon: Globe,     label: 'Website',      href: '#' },
]

export default function Footer() {
  return (
    <footer className="bg-dark-950 border-t border-white/[0.07]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-6 gap-10 lg:gap-10">
          {/* Brand */}
          <div className="lg:col-span-2">
            <Link href="/" className="flex items-center gap-1.5 mb-4">
              <span className="w-8 h-8 rounded-lg bg-gradient-to-br from-violet-600 to-blue-600 flex items-center justify-center text-white font-bold text-sm">
                V
              </span>
              <span className="text-xl font-bold text-white">
                Vantro<span className="text-violet-400">.ai</span>
              </span>
            </Link>
            <p className="text-sm text-white/50 leading-relaxed max-w-xs mb-6">
              Autonomous AI agents that handle sales, support, research, and operations — so your team can focus on what matters.
            </p>
            {/* Newsletter */}
            <div className="flex gap-2">
              <input
                type="email"
                placeholder="your@company.com"
                className="flex-1 px-3 py-2 text-sm rounded-lg bg-white/[0.05] border border-white/10 text-white placeholder-white/30 focus:outline-none focus:border-violet-500/60 transition-colors min-w-0"
              />
              <button className="px-4 py-2 text-sm font-semibold rounded-lg bg-violet-600 hover:bg-violet-500 text-white transition-colors whitespace-nowrap">
                Subscribe
              </button>
            </div>
          </div>

          {/* Link columns */}
          {Object.entries(LINKS).map(([title, items]) => (
            <div key={title}>
              <h3 className="text-xs font-semibold text-white/40 uppercase tracking-widest mb-4">{title}</h3>
              <ul className="space-y-2.5">
                {items.map((item) => (
                  <li key={item.label}>
                    <Link href={item.href} className="text-sm text-white/55 hover:text-white transition-colors">
                      {item.label}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        {/* Bottom bar */}
        <div className="mt-14 pt-8 border-t border-white/[0.07] flex flex-col sm:flex-row items-center justify-between gap-4">
          <p className="text-xs text-white/35">
            © {new Date().getFullYear()} Vantro Inc. All rights reserved.
          </p>
          <div className="flex items-center gap-1">
            {SOCIAL.map(({ icon: Icon, label, href }) => (
              <Link
                key={label}
                href={href}
                aria-label={label}
                className="p-2 rounded-lg text-white/35 hover:text-white hover:bg-white/[0.06] transition-all"
              >
                <Icon className="w-4 h-4" />
              </Link>
            ))}
          </div>
          <div className="flex items-center gap-4">
            <Link href="/privacy" className="text-xs text-white/35 hover:text-white/70 transition-colors">Privacy Policy</Link>
            <Link href="/terms"   className="text-xs text-white/35 hover:text-white/70 transition-colors">Terms of Service</Link>
            <Link href="/refund-policy" className="text-xs text-white/35 hover:text-white/70 transition-colors">Refund Policy</Link>
            <Link href="/privacy#cookies" className="text-xs text-white/35 hover:text-white/70 transition-colors">Cookie Policy</Link>
          </div>
        </div>
      </div>
    </footer>
  )
}
