'use client';

import { Twitter, Linkedin, Github } from 'lucide-react';
import { useToast } from '../context/ToastContext';

const COLUMNS = [
  {
    heading: 'Product',
    links: [
      { label: 'Features', href: '#features' },
      { label: 'Agents', href: '#agents' },
      { label: 'Pricing', href: '#pricing' },
      { label: 'Integrations', href: null },
      { label: 'Changelog', href: null },
    ],
  },
  {
    heading: 'Company',
    links: [
      { label: 'About', href: null },
      { label: 'Careers', href: null },
      { label: 'Blog', href: null },
      { label: 'Contact', href: null },
    ],
  },
  {
    heading: 'Resources',
    links: [
      { label: 'Docs', href: null },
      { label: 'API', href: null },
      { label: 'Status', href: null },
      { label: 'Security', href: null },
    ],
  },
  {
    heading: 'Legal',
    links: [
      { label: 'Privacy', href: null },
      { label: 'Terms', href: null },
      { label: 'DPA', href: null },
    ],
  },
];

export function Footer() {
  const { showToast } = useToast();

  function handleLink(e: React.MouseEvent<HTMLAnchorElement>, href: string | null) {
    if (!href) {
      e.preventDefault();
      showToast();
    }
  }

  return (
    <footer
      className="pt-20 pb-10"
      style={{
        backgroundColor: 'oklch(0.10 0 0)',
        borderTop: '1px solid rgba(255,255,255,0.08)',
      }}
    >
      <div className="max-w-7xl mx-auto px-6">
        {/* Top row */}
        <div className="grid grid-cols-1 lg:grid-cols-5 gap-12 lg:gap-8">
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
                style={{ fontFamily: 'Space Grotesk, sans-serif', color: 'oklch(0.97 0 0)' }}
              >
                VANTRO.ai
              </span>
            </div>
            <p className="text-sm mt-2" style={{ color: 'oklch(0.70 0 0)' }}>
              Deploy your autonomous AI workforce.
            </p>
          </div>

          {/* Nav columns */}
          {COLUMNS.map((col) => (
            <div key={col.heading}>
              <p
                className="text-xs uppercase tracking-widest mb-4"
                style={{ fontFamily: 'JetBrains Mono, monospace', color: 'oklch(0.79 0 0)' }}
              >
                {col.heading}
              </p>
              <ul className="flex flex-col gap-3">
                {col.links.map((link) => (
                  <li key={link.label}>
                    <a
                      href={link.href ?? '#'}
                      onClick={(e) => handleLink(e, link.href)}
                      className="text-sm transition-colors duration-150"
                      style={{ color: 'oklch(0.70 0 0)' }}
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
          <p className="text-sm" style={{ color: 'oklch(0.70 0 0)' }}>
            2026 Vantro.ai. All rights reserved.
          </p>

          <div className="flex items-center gap-4">
            {[
              { Icon: Twitter, label: 'Twitter' },
              { Icon: Linkedin, label: 'LinkedIn' },
              { Icon: Github, label: 'GitHub' },
            ].map(({ Icon, label }) => (
              <button
                key={label}
                aria-label={label}
                onClick={() => showToast()}
                className="transition-colors duration-150 cursor-pointer"
                style={{ color: 'oklch(0.70 0 0)', background: 'none', border: 'none', padding: 0 }}
                onMouseEnter={(e) => {
                  (e.currentTarget as HTMLButtonElement).style.color = 'oklch(0.97 0 0)';
                }}
                onMouseLeave={(e) => {
                  (e.currentTarget as HTMLButtonElement).style.color = 'oklch(0.70 0 0)';
                }}
              >
                <Icon size={16} />
              </button>
            ))}
          </div>
        </div>
      </div>
    </footer>
  );
}
