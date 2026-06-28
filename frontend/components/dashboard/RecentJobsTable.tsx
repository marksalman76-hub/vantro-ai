'use client';

import React from 'react';
import Link from 'next/link';
import StatusBadge from './StatusBadge';

export interface HistoryJob {
  id: string;
  agent_id: string;
  agent_name: string;
  status: string;
  credits_used: number;
  created_at: string | null;
  completed_at: string | null;
}

interface RecentJobsTableProps {
  jobs: HistoryJob[];
}

function formatCreatedTime(dateString: string | null): string {
  if (!dateString) return '—';
  try {
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  } catch {
    return '—';
  }
}

export default function RecentJobsTable({ jobs }: RecentJobsTableProps) {
  const displayJobs = jobs.slice(0, 10);
  const hasJobs = displayJobs.length > 0;

  return (
    <div
      style={{
        borderRadius: '1rem',
        overflow: 'hidden',
        background: 'oklch(1 0 0 / 0.04)',
        border: '1px solid oklch(1 0 0 / 0.08)',
      }}
    >
      {/* Header */}
      <div
        style={{
          padding: '1.5rem 1.5rem',
          borderBottom: '1px solid oklch(1 0 0 / 0.08)',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
        }}
      >
        <h3
          style={{
            fontSize: '0.875rem',
            fontWeight: 600,
            color: 'white',
            margin: 0,
          }}
        >
          Recent jobs
        </h3>
        <Link
          href="/dashboard/jobs"
          style={{
            fontSize: '0.875rem',
            color: 'oklch(0.78 0.13 250)',
            textDecoration: 'none',
            transition: 'color 0.2s',
          }}
          onMouseEnter={(e) => {
            (e.currentTarget as HTMLAnchorElement).style.color =
              'oklch(0.85 0.16 250)';
          }}
          onMouseLeave={(e) => {
            (e.currentTarget as HTMLAnchorElement).style.color =
              'oklch(0.78 0.13 250)';
          }}
        >
          View all →
        </Link>
      </div>

      {/* Content */}
      {!hasJobs ? (
        <div
          style={{
            textAlign: 'center',
            padding: '3rem 1.5rem',
            color: 'oklch(0.39 0.009 264.4)',
            fontSize: '0.875rem',
          }}
        >
          <p style={{ margin: '0 0 1rem 0' }}>No jobs yet</p>
          <Link
            href="/dashboard/agents"
            style={{
              color: 'oklch(0.78 0.13 250)',
              textDecoration: 'none',
              transition: 'color 0.2s',
            }}
            onMouseEnter={(e) => {
              (e.currentTarget as HTMLAnchorElement).style.color =
                'oklch(0.85 0.16 250)';
            }}
            onMouseLeave={(e) => {
              (e.currentTarget as HTMLAnchorElement).style.color =
                'oklch(0.78 0.13 250)';
            }}
          >
            Run your first agent →
          </Link>
        </div>
      ) : (
        <div>
          {displayJobs.map((job) => (
            <div
              key={job.id}
              style={{
                padding: '0.75rem 1.5rem',
                borderBottom: '1px solid oklch(1 0 0 / 0.08)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                cursor: 'pointer',
                transition: 'background-color 0.2s',
              }}
              onMouseEnter={(e) => {
                (e.currentTarget as HTMLDivElement).style.backgroundColor =
                  'rgba(0, 0, 0, 0.2)';
              }}
              onMouseLeave={(e) => {
                (e.currentTarget as HTMLDivElement).style.backgroundColor =
                  'transparent';
              }}
            >
              {/* Left: Agent name + created time */}
              <div style={{ flex: 1, minWidth: 0 }}>
                <div
                  style={{
                    fontSize: '0.875rem',
                    fontWeight: 500,
                    color: 'white',
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                    whiteSpace: 'nowrap',
                  }}
                >
                  {job.agent_name}
                </div>
                <div
                  style={{
                    fontSize: '0.75rem',
                    color: 'oklch(0.39 0.009 264.4)',
                    marginTop: '0.25rem',
                  }}
                >
                  {formatCreatedTime(job.created_at)}
                </div>
              </div>

              {/* Status badge */}
              <div style={{ marginLeft: '1rem', marginRight: '1rem' }}>
                <StatusBadge status={job.status} />
              </div>

              {/* Right: Credits (if > 0) */}
              {job.credits_used > 0 && (
                <div
                  style={{
                    fontSize: '0.875rem',
                    fontWeight: 500,
                    color: 'oklch(0.75 0.22 145)',
                    minWidth: '3rem',
                    textAlign: 'right',
                  }}
                >
                  {job.credits_used}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
