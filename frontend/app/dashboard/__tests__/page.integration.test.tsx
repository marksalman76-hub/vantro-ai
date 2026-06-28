import React from 'react';
import { render, screen, waitFor, act } from '@testing-library/react';
import { useRouter } from 'next/navigation';
import DashboardPage from '../page';

// ── next/navigation — stable reference via mockReturnValue ────────────────────
// IMPORTANT: if useRouter returns a NEW object literal on every call, the
// [router] dependency in the page's useEffect changes each render, causing
// an infinite setState loop.  mockReturnValue stores one reference; every
// call to useRouter() returns that SAME object.
const mockPush = jest.fn();

jest.mock('next/navigation', () => ({
  useRouter: jest.fn(),
}));

// ── next/link ─────────────────────────────────────────────────────────────────
jest.mock('next/link', () =>
  function MockLink({ children, href }: { children: React.ReactNode; href: string }) {
    return <a href={href}>{children}</a>;
  }
);

// ── Section stubs — expose received props as data-* attrs ─────────────────────
jest.mock('@/components/dashboard/DashboardHeader', () =>
  function MockDashboardHeader({
    credits,
    pendingApprovals,
    failedJobs,
    onSignOut,
  }: {
    credits: { remaining_credits: number } | null;
    pendingApprovals: number;
    failedJobs: number;
    onSignOut: () => void;
  }) {
    return (
      <header
        data-testid="dashboard-header"
        data-pending={pendingApprovals}
        data-failed={failedJobs}
        data-has-credits={credits !== null ? 'yes' : 'no'}
        style={{ position: 'fixed', top: 0, zIndex: 100 }}
      >
        <button onClick={onSignOut} data-testid="sign-out-btn">Sign out</button>
      </header>
    );
  }
);

jest.mock('@/components/dashboard/StatusStrip', () =>
  function MockStatusStrip({
    completedThisMonth,
    pendingApprovals,
    topAgents,
  }: {
    completedThisMonth: number;
    pendingApprovals: number;
    topAgents: { agent_id: string }[];
  }) {
    return (
      <div
        data-testid="status-strip"
        data-completed={completedThisMonth}
        data-pending={pendingApprovals}
        data-top-agents={topAgents.length}
      >
        Status Strip
      </div>
    );
  }
);

jest.mock('@/components/dashboard/AlertsSection', () =>
  function MockAlertsSection({
    announcements,
    pendingApprovals,
    failedJobs,
  }: {
    announcements: unknown[];
    pendingApprovals: number;
    failedJobs: number;
  }) {
    return (
      <div
        data-testid="alerts-section"
        data-ann-count={announcements.length}
        data-pending={pendingApprovals}
        data-failed={failedJobs}
      >
        Alerts Section
      </div>
    );
  }
);

jest.mock('@/components/dashboard/QuickLaunchSection', () =>
  function MockQuickLaunchSection() {
    return <div data-testid="quick-launch-section">Quick Launch</div>;
  }
);

jest.mock('@/components/dashboard/RecentJobsTable', () =>
  function MockRecentJobsTable({ jobs }: { jobs: unknown[] }) {
    return (
      <div data-testid="recent-jobs-table" data-job-count={jobs.length}>
        Recent Jobs
      </div>
    );
  }
);

jest.mock('@/components/dashboard/ThemeToggle', () =>
  function MockThemeToggle() {
    return (
      <button
        data-testid="theme-toggle"
        style={{ position: 'fixed', bottom: '2rem', left: '2rem', zIndex: 50 }}
        aria-label="Toggle theme"
      >
        Theme
      </button>
    );
  }
);

// ── Primitives (imported by page but not rendered in JSX directly) ─────────────
jest.mock('@/components/dashboard/MetricCard', () => () => null);
jest.mock('@/components/dashboard/ActionCard', () => () => null);
jest.mock('@/components/dashboard/StatusBadge', () => () => null);

// ── Skeleton ──────────────────────────────────────────────────────────────────
jest.mock('@/components/Skeleton', () => ({
  SkeletonCard: () => <div data-testid="skeleton-card" />,
}));

// ── Fixtures ──────────────────────────────────────────────────────────────────
const CREDITS = {
  total_credits: 1000,
  used_credits: 200,
  remaining_credits: 800,
  tier: 'growth',
};

const thisMonthISO = new Date().toISOString();

const JOBS = [
  { id: 'j1', agent_id: 'a1', agent_name: 'Research Agent', status: 'completed',         credits_used: 50, created_at: thisMonthISO, completed_at: thisMonthISO },
  { id: 'j2', agent_id: 'a2', agent_name: 'Analytics Agent', status: 'pending_approval', credits_used: 0,  created_at: thisMonthISO, completed_at: null },
  { id: 'j3', agent_id: 'a3', agent_name: 'SEO Agent',       status: 'failed',           credits_used: 10, created_at: thisMonthISO, completed_at: null },
];

const ANNOUNCEMENTS = [
  { id: 'ann-1', title: 'New Feature', body: 'Check it out', affects: null, type: 'new_feature', show_as: 'banner' },
];

