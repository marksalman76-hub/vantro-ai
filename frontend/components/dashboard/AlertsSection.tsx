'use client';

import React from 'react';
import Link from 'next/link';

interface Announcement {
  id: string;
  title: string;
  body: string;
  affects: string | null;
  type: string;
  show_as: string;
}

interface AlertsSectionProps {
  announcements: Announcement[];
  pendingApprovals: number;
  failedJobs: number;
  dismissed: Set<string>;
  onDismiss: (id: string) => void;
}

const ANN_INLINE_STYLES: Record<string, { text: string; bg: string; border: string }> = {
  info: {
    text: 'oklch(0.78 0.13 250)',
    bg: 'oklch(0.95 0.04 250)',
    border: 'oklch(0.8 0.08 250)',
  },
  new_feature: {
    text: 'oklch(0.78 0.13 250)',
    bg: 'oklch(0.95 0.04 250)',
    border: 'oklch(0.8 0.08 250)',
  },
  new_agent: {
    text: 'oklch(0.78 0.13 250)',
    bg: 'oklch(0.95 0.04 250)',
    border: 'oklch(0.8 0.08 250)',
  },
  warning: {
    text: 'oklch(0.82 0.18 65)',
    bg: 'oklch(0.97 0.08 65)',
    border: 'oklch(0.85 0.12 65)',
  },
  maintenance: {
    text: 'oklch(0.75 0.18 55)',
    bg: 'oklch(0.93 0.08 55)',
    border: 'oklch(0.78 0.12 55)',
  },
};

export default function AlertsSection({
  announcements,
  pendingApprovals,
  failedJobs,
  dismissed,
  onDismiss,
}: AlertsSectionProps) {
  // Filter visible announcements: show_as='banner' and not dismissed
  const visibleAnnouncements = announcements.filter(
    (ann) => ann.show_as === 'banner' && !dismissed.has(ann.id)
  );

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        gap: '1rem',
      }}
    >
      {/* Platform Announcements */}
      {visibleAnnouncements.map((ann) => {
        const style = ANN_INLINE_STYLES[ann.type] || ANN_INLINE_STYLES.info;
        return (
          <div
            key={ann.id}
            data-testid="announcement-banner"
            style={{
              background: style.bg,
              border: `1px solid ${style.border}`,
              borderRadius: '0.75rem',
              padding: '1rem',
              display: 'flex',
              flexDirection: 'row',
              gap: '1rem',
              alignItems: 'flex-start',
              justifyContent: 'space-between',
            }}
          >
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
                  fontWeight: 600,
                  color: style.text,
                }}
              >
                {ann.title}
              </div>
              <div
                style={{
                  fontSize: '0.75rem',
                  color: 'oklch(0.39 0.009 264.4)',
                  lineHeight: 1.4,
                }}
              >
                {ann.body}
              </div>
              {ann.affects && (
                <div
                  style={{
                    fontSize: '0.7rem',
                    color: style.text,
                    marginTop: '0.5rem',
                    fontWeight: 500,
                  }}
                >
                  Affects: {ann.affects}
                </div>
              )}
            </div>
            <button
              onClick={() => onDismiss(ann.id)}
              style={{
                background: 'transparent',
                border: 'none',
                color: style.text,
                cursor: 'pointer',
                fontSize: '1.25rem',
                padding: '0',
                marginLeft: '0.5rem',
                flexShrink: 0,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
              aria-label={`Dismiss ${ann.title}`}
            >
              ✕
            </button>
          </div>
        );
      })}

      {/* Action Cards */}
      <div
        style={{
          display: 'flex',
          flexDirection: 'row',
          gap: '1rem',
          flexWrap: 'wrap',
        }}
      >
        {pendingApprovals > 0 && (
          <Link
            href="/dashboard/approvals"
            style={{
              minWidth: '180px',
              background: 'oklch(0.93 0.08 55)',
              border: '1px solid oklch(0.78 0.12 55)',
              borderRadius: '0.75rem',
              padding: '1rem',
              display: 'flex',
              flexDirection: 'column',
              gap: '0.5rem',
              textDecoration: 'none',
              cursor: 'pointer',
              transition: 'all 0.2s ease',
            }}
            onMouseEnter={(e) => {
              (e.currentTarget as HTMLElement).style.background =
                'oklch(0.91 0.1 55)';
              (e.currentTarget as HTMLElement).style.transform =
                'translateY(-2px)';
            }}
            onMouseLeave={(e) => {
              (e.currentTarget as HTMLElement).style.background =
                'oklch(0.93 0.08 55)';
              (e.currentTarget as HTMLElement).style.transform =
                'translateY(0)';
            }}
          >
            <div
              style={{
                fontSize: '0.75rem',
                color: 'oklch(0.39 0.009 264.4)',
                textTransform: 'uppercase',
                fontWeight: 500,
                letterSpacing: '0.05em',
              }}
            >
              Pending Approvals
            </div>
            <div
              style={{
                fontSize: '1.875rem',
                fontWeight: 700,
                color: 'oklch(0.75 0.18 55)',
              }}
            >
              {pendingApprovals}
            </div>
          </Link>
        )}

        {failedJobs > 0 && (
          <Link
            href="/dashboard/jobs?filter=failed"
            style={{
              minWidth: '180px',
              background: 'oklch(0.92 0.12 10)',
              border: '1px solid oklch(0.65 0.2 10)',
              borderRadius: '0.75rem',
              padding: '1rem',
              display: 'flex',
              flexDirection: 'column',
              gap: '0.5rem',
              textDecoration: 'none',
              cursor: 'pointer',
              transition: 'all 0.2s ease',
            }}
            onMouseEnter={(e) => {
              (e.currentTarget as HTMLElement).style.background =
                'oklch(0.9 0.14 10)';
              (e.currentTarget as HTMLElement).style.transform =
                'translateY(-2px)';
            }}
            onMouseLeave={(e) => {
              (e.currentTarget as HTMLElement).style.background =
                'oklch(0.92 0.12 10)';
              (e.currentTarget as HTMLElement).style.transform =
                'translateY(0)';
            }}
          >
            <div
              style={{
                fontSize: '0.75rem',
                color: 'oklch(0.39 0.009 264.4)',
                textTransform: 'uppercase',
                fontWeight: 500,
                letterSpacing: '0.05em',
              }}
            >
              Failed Jobs
            </div>
            <div
              style={{
                fontSize: '1.875rem',
                fontWeight: 700,
                color: 'oklch(0.65 0.2 10)',
              }}
            >
              {failedJobs}
            </div>
          </Link>
        )}
      </div>
    </div>
  );
}
