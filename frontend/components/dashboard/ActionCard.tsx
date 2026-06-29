'use client';

import React from 'react';
import Link from 'next/link';

interface ActionCardProps {
  href: string;
  icon: string;
  label: string;
  desc: string;
}

export default function ActionCard({
  href,
  icon,
  label,
  desc,
}: ActionCardProps) {
  return (
    <Link
      href={href}
      className="transition-all rounded-2xl p-5 group"
      style={{
        background: 'oklch(1 0 0 / 0.04)',
        border: '1px solid oklch(1 0 0 / 0.08)',
        borderRadius: '1rem',
        padding: '1.25rem',
        display: 'flex',
        flexDirection: 'row',
        gap: '1rem',
        alignItems: 'flex-start',
      }}
    >
      <div
        style={{
          fontSize: '1.5rem',
          color: 'oklch(0.78 0.13 250)',
          minWidth: '1.5rem',
        }}
      >
        {icon}
      </div>
      <div
        style={{
          display: 'flex',
          flexDirection: 'column',
          gap: '0.25rem',
          flex: 1,
        }}
      >
        <div
          style={{
            fontSize: '0.875rem',
            fontWeight: 500,
            color: 'white',
          }}
        >
          {label}
        </div>
        <div
          style={{
            fontSize: '0.75rem',
            color: 'oklch(0.39 0.009 264.4)',
          }}
        >
          {desc}
        </div>
      </div>
    </Link>
  );
}