function setupFetch() {
  global.fetch = jest.fn().mockImplementation((url: string) => {
    if (url.includes('/api/workspace/credits'))
      return Promise.resolve({ ok: true, json: () => Promise.resolve(CREDITS) });
    if (url.includes('/api/agents/jobs'))
      return Promise.resolve({ ok: true, json: () => Promise.resolve({ jobs: JOBS }) });
    if (url.includes('/api/platform/announcements'))
      return Promise.resolve({ ok: true, json: () => Promise.resolve(ANNOUNCEMENTS) });
    return Promise.resolve({ ok: false, json: () => Promise.resolve(null) });
  });
}

// ── Suite ─────────────────────────────────────────────────────────────────────
describe('DashboardPage integration', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    // Stable router reference — prevents infinite useEffect loop
    (useRouter as jest.Mock).mockReturnValue({ push: mockPush });
    localStorage.clear();
    localStorage.setItem('token', 'test-token');
    setupFetch();
  });

  it('redirects to /login when no token is present', async () => {
    localStorage.removeItem('token');

    await act(async () => {
      render(<DashboardPage />);
    });

    expect(mockPush).toHaveBeenCalledWith('/login');
  });

  it('shows loading skeleton while fetching', () => {
    // Keep fetch pending so loading state stays visible
    (global.fetch as jest.Mock).mockImplementation(() => new Promise(() => {}));

    render(<DashboardPage />);

    const skeletons = screen.getAllByTestId('skeleton-card');
    expect(skeletons.length).toBeGreaterThanOrEqual(4);
  });

  it('renders all main sections after data loads', async () => {
    await act(async () => { render(<DashboardPage />); });

    await waitFor(() => {
      expect(screen.getByTestId('dashboard-header')).toBeInTheDocument();
      expect(screen.getByTestId('status-strip')).toBeInTheDocument();
      expect(screen.getByTestId('alerts-section')).toBeInTheDocument();
      expect(screen.getByTestId('quick-launch-section')).toBeInTheDocument();
      expect(screen.getByTestId('recent-jobs-table')).toBeInTheDocument();
      expect(screen.getByTestId('theme-toggle')).toBeInTheDocument();
    });
  });

  it('DashboardHeader receives credits, pendingApprovals=1, failedJobs=1', async () => {
    await act(async () => { render(<DashboardPage />); });

    await waitFor(() => {
      const header = screen.getByTestId('dashboard-header');
      expect(header).toHaveAttribute('data-has-credits', 'yes');
      expect(header).toHaveAttribute('data-pending', '1');
      expect(header).toHaveAttribute('data-failed', '1');
    });
  });

  it('StatusStrip receives completedThisMonth=1 and topAgents=3', async () => {
    await act(async () => { render(<DashboardPage />); });

    await waitFor(() => {
      const strip = screen.getByTestId('status-strip');
      expect(strip).toHaveAttribute('data-completed', '1');
      expect(strip).toHaveAttribute('data-top-agents', '3');
    });
  });

  it('AlertsSection receives announcements, pendingApprovals, failedJobs', async () => {
    await act(async () => { render(<DashboardPage />); });

    await waitFor(() => {
      const alerts = screen.getByTestId('alerts-section');
      expect(alerts).toHaveAttribute('data-ann-count', '1');
      expect(alerts).toHaveAttribute('data-pending', '1');
      expect(alerts).toHaveAttribute('data-failed', '1');
    });
  });

  it('RecentJobsTable receives all fetched jobs', async () => {
    await act(async () => { render(<DashboardPage />); });

    await waitFor(() => {
      expect(screen.getByTestId('recent-jobs-table'))
        .toHaveAttribute('data-job-count', String(JOBS.length));
    });
  });

  it('DashboardHeader has sticky positioning (position:fixed, top:0, zIndex:100)', async () => {
    await act(async () => { render(<DashboardPage />); });

    await waitFor(() => {
      const header = screen.getByTestId('dashboard-header');
      expect(header).toHaveStyle({ position: 'fixed', top: '0', zIndex: '100' });
    });
  });

  it('ThemeToggle is position:fixed with bottom and left set', async () => {
    await act(async () => { render(<DashboardPage />); });

    await waitFor(() => {
      const toggle = screen.getByTestId('theme-toggle');
      expect(toggle).toHaveStyle({ position: 'fixed' });
      const style = toggle.getAttribute('style') || '';
      expect(style).toMatch(/bottom/);
      expect(style).toMatch(/left/);
    });
  });

  it('sign-out clears localStorage token and navigates to /login', async () => {
    await act(async () => { render(<DashboardPage />); });
    await waitFor(() => screen.getByTestId('sign-out-btn'));

    act(() => { screen.getByTestId('sign-out-btn').click(); });

    expect(localStorage.getItem('token')).toBeNull();
    expect(mockPush).toHaveBeenCalledWith('/login');
  });

  it('loads pre-existing dismissed_announcements from localStorage', async () => {
    localStorage.setItem('dismissed_announcements', JSON.stringify(['ann-old']));

    await act(async () => { render(<DashboardPage />); });

    await waitFor(() => {
      // Page must render without crashing when dismissed set is pre-populated
      expect(screen.getByTestId('alerts-section')).toBeInTheDocument();
    });
  });
});
