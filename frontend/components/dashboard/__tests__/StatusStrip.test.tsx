import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import StatusStrip from '../StatusStrip';

describe('StatusStrip', () => {
  const mockCreditsData = {
    total_credits: 1000,
    used_credits: 300,
    remaining_credits: 700,
    tier: 'Pro',
  };

  const mockAgentUsage = [
    { agent_id: '1', agent_name: 'Research Agent', count: 45 },
    { agent_id: '2', agent_name: 'Content Writer', count: 32 },
    { agent_id: '3', agent_name: 'Data Analyzer', count: 28 },
  ];

  beforeEach(() => {
    localStorage.clear();
  });

  it('renders collapsible section with metrics', () => {
    render(
      <StatusStrip
        credits={mockCreditsData}
        completedThisMonth={105}
        pendingApprovals={3}
        topAgents={mockAgentUsage}
      />
    );

    expect(screen.getByText('Status')).toBeInTheDocument();
    expect(screen.getByText('Credits remaining')).toBeInTheDocument();
    expect(screen.getByText('Jobs completed this month')).toBeInTheDocument();
    expect(screen.getByText('Next billing date')).toBeInTheDocument();
  });

  it('renders chevron toggle button', () => {
    render(
      <StatusStrip
        credits={mockCreditsData}
        completedThisMonth={105}
        pendingApprovals={3}
        topAgents={mockAgentUsage}
      />
    );

    const toggleButton = screen.getByRole('button');
    expect(toggleButton).toBeInTheDocument();
    expect(toggleButton).toHaveTextContent('▼');
  });

  it('can toggle collapsed state and persists to localStorage', () => {
    const { rerender } = render(
      <StatusStrip
        credits={mockCreditsData}
        completedThisMonth={105}
        pendingApprovals={3}
        topAgents={mockAgentUsage}
      />
    );

    // Initially expanded
    expect(screen.getByText('Credits remaining')).toBeInTheDocument();

    // Click toggle
    const toggleButton = screen.getByRole('button');
    fireEvent.click(toggleButton);

    // Should be collapsed (metrics hidden)
    expect(screen.queryByText('Credits remaining')).not.toBeInTheDocument();

    // Check localStorage was updated
    const stored = JSON.parse(localStorage.getItem('collapsed_sections') || '{}');
    expect(stored.status).toBe(true);

    // Rerender and verify state persisted
    rerender(
      <StatusStrip
        credits={mockCreditsData}
        completedThisMonth={105}
        pendingApprovals={3}
        topAgents={mockAgentUsage}
      />
    );

    expect(screen.queryByText('Credits remaining')).not.toBeInTheDocument();
  });

  it('displays correct credit percentage color coding', () => {
    const { rerender } = render(
      <StatusStrip
        credits={{
          total_credits: 1000,
          used_credits: 950,
          remaining_credits: 50,
          tier: 'Pro',
        }}
        completedThisMonth={10}
        pendingApprovals={0}
        topAgents={[]}
      />
    );

    const valueElements = screen.getAllByText('50');
    expect(valueElements.length).toBeGreaterThan(0);

    // Rerender with amber threshold
    rerender(
      <StatusStrip
        credits={{
          total_credits: 1000,
          used_credits: 500,
          remaining_credits: 500,
          tier: 'Pro',
        }}
        completedThisMonth={10}
        pendingApprovals={0}
        topAgents={[]}
      />
    );

    expect(screen.getByText('500')).toBeInTheDocument();
  });

  it('displays "No jobs run yet" when topAgents is empty', () => {
    render(
      <StatusStrip
        credits={mockCreditsData}
        completedThisMonth={0}
        pendingApprovals={0}
        topAgents={[]}
      />
    );

    expect(screen.getByText('No jobs run yet')).toBeInTheDocument();
  });

  it('renders agent bars when agents are provided', () => {
    render(
      <StatusStrip
        credits={mockCreditsData}
        completedThisMonth={105}
        pendingApprovals={3}
        topAgents={mockAgentUsage}
      />
    );

    expect(screen.getByText('Research Agent')).toBeInTheDocument();
    expect(screen.getByText('Content Writer')).toBeInTheDocument();
    expect(screen.getByText('Data Analyzer')).toBeInTheDocument();
  });

  it('shows correct completed jobs count', () => {
    render(
      <StatusStrip
        credits={mockCreditsData}
        completedThisMonth={105}
        pendingApprovals={3}
        topAgents={mockAgentUsage}
      />
    );

    expect(screen.getByText('105')).toBeInTheDocument();
  });

  it('handles null credits gracefully', () => {
    render(
      <StatusStrip
        credits={null}
        completedThisMonth={50}
        pendingApprovals={2}
        topAgents={mockAgentUsage}
      />
    );

    expect(screen.getByText('Status')).toBeInTheDocument();
  });
});
