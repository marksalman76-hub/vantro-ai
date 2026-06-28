import React from 'react';
import { render, screen } from '@testing-library/react';
import DashboardHeader from '../DashboardHeader';

// Mock next/link
jest.mock('next/link', () => {
  return ({ children, href }: { children: React.ReactNode; href: string }) => (
    <a href={href}>{children}</a>
  );
});

describe('DashboardHeader', () => {
  const mockOnSignOut = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders "Run Agent" CTA button', () => {
    render(
      <DashboardHeader
        credits={null}
        pendingApprovals={0}
        failedJobs={0}
        onSignOut={mockOnSignOut}
      />
    );

    const runAgentButton = screen.getByText('Run Agent');
    expect(runAgentButton).toBeInTheDocument();
    expect(runAgentButton.closest('a')).toHaveAttribute('href', '/dashboard/agents');
  });

  it('displays credits count (800 from 1000 total)', () => {
    const creditsData = {
      total_credits: 1000,
      used_credits: 200,
      remaining_credits: 800,
    };

    render(
      <DashboardHeader
        credits={creditsData}
        pendingApprovals={0}
        failedJobs={0}
        onSignOut={mockOnSignOut}
      />
    );

    expect(screen.getByText('800')).toBeInTheDocument();
    expect(screen.getByText('credits')).toBeInTheDocument();
  });

  it('displays alert count badge (pending + failed)', () => {
    render(
      <DashboardHeader
        credits={null}
        pendingApprovals={3}
        failedJobs={2}
        onSignOut={mockOnSignOut}
      />
    );

    const alertButton = screen.getByText('Alerts');
    expect(alertButton).toBeInTheDocument();
    // Should display 5 (3 + 2) as badge
    expect(screen.getByText('5')).toBeInTheDocument();
  });

  it('has sticky positioning (position: fixed, top: 0, z-index: 100)', () => {
    const { container } = render(
      <DashboardHeader
        credits={null}
        pendingApprovals={0}
        failedJobs={0}
        onSignOut={mockOnSignOut}
      />
    );

    const header = container.firstChild as HTMLElement;
    const computedStyle = window.getComputedStyle(header);

    expect(header).toHaveStyle({ position: 'fixed', top: '0', zIndex: '100' });
  });
});
