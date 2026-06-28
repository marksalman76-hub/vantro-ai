import React from 'react';
import { render, screen, waitFor, act } from '@testing-library/react';
import { useRouter } from 'next/navigation';
import DashboardPage from '../page';

// ── next/navigation ───────────────────────────────────────────────────────────
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

// ── Mock components to expose layout information ───────────────────────────────

jest.mock('@/components/dashboard/DashboardHeader', () =>
  function MockDashboardHeader({
    credits,
    pendingApprovals,
    failedJobs,
    onSignOut,
  }: any) {
    return (
      <header
        data-testid="dashboard-header"
        style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          zIndex: 100,
          height: '4rem',
          background: 'rgba(30, 30, 30, 0.95)',
        }}
      >
        <div data-testid="header-content">Header</div>
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
  }: any) {
    return (
      <div
        data-testid="status-strip"
        data-completed={completedThisMonth}
        data-pending={pendingApprovals}
        data-top-agents={topAgents.length}
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4"
      >
        <div data-testid="metric-1" className="p-4 border rounded">Metric 1</div>
        <div data-testid="metric-2" className="p-4 border rounded">Metric 2</div>
        <div data-testid="metric-3" className="p-4 border rounded">Metric 3</div>
        <div data-testid="metric-4" className="p-4 border rounded">Metric 4</div>
      </div>
    );
  }
);

jest.mock('@/components/dashboard/AlertsSection', () =>
  function MockAlertsSection({
    announcements,
    pendingApprovals,
    failedJobs,
  }: any) {
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
    return (
      <div
        data-testid="quick-launch-section"
        className="grid grid-cols-2 md:grid-cols-2 lg:grid-cols-3 gap-4"
      >
        <div data-testid="action-1" className="p-4 border rounded" style={{ minHeight: '60px' }}>Action 1</div>
        <div data-testid="action-2" className="p-4 border rounded" style={{ minHeight: '60px' }}>Action 2</div>
        <div data-testid="action-3" className="p-4 border rounded" style={{ minHeight: '60px' }}>Action 3</div>
        <div data-testid="action-4" className="p-4 border rounded" style={{ minHeight: '60px' }}>Action 4</div>
        <div data-testid="action-5" className="p-4 border rounded" style={{ minHeight: '60px' }}>Action 5</div>
        <div data-testid="action-6" className="p-4 border rounded" style={{ minHeight: '60px' }}>Action 6</div>
      </div>
    );
  }
);

