'use client';

import { Twitter, Linkedin, Github } from 'lucide-react';

const COLUMNS = [
  {
    heading: 'Product',
    links: [
      { label: 'Features', href: '#features' },
      { label: 'Agents', href: '#agents' },
      { label: 'Pricing', href: '/#pricing' },
    ],
  },
  {
    heading: 'Company',
    links: [
      { label: 'About', href: '/about' },
      { label: 'Blog', href: '/blog' },
      { label: 'Contact', href: '/contact' },
    ],
  },
  {
    heading: 'Legal',
    links: [
      { label: 'Privacy', href: '/privacy' },
      { label: 'Terms', href: '/terms' },
      { label: 'Cookies', href: '/cookies' },
    ],
  },
];

export function Footer() {
  return (
    <footer
      className="pt-20 pb-10"
      style={{
        backgroundColor: '#0A0D14',
        borderTop: '1px solid rgba(255,255,255,0.08)',
      }}
    >
      <div className="max-w-7xl mx-auto px-6">
        {/* Top row */}
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-12 lg:gap-8">
          {/* Brand column */}
          <div className="lg:col-span-1">
            <div className="flex items-center gap-2 mb-2">
              <img
                src="https://files.manuscdn.com/user_upload_by_module/session_file/310519663790183318/uLNNHswnlaLuEQJY.png"
                alt="Vantro logo"
                className="h-8 w-auto"
              />
              <span
                className="font-bold text-sm tracking-widest"
                style={{ fontFamily: 'Space Grotesk, sans-serif', color: '#FFFFFF' }}
              >
                VANTRO.ai
              </span>
            </div>
            <p className="text-sm mt-2" style={{ color: '#9CA3AF' }}>
              Deploy your autonomous AI workforce.
            </p>
          </div>

          {/* Nav columns */}
          {COLUMNS.map((col) => (
            <div key={col.heading}>
              <p
                className="text-xs uppercase tracking-widest mb-4"
                style={{ fontFamily: 'JetBrains Mono, monospace', color: '#E5E7EB' }}
              >
                {col.heading}
              </p>
              <ul className="flex flex-col gap-3">
                {col.links.map((link) => (
                  <li key={link.label}>
                    <a
                      href={link.href}
                      className="text-sm transition-colors duration-150"
                      style={{ color: '#9CA3AF' }}
                      onMouseEnter={(e) => {
                        (e.currentTarget as HTMLAnchorElement).style.color = 'oklch(0.97 0 0)';
                      }}
                      onMouseLeave={(e) => {
                        (e.currentTarget as HTMLAnchorElement).style.color = 'oklch(0.70 0 0)';
                      }}
                    >
                      {link.label}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        {/* Bottom row */}
        <div
          className="mt-16 pt-8 flex justify-between items-center flex-wrap gap-4"
          style={{ borderTop: '1px solid rgba(255,255,255,0.08)' }}
        >
          <p className="text-sm" style={{ color: '#9CA3AF' }}>
            2026 Vantro.ai. All rights reserved.
          </p>

          <div className="flex items-center gap-4">
            {[
              // TODO: replace href values with real Vantro social profile URLs when available
              { Icon: Twitter, label: 'Twitter', href: 'https://twitter.com/vantroai' },
              { Icon: Linkedin, label: 'LinkedIn', href: 'https://linkedin.com/company/vantroai' },
              { Icon: Github, label: 'GitHub', href: 'https://github.com/vantroai' },
            ].map(({ Icon, label, href }) => (
              <a
                key={label}
                href={href}
                aria-label={label}
                target="_blank"
                rel="noopener noreferrer"
                className="transition-colors duration-150 cursor-pointer"
                style={{ color: '#9CA3AF', display: 'inline-flex' }}
                onMouseEnter={(e) => {
                  (e.currentTarget as HTMLAnchorElement).style.color = 'oklch(0.97 0 0)';
                }}
                onMouseLeave={(e) => {
                  (e.currentTarget as HTMLAnchorElement).style.color = 'oklch(0.70 0 0)';
                }}
              >
                <Icon size={16} />
              </a>
            ))}
          </div>
        </div>
      </div>
    </footer>
  );
}
