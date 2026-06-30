'use client';

import React, { useState } from 'react';
import Link from 'next/link';

interface CreditsData {
  total_credits: number;
  used_credits: number;
  remaining_credits: number;
  credits_unlimited?: boolean;
  credit_label?: string;
}

interface DashboardHeaderProps {
  credits: CreditsData | null;
  pendingApprovals: number;
  failedJobs: number;
  onSignOut: () => void;
  agentsHref?: string;
}

export default function DashboardHeader({
  credits,
  pendingApprovals,
  failedJobs,
  onSignOut,
  agentsHref = '/dashboard/agents',
}: DashboardHeaderProps): React.ReactNode {
  const [showAlerts] = useState(false);

  const alertCount = pendingApprovals + failedJobs;
  const remainingCredits = credits?.remaining_credits ?? 0;
  const totalCredits = credits?.total_credits ?? 0;
  const creditsUnlimited = Boolean(credits?.credits_unlimited);

  // Determine credit color based on percentage
  let creditColor = 'oklch(0.20 0.2 142)'; // green ≥50%
  if (creditsUnlimited) {
    creditColor = 'oklch(0.62 0.18 250)';
  } else if (totalCredits > 0) {
    const percentageRemaining = (remainingCredits / totalCredits) * 100;
    if (percentageRemaining < 20) {
      creditColor = 'oklch(0.55 0.2 25)'; // red <20%
    } else if (percentageRemaining < 50) {
      creditColor = 'oklch(0.60 0.15 70)'; // amber <50%
    }
  }

  return (
    <header
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        zIndex: 100,
        height: '70px',
        width: '100%',
        background: 'oklch(1 0 0 / 0.04)',
        borderBottom: '1px solid oklch(1 0 0 / 0.08)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        paddingLeft: '2rem',
        paddingRight: '2rem',
      }}
    >
      {/* Left: Vantro branding */}
      <div
        style={{
          fontSize: '1.25rem',
          fontWeight: 'bold',
          color: 'white',
          minWidth: 'auto',
        }}
      >
        Vantro
      </div>

      {/* Center: Run Agent CTA */}
      <Link href={agentsHref}>
        <button
          style={{
            background: 'rgb(37, 99, 235)',
            color: 'white',
            border: 'none',
            borderRadius: '0.5rem',
            padding: '0.5rem 1.5rem',
            fontSize: '1rem',
            fontWeight: '600',
            cursor: 'pointer',
            transition: 'background-color 0.2s ease',
          }}
          onMouseEnter={(e) => {
            (e.currentTarget as HTMLButtonElement).style.background =
              'rgb(29, 78, 216)';
          }}
          onMouseLeave={(e) => {
            (e.currentTarget as HTMLButtonElement).style.background =
              'rgb(37, 99, 235)';
          }}
        >
          Run Agent
        </button>
      </Link>

      {/* Right: Credits, Alerts, Sign-out */}
      <div
        style={{
          display: 'flex',
          gap: '1rem',
          alignItems: 'center',
        }}
      >
        {/* Credits display */}
        {credits && (
          <div
            style={{
              display: 'flex',
              alignItems: 'baseline',
              gap: '0.25rem',
            }}
          >
            <span
              style={{
                fontWeight: 'bold',
                fontSize: '1rem',
                color: creditColor,
              }}
            >
              {creditsUnlimited ? (credits?.credit_label || 'Unlimited') : remainingCredits}
            </span>
            <span
              style={{
                fontSize: '0.875rem',
                color: 'oklch(0.50 0 0)',
              }}
            >
              credits
            </span>
          </div>
        )}

        {/* Alerts badge */}
        <button
          style={{
            position: 'relative',
            background: 'transparent',
            border: 'none',
            color: 'oklch(0.50 0 0)',
            cursor: 'pointer',
            fontSize: '0.875rem',
            padding: 0,
          }}
        >
          Alerts
          {alertCount > 0 && (
            <span
              style={{
                position: 'absolute',
                top: '-8px',
                right: '-8px',
                background: 'oklch(0.60 0.15 70)',
                color: 'white',
                borderRadius: '50%',
                width: '24px',
                height: '24px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '0.75rem',
                fontWeight: 'bold',
              }}
            >
              {alertCount}
            </span>
          )}
        </button>

        {/* Sign-out button */}
        <button
          onClick={onSignOut}
          style={{
            background: 'transparent',
            color: 'oklch(0.50 0 0)',
            border: '1px solid oklch(1 0 0 / 0.08)',
            borderRadius: '0.5rem',
            padding: '0.25rem 1rem',
            fontSize: '0.875rem',
            cursor: 'pointer',
            transition: 'all 0.2s ease',
          }}
          onMouseEnter={(e) => {
            (e.currentTarget as HTMLButtonElement).style.borderColor =
              'oklch(1 0 0 / 0.2)';
            (e.currentTarget as HTMLButtonElement).style.color = 'oklch(0.30 0 0)';
          }}
          onMouseLeave={(e) => {
            (e.currentTarget as HTMLButtonElement).style.borderColor =
              'oklch(1 0 0 / 0.08)';
            (e.currentTarget as HTMLButtonElement).style.color = 'oklch(0.50 0 0)';
          }}
        >
          Sign out
        </button>
      </div>
    </header>
  );
}