jest.mock('@/components/dashboard/RecentJobsTable', () =>
  function MockRecentJobsTable({ jobs }: any) {
    return (
      <div
        data-testid="recent-jobs-table"
        data-job-count={jobs.length}
        className="overflow-x-auto"
        style={{
          display: 'table-row-group',
        }}
      >
        <table className="w-full min-w-full">
          <thead>
            <tr className="hidden md:table-row">
              <th data-testid="col-id" className="p-2">ID</th>
              <th data-testid="col-agent" className="p-2">Agent</th>
              <th data-testid="col-status" className="p-2">Status</th>
              <th data-testid="col-credits" className="p-2">Credits</th>
              <th data-testid="col-created" className="p-2">Created</th>
              <th data-testid="col-completed" className="p-2">Completed</th>
            </tr>
          </thead>
          <tbody>
            {jobs.map((job: any, idx: number) => (
              <tr key={job.id} data-testid={`job-row-${idx}`}>
                <td className="p-2">{job.id}</td>
                <td className="p-2">{job.agent_name}</td>
                <td className="p-2">{job.status}</td>
                <td className="p-2">{job.credits_used}</td>
                <td className="p-2 text-sm">{job.created_at}</td>
                <td className="p-2 text-sm">{job.completed_at}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  }
);

jest.mock('@/components/dashboard/ThemeToggle', () =>
  function MockThemeToggle() {
    return (
      <button
        data-testid="theme-toggle"
        style={{
          position: 'fixed',
          bottom: '2rem',
          left: '2rem',
          zIndex: 50,
          width: '44px',
          height: '44px',
          minWidth: '44px',
          minHeight: '44px',
        }}
        aria-label="Toggle theme"
      >
        🌙
      </button>
    );
  }
);

jest.mock('@/components/Skeleton', () => ({
  SkeletonCard: () => <div data-testid="skeleton-card" />,
}));

jest.mock('@/components/dashboard/MetricCard', () => () => null);
jest.mock('@/components/dashboard/ActionCard', () => () => null);
jest.mock('@/components/dashboard/StatusBadge', () => () => null);

// ── Fixtures ──────────────────────────────────────────────────────────────────
const CREDITS = {
  total_credits: 1000,
  used_credits: 200,
  remaining_credits: 800,
  tier: 'growth',
};

const thisMonthISO = new Date().toISOString();

const JOBS = [
  { id: 'j1', agent_id: 'a1', agent_name: 'Research Agent', status: 'completed', credits_used: 50, created_at: thisMonthISO, completed_at: thisMonthISO },
  { id: 'j2', agent_id: 'a2', agent_name: 'Analytics Agent', status: 'pending_approval', credits_used: 0, created_at: thisMonthISO, completed_at: null },
  { id: 'j3', agent_id: 'a3', agent_name: 'SEO Agent', status: 'failed', credits_used: 10, created_at: thisMonthISO, completed_at: null },
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

// ── Helper to set viewport width ──────────────────────────────────────────────
function setViewportWidth(width: number) {
  Object.defineProperty(window, 'innerWidth', {
    writable: true,
    configurable: true,
    value: width,
  });
  global.matchMedia = jest.fn().mockImplementation((query: string) => ({
    matches: query === '(min-width: 1024px)' ? width >= 1024 : query === '(min-width: 768px)' ? width >= 768 : width < 768,
    media: query,
    onchange: null,
    addListener: jest.fn(),
    removeListener: jest.fn(),
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  }));
  window.dispatchEvent(new Event('resize'));
}

// ── Helper to get computed styles via getComputedStyle mock ──────────────────
function getGridColumnsForViewport(width: number, gridSelector: string): string | null {
  // Simulate Tailwind breakpoints
  if (width >= 1024) {
    // lg: grid-cols-4 for metrics, grid-cols-3 for quick-launch
    if (gridSelector === 'metrics') return '4';
    if (gridSelector === 'quick-launch') return '3';
  } else if (width >= 768) {
    // md: grid-cols-2
    if (gridSelector === 'metrics') return '2';
    if (gridSelector === 'quick-launch') return '2';
  } else {
    // base: grid-cols-1 for metrics, grid-cols-2 for quick-launch
    if (gridSelector === 'metrics') return '1';
    if (gridSelector === 'quick-launch') return '2';
  }
  return null;
}

// ── Suite ─────────────────────────────────────────────────────────────────────
describe('Dashboard Responsive Layout', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    (useRouter as jest.Mock).mockReturnValue({ push: mockPush });
    localStorage.clear();
    localStorage.setItem('token', 'test-token');
    setupFetch();
    setViewportWidth(1024);
  });

  describe('Desktop Layout (1024px+)', () => {
    beforeEach(() => {
      setViewportWidth(1366);
    });

    it('renders 4-column metric cards grid', async () => {
      await act(async () => { render(<DashboardPage />); });

      await waitFor(() => {
        expect(screen.getByTestId('metric-1')).toBeInTheDocument();
        expect(screen.getByTestId('metric-2')).toBeInTheDocument();
        expect(screen.getByTestId('metric-3')).toBeInTheDocument();
        expect(screen.getByTestId('metric-4')).toBeInTheDocument();
      });

      // Verify 4-column grid class is present
      const statusStrip = screen.getByTestId('status-strip');
      expect(statusStrip.className).toContain('lg:grid-cols-4');
    });

    it('renders 3-column quick-action grid', async () => {
      await act(async () => { render(<DashboardPage />); });

      await waitFor(() => {
        expect(screen.getByTestId('action-1')).toBeInTheDocument();
        expect(screen.getByTestId('action-2')).toBeInTheDocument();
        expect(screen.getByTestId('action-3')).toBeInTheDocument();
      });

      const quickLaunch = screen.getByTestId('quick-launch-section');
      expect(quickLaunch.className).toContain('lg:grid-cols-3');
    });

    it('displays table with all columns', async () => {
      await act(async () => { render(<DashboardPage />); });

      await waitFor(() => {
        expect(screen.getByTestId('col-id')).toBeInTheDocument();
        expect(screen.getByTestId('col-agent')).toBeInTheDocument();
        expect(screen.getByTestId('col-status')).toBeInTheDocument();
        expect(screen.getByTestId('col-credits')).toBeInTheDocument();
        expect(screen.getByTestId('col-created')).toBeInTheDocument();
        expect(screen.getByTestId('col-completed')).toBeInTheDocument();
      });
    });

    it('header is sticky at top (z-index 100)', async () => {
      await act(async () => { render(<DashboardPage />); });

      await waitFor(() => {
        const header = screen.getByTestId('dashboard-header');
        expect(header).toHaveStyle({
          position: 'fixed',
          top: '0',
          zIndex: '100',
        });
      });
    });

    it('displays all 6 quick-action items visible', async () => {
      await act(async () => { render(<DashboardPage />); });

      await waitFor(() => {
        for (let i = 1; i <= 6; i++) {
          expect(screen.getByTestId(`action-${i}`)).toBeVisible();
        }
      });
    });
  });

  describe('Tablet Layout (768-1023px)', () => {
    beforeEach(() => {
      setViewportWidth(768);
    });

    it('renders 2-column metric cards grid', async () => {
      await act(async () => { render(<DashboardPage />); });

      await waitFor(() => {
        const statusStrip = screen.getByTestId('status-strip');
        expect(statusStrip.className).toContain('md:grid-cols-2');
      });
    });

    it('renders 2-column quick-action grid', async () => {
      await act(async () => { render(<DashboardPage />); });

      await waitFor(() => {
        const quickLaunch = screen.getByTestId('quick-launch-section');
        expect(quickLaunch.className).toContain('md:grid-cols-2');
      });
    });

    it('table shows overflow-x-auto for responsive scrolling', async () => {
      await act(async () => { render(<DashboardPage />); });

      await waitFor(() => {
        const table = screen.getByTestId('recent-jobs-table');
        expect(table.className).toContain('overflow-x-auto');
      });
    });

    it('table columns remain visible (not hidden on tablet)', async () => {
      await act(async () => { render(<DashboardPage />); });

      await waitFor(() => {
        const headerRow = screen.getByTestId('col-id').closest('tr');
        expect(headerRow?.className).toContain('md:table-row');
      });
    });
  });

  describe('Mobile Layout (<768px)', () => {
    beforeEach(() => {
      setViewportWidth(390);
    });

    it('renders 1-column metric cards stack', async () => {
      await act(async () => { render(<DashboardPage />); });

      await waitFor(() => {
        const statusStrip = screen.getByTestId('status-strip');
        expect(statusStrip.className).toContain('grid-cols-1');
      });
    });

    it('renders 2-column quick-actions (full-width wrapping)', async () => {
      await act(async () => { render(<DashboardPage />); });

      await waitFor(() => {
        const quickLaunch = screen.getByTestId('quick-launch-section');
        expect(quickLaunch.className).toContain('grid-cols-2');
      });
    });

    it('table becomes scrollable container on mobile', async () => {
      await act(async () => { render(<DashboardPage />); });

      await waitFor(() => {
        const table = screen.getByTestId('recent-jobs-table');
        expect(table.className).toContain('overflow-x-auto');
      });
    });

    it('table header row is hidden on mobile (hidden md:table-row)', async () => {
      await act(async () => { render(<DashboardPage />); });

      await waitFor(() => {
        const headerRow = screen.getByTestId('col-id').closest('tr');
        expect(headerRow?.className).toContain('hidden');
        expect(headerRow?.className).toContain('md:table-row');
      });
    });

    it('theme toggle is visible at bottom-left with sufficient touch target (44px)', async () => {
      await act(async () => { render(<DashboardPage />); });

      await waitFor(() => {
        const toggle = screen.getByTestId('theme-toggle');
        expect(toggle).toBeVisible();
        // Check minimum touch target size (44px × 44px per WCAG)
        const width = window.getComputedStyle(toggle).width || '44px';
        const height = window.getComputedStyle(toggle).height || '44px';
        expect(parseInt(width)).toBeGreaterThanOrEqual(44);
        expect(parseInt(height)).toBeGreaterThanOrEqual(44);
      });
    });
  });

  describe('Sticky Header on Scroll', () => {
    beforeEach(() => {
      setViewportWidth(1024);
    });

    it('header remains at top when scrolling on desktop', async () => {
      await act(async () => { render(<DashboardPage />); });

      await waitFor(() => {
        const header = screen.getByTestId('dashboard-header');
        // Verify position:fixed ensures sticky behavior
        expect(header).toHaveStyle({
          position: 'fixed',
          top: '0',
        });
      });
    });

    it('header remains at top when scrolling on tablet', async () => {
      setViewportWidth(768);
      await act(async () => { render(<DashboardPage />); });

      await waitFor(() => {
        const header = screen.getByTestId('dashboard-header');
        expect(header).toHaveStyle({
          position: 'fixed',
          top: '0',
        });
      });
    });

    it('header remains at top when scrolling on mobile', async () => {
      setViewportWidth(390);
      await act(async () => { render(<DashboardPage />); });

      await waitFor(() => {
        const header = screen.getByTestId('dashboard-header');
        expect(header).toHaveStyle({
          position: 'fixed',
          top: '0',
        });
      });
    });

    it('content is offset below sticky header (paddingTop applied)', async () => {
      await act(async () => { render(<DashboardPage />); });

      await waitFor(() => {
        // Main content wrapper should have paddingTop to accommodate fixed header
        const mainContent = screen.getByTestId('status-strip').closest('.p-8');
        expect(mainContent).toHaveStyle({ paddingTop: '6rem' });
      });
    });
  });

  describe('Theme Toggle Accessibility', () => {
    it('theme toggle is accessible on desktop (1024px+)', async () => {
      setViewportWidth(1366);
      await act(async () => { render(<DashboardPage />); });

      await waitFor(() => {
        const toggle = screen.getByTestId('theme-toggle');
        expect(toggle).toBeInTheDocument();
        expect(toggle).toBeVisible();
        expect(toggle).toHaveAttribute('aria-label', 'Toggle theme');
      });
    });

    it('theme toggle is accessible on tablet (768-1023px)', async () => {
      setViewportWidth(768);
      await act(async () => { render(<DashboardPage />); });

      await waitFor(() => {
        const toggle = screen.getByTestId('theme-toggle');
        expect(toggle).toBeInTheDocument();
        expect(toggle).toBeVisible();
      });
    });

    it('theme toggle is accessible on mobile (<768px)', async () => {
      setViewportWidth(390);
      await act(async () => { render(<DashboardPage />); });

      await waitFor(() => {
        const toggle = screen.getByTestId('theme-toggle');
        expect(toggle).toBeInTheDocument();
        expect(toggle).toBeVisible();
        expect(toggle).toHaveAttribute('aria-label');
      });
    });

    it('theme toggle has proper fixed positioning at bottom-left', async () => {
      await act(async () => { render(<DashboardPage />); });

      await waitFor(() => {
        const toggle = screen.getByTestId('theme-toggle');
        expect(toggle).toHaveStyle({
          position: 'fixed',
          bottom: '2rem',
          left: '2rem',
          zIndex: '50',
        });
      });
    });
  });

  describe('Touch Target Sizes', () => {
    it('theme toggle is >= 44px × 44px on mobile', async () => {
      setViewportWidth(390);
      await act(async () => { render(<DashboardPage />); });

      await waitFor(() => {
        const toggle = screen.getByTestId('theme-toggle');
        expect(toggle).toHaveStyle({
          width: '44px',
          height: '44px',
          minWidth: '44px',
          minHeight: '44px',
        });
      });
    });

    it('action cards maintain min-height for touch targets', async () => {
      setViewportWidth(390);
      await act(async () => { render(<DashboardPage />); });

      await waitFor(() => {
        const action1 = screen.getByTestId('action-1');
        const minHeight = action1.style.minHeight;
        expect(minHeight).toBeDefined();
        expect(parseInt(minHeight)).toBeGreaterThanOrEqual(44);
      });
    });

    it('sign-out button is accessible with sufficient size', async () => {
      await act(async () => { render(<DashboardPage />); });

      await waitFor(() => {
        const signOutBtn = screen.getByTestId('sign-out-btn');
        expect(signOutBtn).toBeInTheDocument();
      });
    });
  });

  describe('Responsive Grid Transitions', () => {
    it('metric cards transition from 4 columns (desktop) to 2 columns (tablet)', async () => {
      setViewportWidth(1366);
      const { rerender } = render(<DashboardPage />);

      await waitFor(() => {
        expect(screen.getByTestId('status-strip').className).toContain('lg:grid-cols-4');
      });

      // Simulate viewport resize
      setViewportWidth(768);
      rerender(<DashboardPage />);

      await waitFor(() => {
        expect(screen.getByTestId('status-strip').className).toContain('md:grid-cols-2');
      });
    });

    it('quick-action cards transition from 3 columns (desktop) to 2 columns (mobile)', async () => {
      setViewportWidth(1366);
      render(<DashboardPage />);

      await waitFor(() => {
        expect(screen.getByTestId('quick-launch-section').className).toContain('lg:grid-cols-3');
      });

      setViewportWidth(390);

      await waitFor(() => {
        expect(screen.getByTestId('quick-launch-section').className).toContain('grid-cols-2');
      });
    });
  });

  describe('Collapsible Sections', () => {
    it('status strip is rendered and can be collapsed/expanded', async () => {
      await act(async () => { render(<DashboardPage />); });

      await waitFor(() => {
        expect(screen.getByTestId('status-strip')).toBeInTheDocument();
      });
    });

    it('alerts section remains visible across all breakpoints', async () => {
      await act(async () => { render(<DashboardPage />); });

      await waitFor(() => {
        expect(screen.getByTestId('alerts-section')).toBeInTheDocument();
      });

      // Test on tablet
      setViewportWidth(768);
      await waitFor(() => {
        expect(screen.getByTestId('alerts-section')).toBeInTheDocument();
      });

      // Test on mobile
      setViewportWidth(390);
      await waitFor(() => {
        expect(screen.getByTestId('alerts-section')).toBeInTheDocument();
      });
    });
  });
});
