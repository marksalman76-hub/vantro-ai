'use client';

import React, { useState, useEffect } from 'react';
import MetricCard from './MetricCard';

export interface CreditsData {
  total_credits: number;
  used_credits: number;
  remaining_credits: number;
  tier: string;
}

export interface AgentUsage {
  agent_id: string;
  agent_name: string;
  count: number;
}

export interface StatusStripProps {
  credits: CreditsData | null;
  completedThisMonth: number;
  pendingApprovals: number;
  topAgents: AgentUsage[];
}

interface AgentBarProps {
  name: string;
  count: number;
  max: number;
}

function AgentBar({ name, count, max }: AgentBarProps) {
  const percentage = max > 0 ? (count / max) * 100 : 0;

  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: '0.75rem',
        paddingBottom: '0.75rem',
      }}
    >
      <div
        style={{
          minWidth: '100px',
          fontSize: '0.875rem',
          color: 'oklch(0.50 0 0)',
          overflow: 'hidden',
          textOverflow: 'ellipsis',
          whiteSpace: 'nowrap',
        }}
      >
        {name}
      </div>
      <div
        style={{
          flex: 1,
          height: '0.5rem',
          backgroundColor: 'oklch(1 0 0 / 0.08)',
          borderRadius: '0.25rem',
          overflow: 'hidden',
        }}
      >
        <div
          style={{
            height: '100%',
            width: '100%',
            backgroundColor: 'oklch(0.60 0.18 250)',
            transform: `scaleX(${percentage / 100})`,
            transformOrigin: 'left',
            transition: 'transform 0.3s ease',
          }}
        />
      </div>
      <div
        style={{
          minWidth: '40px',
          textAlign: 'right',
          fontSize: '0.875rem',
          fontWeight: 500,
          color: 'oklch(1 0 0)',
        }}
      >
        {count}
      </div>
    </div>
  );
}

export default function StatusStrip({
  credits,
  completedThisMonth,
  pendingApprovals,
  topAgents,
}: StatusStripProps) {
  const [collapsed, setCollapsed] = useState(false);

  // On mount, read localStorage and restore collapsed state
  useEffect(() => {
    const stored = localStorage.getItem('collapsed_sections');
    if (stored) {
      try {
        const sections = JSON.parse(stored);
        if (sections.status !== undefined) {
          setCollapsed(sections.status);
        }
      } catch {
        // Ignore parse errors
      }
    }
  }, []);

  // Toggle handler - persists to localStorage
  const handleToggle = () => {
    const newState = !collapsed;
    setCollapsed(newState);

    const stored = localStorage.getItem('collapsed_sections');
    let sections = {};
    try {
      sections = stored ? JSON.parse(stored) : {};
    } catch {
      sections = {};
    }
    sections.status = newState;
    localStorage.setItem('collapsed_sections', JSON.stringify(sections));
  };

  // Calculate credit percentage and color
  let creditsColor = 'white';
  let creditsPercentage = 0;
  if (credits) {
    creditsPercentage = (credits.remaining_credits / credits.total_credits) * 100;
    if (creditsPercentage < 20) {
      creditsColor = 'oklch(0.63 0.20 25)'; // red
    } else if (creditsPercentage < 50) {
      creditsColor = 'oklch(0.71 0.17 90)'; // amber
    } else {
      creditsColor = 'oklch(0.60 0.15 142)'; // green
    }
  }

  // Find max count for progress bar scaling
  const maxCount = topAgents.length > 0 ? Math.max(...topAgents.map(a => a.count)) : 1;

  return (
    <div
      style={{
        background: 'oklch(1 0 0 / 0.04)',
        border: '1px solid oklch(1 0 0 / 0.08)',
        borderRadius: '1rem',
        padding: '1.25rem',
        marginBottom: '1.5rem',
      }}
    >
      {/* Header */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          marginBottom: collapsed ? 0 : '1.5rem',
        }}
      >
        <h3
          style={{
            margin: 0,
            fontSize: '1.125rem',
            fontWeight: 600,
            color: 'oklch(1 0 0)',
          }}
        >
          Status
        </h3>
        <button
          onClick={handleToggle}
          style={{
            background: 'none',
            border: 'none',
            cursor: 'pointer',
            fontSize: '1rem',
            color: 'oklch(0.50 0 0)',
            padding: '0.25rem 0.5rem',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          {collapsed ? '▶' : '▼'}
        </button>
      </div>

      {/* Metrics - rendered only when expanded */}
      {!collapsed && (
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
            gap: '1rem',
            marginBottom: '1.5rem',
          }}
        >
          {/* Card 1: Credits remaining */}
          {credits && (
            <MetricCard
              label="Credits remaining"
              value={credits.remaining_credits}
              sub={`of ${credits.total_credits} total`}
              color={creditsColor}
            />
          )}

          {/* Card 2: Jobs completed this month */}
          <MetricCard
            label="Jobs completed this month"
            value={completedThisMonth}
            sub="completed status"
          />

          {/* Card 3: Next billing date */}
          <MetricCard
            label="Next billing date"
            value="—"
            sub="Manage in Billing"
          />

          {/* Card 4: Top agents chart */}
          <div
            style={{
              background: 'oklch(1 0 0 / 0.02)',
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
                marginBottom: '0.5rem',
              }}
            >
              Top agents
            </label>
            {topAgents.length > 0 ? (
              <div style={{ display: 'flex', flexDirection: 'column' }}>
                {topAgents.map((agent) => (
                  <AgentBar
                    key={agent.agent_id}
                    name={agent.agent_name}
                    count={agent.count}
                    max={maxCount}
                  />
                ))}
              </div>
            ) : (
              <div
                style={{
                  fontSize: '0.875rem',
                  color: 'oklch(0.50 0 0)',
                  fontStyle: 'italic',
                  paddingTop: '0.5rem',
                }}
              >
                No jobs run yet
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
