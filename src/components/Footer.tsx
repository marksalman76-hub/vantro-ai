'use client';

import { Twitter, Linkedin, Facebook } from 'lucide-react';

function TikTokIcon({ size = 16 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
      <path d="M19.59 6.69a4.83 4.83 0 0 1-3.77-4.25V2h-3.45v13.67a2.89 2.89 0 0 1-2.88 2.5 2.89 2.89 0 0 1-2.89-2.89 2.89 2.89 0 0 1 2.89-2.89c.28 0 .54.04.79.1V9.01a6.33 6.33 0 0 0-.79-.05 6.34 6.34 0 0 0-6.34 6.34 6.34 6.34 0 0 0 6.34 6.34 6.34 6.34 0 0 0 6.33-6.34V8.69a8.18 8.18 0 0 0 4.78 1.52V6.76a4.85 4.85 0 0 1-1.01-.07Z" />
    </svg>
  );
}

const COLUMNS = [
  {
    heading: 'Product',
    links: [
      { label: 'Integrations', href: '#integrations' },
      { label: 'Agents', href: '#agents' },
      { label: 'Pricing', href: '#pricing' },
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

const SOCIALS = [
  { Icon: Twitter, label: 'Twitter', href: 'https://twitter.com/vantroai' },
  { Icon: Linkedin, label: 'LinkedIn', href: 'https://linkedin.com/company/vantroai' },
  { Icon: Facebook, label: 'Facebook', href: 'https://facebook.com/vantroai' },
  { Icon: TikTokIcon, label: 'TikTok', href: 'https://tiktok.com/@vantroai' },
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
                      onMouseEnter={(e) => { (e.currentTarget as HTMLAnchorElement).style.color = '#FFFFFF'; }}
                      onMouseLeave={(e) => { (e.currentTarget as HTMLAnchorElement).style.color = '#9CA3AF'; }}
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
            © 2026 Vantro.ai. All rights reserved.
          </p>

          <div className="flex items-center gap-4">
            {SOCIALS.map(({ Icon, label, href }) => (
              <a
                key={label}
                href={href}
                aria-label={label}
                target="_blank"
                rel="noopener noreferrer"
                className="transition-colors duration-150 cursor-pointer"
                style={{ color: '#9CA3AF', display: 'inline-flex' }}
                onMouseEnter={(e) => { (e.currentTarget as HTMLAnchorElement).style.color = '#FFFFFF'; }}
                onMouseLeave={(e) => { (e.currentTarget as HTMLAnchorElement).style.color = '#9CA3AF'; }}
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
