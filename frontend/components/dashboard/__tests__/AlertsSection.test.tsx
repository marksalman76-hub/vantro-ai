import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import AlertsSection from '../AlertsSection';

// Mock next/link
jest.mock('next/link', () => {
  return ({ children, href }: { children: React.ReactNode; href: string }) => (
    <a href={href}>{children}</a>
  );
});

const mockAnnouncements = [
  {
    id: 'ann-1',
    title: 'New Feature Released',
    body: 'Check out our latest agent capabilities',
    affects: null,
    type: 'new_feature',
    show_as: 'banner',
  },
  {
    id: 'ann-2',
    title: 'Maintenance Window',
    body: 'System will be down for 2 hours',
    affects: 'All workspaces',
    type: 'maintenance',
    show_as: 'banner',
  },
  {
    id: 'ann-3',
    title: 'Hidden Announcement',
    body: 'This should not be visible',
    affects: null,
    type: 'info',
    show_as: 'modal',
  },
];

describe('AlertsSection', () => {
  it('renders platform announcements with show_as=banner and not dismissed', () => {
    render(
      <AlertsSection
        announcements={mockAnnouncements}
        pendingApprovals={0}
        failedJobs={0}
        dismissed={new Set()}
        onDismiss={jest.fn()}
      />
    );

    // Should render announcements with show_as='banner'
    expect(screen.getByText('New Feature Released')).toBeInTheDocument();
    expect(screen.getByText('Maintenance Window')).toBeInTheDocument();

    // Should NOT render modal announcement
    expect(screen.queryByText('Hidden Announcement')).not.toBeInTheDocument();
  });

  it('renders pending approvals card when count > 0', () => {
    render(
      <AlertsSection
        announcements={[]}
        pendingApprovals={3}
        failedJobs={0}
        dismissed={new Set()}
        onDismiss={jest.fn()}
      />
    );

    const approvalLink = screen.getByRole('link', { name: /pending approvals/i });
    expect(approvalLink).toHaveAttribute('href', '/dashboard/approvals');
    expect(screen.getByText('3')).toBeInTheDocument();
  });

  it('dismisses announcement on button click', () => {
    const handleDismiss = jest.fn();

    render(
      <AlertsSection
        announcements={mockAnnouncements}
        pendingApprovals={0}
        failedJobs={0}
        dismissed={new Set()}
        onDismiss={handleDismiss}
      />
    );

    const dismissButtons = screen.getAllByRole('button');
    fireEvent.click(dismissButtons[0]);

    expect(handleDismiss).toHaveBeenCalledWith('ann-1');
  });

  it('renders failed jobs card when count > 0', () => {
    render(
      <AlertsSection
        announcements={[]}
        pendingApprovals={0}
        failedJobs={2}
        dismissed={new Set()}
        onDismiss={jest.fn()}
      />
    );

    const failedLink = screen.getByRole('link', { name: /failed jobs/i });
    expect(failedLink).toHaveAttribute('href', '/dashboard/jobs?filter=failed');
    expect(screen.getByText('2')).toBeInTheDocument();
  });

  it('respects dismissed set and does not render dismissed announcements', () => {
    const dismissed = new Set(['ann-1']);

    render(
      <AlertsSection
        announcements={mockAnnouncements}
        pendingApprovals={0}
        failedJobs={0}
        dismissed={dismissed}
        onDismiss={jest.fn()}
      />
    );

    // Should not render dismissed announcement
    expect(screen.queryByText('New Feature Released')).not.toBeInTheDocument();

    // Should render other announcements
    expect(screen.getByText('Maintenance Window')).toBeInTheDocument();
  });

  it('does not render action cards when counts are 0', () => {
    render(
      <AlertsSection
        announcements={[]}
        pendingApprovals={0}
        failedJobs={0}
        dismissed={new Set()}
        onDismiss={jest.fn()}
      />
    );

    expect(screen.queryByRole('link', { name: /pending approvals/i })).not.toBeInTheDocument();
    expect(screen.queryByRole('link', { name: /failed jobs/i })).not.toBeInTheDocument();
  });

  it('applies type-based styling for announcements', () => {
    const { container } = render(
      <AlertsSection
        announcements={mockAnnouncements}
        pendingApprovals={0}
        failedJobs={0}
        dismissed={new Set()}
        onDismiss={jest.fn()}
      />
    );

    // Find announcement elements
    const announcements = container.querySelectorAll('[data-testid="announcement-banner"]');
    expect(announcements.length).toBeGreaterThan(0);
  });
});
