'use client';

import React from 'react';
import ActionCard from './ActionCard';

const QUICK_LAUNCH_CARDS = [
  {
    href: '/dashboard/agents',
    icon: '◆',
    label: 'Run an agent',
    desc: 'Launch a task with any active agent',
  },
  {
    href: '/dashboard/library',
    icon: '▣',
    label: 'Output library',
    desc: 'Browse and copy past agent outputs',
  },
  {
    href: '/dashboard/reports',
    icon: '◈',
    label: 'Weekly report',
    desc: 'Performance summary and insights',
  },
  {
    href: '/dashboard/brand',
    icon: '◎',
    label: 'Brand profile',
    desc: 'Feed your brand context to agents',
  },
  {
    href: '/dashboard/billing',
    icon: '◇',
    label: 'Billing & credits',
    desc: 'Top up credits or manage your plan',
  },
  {
    href: '/dashboard/settings',
    icon: '◌',
    label: 'Settings',
    desc: 'Integrations, notifications, security',
  },
];

export default function QuickLaunchSection() {
  return (
    <div className="grid grid-cols-2 lg:grid-cols-3 gap-4 mb-8">
      {QUICK_LAUNCH_CARDS.map((card) => (
        <ActionCard
          key={card.href}
          href={card.href}
          icon={card.icon}
          label={card.label}
          desc={card.desc}
        />
      ))}
    </div>
  );
}
