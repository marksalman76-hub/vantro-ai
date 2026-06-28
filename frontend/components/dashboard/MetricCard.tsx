'use client';

import React from 'react';

interface MetricCardProps {
  label: string;
  value: string | number;
  sub?: string;
  color?: string;
}

export default function MetricCard({
  label,
  value,
  sub,
  color = 'white',
}: MetricCardProps) {
  return (
    <div
      style={{
        background: 'oklch(1 0 0 / 0.04)',
        border: '1px solid oklch(1 0 0 / 0.08)',
        borderRadius: '1rem',
        padding: '1.25rem',
        display: 'flex',
        flexDirection: 'column',
        gap: '0.25rem',
      }}
    >
      <label
        style={{
          fontSize: '0.75rem',
          fontWeight: 500,
          color: 'oklch(0.50 0 0)',
        }}
      >
        {label}
      </label>
      <div
        style={{
          fontSize: '1.5rem',
          fontWeight: 'bold',
          color: color,
        }}
      >
        {value}
      </div>
      {sub && (
        <div
          style={{
            fontSize: '0.75rem',
            color: 'oklch(0.60 0 0)',
          }}
        >
          {sub}
        </div>
      )}
    </div>
  );
}
