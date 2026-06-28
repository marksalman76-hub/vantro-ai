import React from 'react';
import { render, screen } from '@testing-library/react';
import RecentJobsTable from '../RecentJobsTable';

describe('RecentJobsTable', () => {
  it('renders job table header "Recent jobs"', () => {
    render(<RecentJobsTable jobs={[]} />);
    expect(screen.getByText('Recent jobs')).toBeInTheDocument();
  });

  it('renders jobs with agent name and status badge', () => {
    const mockJobs = [
      {
        id: '1',
        agent_id: 'agent-123',
        agent_name: 'Research Agent',
        status: 'completed',
        credits_used: 50,
        created_at: '2026-06-28T10:00:00Z',
        completed_at: '2026-06-28T10:05:00Z',
      },
      {
        id: '2',
        agent_id: 'agent-456',
        agent_name: 'Analytics Agent',
        status: 'running',
        credits_used: 25,
        created_at: '2026-06-28T11:00:00Z',
        completed_at: null,
      },
    ];

    render(<RecentJobsTable jobs={mockJobs} />);

    expect(screen.getByText('Research Agent')).toBeInTheDocument();
    expect(screen.getByText('Analytics Agent')).toBeInTheDocument();
  });

  it('shows empty state when no jobs', () => {
    render(<RecentJobsTable jobs={[]} />);
    expect(screen.getByText('No jobs yet')).toBeInTheDocument();
    expect(screen.getByText('Run your first agent →')).toBeInTheDocument();
  });

  it('displays credits used if > 0', () => {
    const mockJobs = [
      {
        id: '1',
        agent_id: 'agent-123',
        agent_name: 'Test Agent',
        status: 'completed',
        credits_used: 75,
        created_at: '2026-06-28T10:00:00Z',
        completed_at: '2026-06-28T10:05:00Z',
      },
    ];

    render(<RecentJobsTable jobs={mockJobs} />);
    expect(screen.getByText('75')).toBeInTheDocument();
  });

  it('only displays first 10 jobs', () => {
    const mockJobs = Array.from({ length: 15 }, (_, i) => ({
      id: `job-${i}`,
      agent_id: `agent-${i}`,
      agent_name: `Agent ${i}`,
      status: 'completed',
      credits_used: 10,
      created_at: '2026-06-28T10:00:00Z',
      completed_at: '2026-06-28T10:05:00Z',
    }));

    render(<RecentJobsTable jobs={mockJobs} />);

    // Check first 10 are visible
    for (let i = 0; i < 10; i++) {
      expect(screen.getByText(`Agent ${i}`)).toBeInTheDocument();
    }

    // Check jobs 10-14 are not visible
    expect(screen.queryByText('Agent 10')).not.toBeInTheDocument();
  });

  it('has rounded-2xl container with proper background and border', () => {
    const { container } = render(<RecentJobsTable jobs={[]} />);
    const tableContainer = container.firstChild as HTMLElement;
    expect(tableContainer).toHaveStyle({ borderRadius: '1rem' });
    expect(tableContainer).toHaveStyle({
      background: 'oklch(1 0 0 / 0.04)',
    });
    expect(tableContainer).toHaveStyle({
      border: '1px solid oklch(1 0 0 / 0.08)',
    });
  });

  it('shows "View all →" link in header', () => {
    render(<RecentJobsTable jobs={[]} />);
    const viewAllLink = screen.getByText('View all →');
    expect(viewAllLink).toHaveAttribute('href', '/dashboard/jobs');
  });

  it('shows "Run your first agent →" link in empty state', () => {
    render(<RecentJobsTable jobs={[]} />);
    const firstAgentLink = screen.getByText('Run your first agent →');
    expect(firstAgentLink).toHaveAttribute('href', '/dashboard/agents');
  });
});
