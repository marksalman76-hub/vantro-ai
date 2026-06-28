'use client';

import React from 'react';

interface StatusBadgeProps {
  status: string;
}

// Maps raw status from API to display string
const CLIENT_STATUS: Record<string, string> = {
  pending: 'Waiting to start',
  running: 'In progress',
  processing: 'In progress',
  approved: 'In progress',
  pending_approval: 'Needs your approval',
  pending_financial_review: 'Needs your approval',
  completed: 'Ready',
  failed: 'Could not complete',
  cancelled: 'Cancelled',
  rejected: 'Not approved',
};

// Style mappings for display strings
const STATUS_INLINE_STYLES: Record<
  string,
  {
    color: string;
    backgroundColor: string;
    border: string;
  }
> = {
  'Waiting to start': {
    color: 'oklch(0.82 0.18 65)',
    backgroundColor: 'oklch(0.82 0.18 65 / 0.10)',
    border: '1px solid oklch(0.82 0.18 65 / 0.20)',
  },
  'In progress': {
    color: 'oklch(0.78 0.13 250)',
    backgroundColor: 'oklch(0.60 0.18 250 / 0.10)',
    border: '1px solid oklch(0.60 0.18 250 / 0.20)',
  },
  'Needs your approval': {
    color: 'oklch(0.75 0.18 55)',
    backgroundColor: 'oklch(0.75 0.18 55 / 0.10)',
    border: '1px solid oklch(0.75 0.18 55 / 0.20)',
  },
  Ready: {
    color: 'oklch(0.75 0.22 145)',
    backgroundColor: 'oklch(0.75 0.22 145 / 0.10)',
    border: '1px solid oklch(0.75 0.22 145 / 0.20)',
  },
  'Could not complete': {
    color: 'oklch(0.65 0.18 25)',
    backgroundColor: 'oklch(0.65 0.18 25 / 0.10)',
    border: '1px solid oklch(0.65 0.18 25 / 0.20)',
  },
  Cancelled: {
    color: 'oklch(0.45 0 0)',
    backgroundColor: 'oklch(1 0 0 / 0.03)',
    border: '1px solid oklch(1 0 0 / 0.08)',
  },
  'Not approved': {
    color: 'oklch(0.65 0.18 25)',
    backgroundColor: 'oklch(0.65 0.18 25 / 0.10)',
    border: '1px solid oklch(0.65 0.18 25 / 0.20)',
  },
};

export default function StatusBadge({ status }: StatusBadgeProps) {
  // Get display string from raw status
  const displayStatus = CLIENT_STATUS[status] || status;

  // Get styles for display string
  const styles = STATUS_INLINE_STYLES[displayStatus] || STATUS_INLINE_STYLES['Cancelled'];

  return (
    <span
      style={{
        borderRadius: '9999px',
        fontSize: '10px',
        padding: '2px 8px',
        fontWeight: '600',
        ...styles,
      }}
    >
      {displayStatus}
    </span>
  );
}
