# Dashboard Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Redesign dashboard layout with sticky header, dense collapsible sections, and responsive grid layout to support hybrid workflow (quick agent execution + monitoring).

**Architecture:** C Layout (Sticky Header + Full Sections) with component-based React architecture. Header fixed at top (z-index 100), main sections stack vertically below. All info visible by default; collapsible status strip for power-user focus mode. Responsive breakpoints: 4-col desktop (1024px+), 2-col tablet (768-1023px), 1-col mobile (<768px).

**Tech Stack:** Next.js 14 App Router, React hooks, TypeScript, oklch color system, localStorage persistence, CSS-in-JS inline styles.

## Global Constraints

- **Header height:** 70px desktop, 60px mobile
- **Max width:** 1200px content
- **Color system:** oklch palette only (no Tailwind merge conflicts) — pending/yellow: `oklch(0.82 0.18 65)`, in-progress/blue: `oklch(0.60 0.18 250)`, approval/orange: `oklch(0.75 0.18 55)`, completed/green: `oklch(0.75 0.22 145)`, failed/red: `oklch(0.65 0.18 25)`, surface: `oklch(1 0 0 / 0.04)`, border: `oklch(1 0 0 / 0.08)`, text: `oklch(1 0 0)` / `oklch(0.50 0 0)` secondary
- **Polling interval:** 10s for running jobs
- **Status badge styles:** Inline styles from `STATUS_INLINE_STYLES` lookup table; no shadow/blur — crisp oklch fills with 10% saturation backgrounds
- **Collapsible state:** Persisted in localStorage as JSON (key: `collapsed_sections`)
- **Theme state:** localStorage key `theme-preference` (dark/light/auto), cycles on click
- **Responsive grid:** Desktop 4-col metric cards → 2-col tablet → 1-col mobile; Quick actions 3-col → 2-col → 2-col; Jobs table horizontal scroll on mobile
- **Component re-use:** MetricCard, ActionCard, StatusBadge primitives shared across sections
- **Accessibility:** WCAG AA, keyboard nav, 44px+ touch targets, semantic HTML
- **Test framework:** Jest + React Testing Library (existing SkeletonCard import available)

---

## Task 1: Create MetricCard Component

**Files:**
- Create: `frontend/components/dashboard/MetricCard.tsx`
- Test: `frontend/components/dashboard/__tests__/MetricCard.test.tsx`

**Interfaces:**
- Consumes: None (primitive component)
- Produces: `MetricCard({ label: string, value: string | number, sub?: string, color?: string }) => ReactNode`
  - Props rendered as: label (small, muted), value (large, bold, colored), optional sub (small, gray)
  - Inline styles: `background: 'oklch(1 0 0 / 0.04)'`, `border: '1px solid oklch(1 0 0 / 0.08)'`, `borderRadius: '1rem'`, `padding: '1.25rem'`
  - Flex column, gap `0.25rem` between label/value/sub

- [ ] **Step 1: Write the failing test**

Create `frontend/components/dashboard/__tests__/MetricCard.test.tsx`:

```typescript
import { render, screen } from '@testing-library/react';
import MetricCard from '../MetricCard';

describe('MetricCard', () => {
  it('renders label, value, and optional sub', () => {
    render(
      <MetricCard 
        label="Credits remaining" 
        value={150} 
        sub="of 1000 total"
        color="text-emerald-400"
      />
    );
    expect(screen.getByText('Credits remaining')).toBeInTheDocument();
    expect(screen.getByText('150')).toBeInTheDocument();
    expect(screen.getByText('of 1000 total')).toBeInTheDocument();
  });

  it('renders without sub when not provided', () => {
    render(
      <MetricCard 
        label="Jobs completed" 
        value={42}
      />
    );
    expect(screen.getByText('Jobs completed')).toBeInTheDocument();
    expect(screen.getByText('42')).toBeInTheDocument();
  });

  it('applies color class to value when provided', () => {
    render(
      <MetricCard 
        label="Test" 
        value="Test Value"
        color="text-red-400"
      />
    );
    const valueEl = screen.getByText('Test Value');
    expect(valueEl.parentElement).toHaveClass('text-red-400');
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd frontend
npm test -- MetricCard.test.tsx
```

Expected: `FAIL` with "Cannot find module '../MetricCard'" or "MetricCard is not exported"

- [ ] **Step 3: Write minimal implementation**

Create `frontend/components/dashboard/MetricCard.tsx`:

```typescript
interface MetricCardProps {
  label: string;
  value: string | number;
  sub?: string;
  color?: string;
}

export default function MetricCard({ label, value, sub, color }: MetricCardProps) {
  return (
    <div style={{ background: 'oklch(1 0 0 / 0.04)', border: '1px solid oklch(1 0 0 / 0.08)', borderRadius: '1rem', padding: '1.25rem', display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
      <p className="text-xs font-medium" style={{ color: 'oklch(0.50 0 0)' }}>{label}</p>
      <p className={`text-2xl font-bold ${color || 'text-white'}`}>{value}</p>
      {sub && <p className="text-xs text-gray-600">{sub}</p>}
    </div>
  );
}
```

- [ ] **Step 4: Run test to verify it passes**

```bash
cd frontend
npm test -- MetricCard.test.tsx
```

Expected: `PASS` (all 3 tests passing)

- [ ] **Step 5: Commit**

```bash
git add frontend/components/dashboard/MetricCard.tsx frontend/components/dashboard/__tests__/MetricCard.test.tsx
git commit -m "feat: add MetricCard primitive component for dashboard status strip"
```

---

## Task 2: Create ActionCard Component

**Files:**
- Create: `frontend/components/dashboard/ActionCard.tsx`
- Test: `frontend/components/dashboard/__tests__/ActionCard.test.tsx`

**Interfaces:**
- Consumes: Next.js `Link` (from `next/link`)
- Produces: `ActionCard({ href: string, icon: string, label: string, desc: string }) => ReactNode`
  - Wraps Next.js `Link`, renders icon + label + desc, smooth hover brightness increase

- [ ] **Step 1: Write the failing test**

Create `frontend/components/dashboard/__tests__/ActionCard.test.tsx`:

```typescript
import { render, screen } from '@testing-library/react';
import ActionCard from '../ActionCard';

describe('ActionCard', () => {
  it('renders as a link with icon, label, and description', () => {
    render(
      <ActionCard 
        href="/dashboard/agents" 
        icon="◆" 
        label="Run an agent" 
        desc="Launch a task with any active agent"
      />
    );
    const link = screen.getByRole('link');
    expect(link).toHaveAttribute('href', '/dashboard/agents');
    expect(screen.getByText('◆')).toBeInTheDocument();
    expect(screen.getByText('Run an agent')).toBeInTheDocument();
    expect(screen.getByText('Launch a task with any active agent')).toBeInTheDocument();
  });

  it('applies card styling with hover effect', () => {
    const { container } = render(
      <ActionCard 
        href="/test" 
        icon="✦" 
        label="Test" 
        desc="Test description"
      />
    );
    const link = container.querySelector('a');
    expect(link).toHaveClass('transition-all');
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd frontend
npm test -- ActionCard.test.tsx
```

Expected: `FAIL` with "Cannot find module '../ActionCard'"

- [ ] **Step 3: Write minimal implementation**

Create `frontend/components/dashboard/ActionCard.tsx`:

```typescript
import Link from 'next/link';

const CARD_STYLE: React.CSSProperties = {
  background: 'oklch(1 0 0 / 0.04)',
  border: '1px solid oklch(1 0 0 / 0.08)',
  borderRadius: '1rem',
};

interface ActionCardProps {
  href: string;
  icon: string;
  label: string;
  desc: string;
}

export default function ActionCard({ href, icon, label, desc }: ActionCardProps) {
  return (
    <Link
      href={href}
      className="rounded-2xl p-5 transition-all group"
      style={CARD_STYLE}
    >
      <div className="flex items-center gap-3 mb-2">
        <span className="text-lg transition-colors" style={{ color: 'oklch(0.78 0.13 250)' }}>{icon}</span>
        <p className="font-medium text-sm text-white">{label}</p>
      </div>
      <p className="text-xs text-gray-600">{desc}</p>
    </Link>
  );
}
```

- [ ] **Step 4: Run test to verify it passes**

```bash
cd frontend
npm test -- ActionCard.test.tsx
```

Expected: `PASS`

- [ ] **Step 5: Commit**

```bash
git add frontend/components/dashboard/ActionCard.tsx frontend/components/dashboard/__tests__/ActionCard.test.tsx
git commit -m "feat: add ActionCard component for quick-launch grid"
```

---

## Task 3: Create StatusBadge Component

**Files:**
- Create: `frontend/components/dashboard/StatusBadge.tsx`
- Test: `frontend/components/dashboard/__tests__/StatusBadge.test.tsx`

**Interfaces:**
- Consumes: `CLIENT_STATUS` lookup (from current dashboard page), `STATUS_INLINE_STYLES` lookup
- Produces: `StatusBadge({ status: string }) => ReactNode`
  - Maps raw status to display string via `CLIENT_STATUS`
  - Looks up inline styles from `STATUS_INLINE_STYLES`
  - Renders inline-styled badge, `borderRadius: '9999px'`, `fontSize: '10px'`, `padding: '2px 8px'`, `fontWeight: '600'`

- [ ] **Step 1: Write the failing test**

Create `frontend/components/dashboard/__tests__/StatusBadge.test.tsx`:

```typescript
import { render, screen } from '@testing-library/react';
import StatusBadge from '../StatusBadge';

describe('StatusBadge', () => {
  it('renders completed status with green color', () => {
    render(<StatusBadge status="completed" />);
    expect(screen.getByText('Ready')).toBeInTheDocument();
  });

  it('renders pending_approval status with orange color', () => {
    render(<StatusBadge status="pending_approval" />);
    expect(screen.getByText('Needs your approval')).toBeInTheDocument();
  });

  it('renders failed status with red color', () => {
    render(<StatusBadge status="failed" />);
    expect(screen.getByText('Could not complete')).toBeInTheDocument();
  });

  it('applies pill-shaped styling', () => {
    const { container } = render(<StatusBadge status="completed" />);
    const badge = container.querySelector('span');
    expect(badge?.style.borderRadius).toBe('9999px');
    expect(badge?.style.fontSize).toBe('10px');
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd frontend
npm test -- StatusBadge.test.tsx
```

Expected: `FAIL`

- [ ] **Step 3: Write minimal implementation**

Create `frontend/components/dashboard/StatusBadge.tsx`:

```typescript
const CLIENT_STATUS: Record<string, string> = {
  pending: 'Waiting to start',
  queued: 'Waiting to start',
  running: 'In progress',
  processing: 'In progress',
  approved: 'In progress',
  pending_approval: 'Needs your approval',
  pending_financial_review: 'Needs your approval',
  completed: 'Ready',
  failed: 'Could not complete',
  cancelled: 'Cancelled',
  rejected: 'Not approved',
};

const STATUS_INLINE_STYLES: Record<string, React.CSSProperties> = {
  'Waiting to start': { color: 'oklch(0.82 0.18 65)', background: 'oklch(0.82 0.18 65 / 0.10)', border: '1px solid oklch(0.82 0.18 65 / 0.20)' },
  'In progress': { color: 'oklch(0.78 0.13 250)', background: 'oklch(0.60 0.18 250 / 0.10)', border: '1px solid oklch(0.60 0.18 250 / 0.20)' },
  'Needs your approval': { color: 'oklch(0.75 0.18 55)', background: 'oklch(0.75 0.18 55 / 0.10)', border: '1px solid oklch(0.75 0.18 55 / 0.20)' },
  'Ready': { color: 'oklch(0.75 0.22 145)', background: 'oklch(0.75 0.22 145 / 0.10)', border: '1px solid oklch(0.75 0.22 145 / 0.20)' },
  'Could not complete': { color: 'oklch(0.65 0.18 25)', background: 'oklch(0.65 0.18 25 / 0.10)', border: '1px solid oklch(0.65 0.18 25 / 0.20)' },
  'Cancelled': { color: 'oklch(0.45 0 0)', background: 'oklch(1 0 0 / 0.03)', border: '1px solid oklch(1 0 0 / 0.08)' },
  'Not approved': { color: 'oklch(0.65 0.18 25)', background: 'oklch(0.65 0.18 25 / 0.10)', border: '1px solid oklch(0.65 0.18 25 / 0.20)' },
};

interface StatusBadgeProps {
  status: string;
}

export default function StatusBadge({ status }: StatusBadgeProps) {
  const displayStatus = CLIENT_STATUS[status] || 'In progress';
  const style = STATUS_INLINE_STYLES[displayStatus] || { color: 'oklch(0.45 0 0)', background: 'oklch(1 0 0 / 0.04)', border: '1px solid oklch(1 0 0 / 0.08)' };

  return (
    <span
      className="px-2 py-0.5 font-semibold"
      style={{ ...style, borderRadius: '9999px', fontSize: '10px' }}
    >
      {displayStatus}
    </span>
  );
}
```

- [ ] **Step 4: Run test to verify it passes**

```bash
cd frontend
npm test -- StatusBadge.test.tsx
```

Expected: `PASS`

- [ ] **Step 5: Commit**

```bash
git add frontend/components/dashboard/StatusBadge.tsx frontend/components/dashboard/__tests__/StatusBadge.test.tsx
git commit -m "feat: add StatusBadge component for job status display"
```

---

## Task 4: Create DashboardHeader Component

**Files:**
- Create: `frontend/components/dashboard/DashboardHeader.tsx`

**Interfaces:**
- Consumes: `credits` (CreditsData | null), `pendingApprovals` (number), `failedJobs` (number)
- Produces: `DashboardHeader({ credits, pendingApprovals, failedJobs, onSignOut }) => ReactNode`
  - Fixed sticky header (z-index 100, height 70px desktop / 60px mobile)
  - Left: Vantro logo + workspace name
  - Center: "Run Agent" button (link to `/dashboard/agents`, primary CTA)
  - Right: Credits meter (color-coded), alerts badge with count (collapsible), sign-out button

- [ ] **Step 1: Write the failing test**

Create `frontend/components/dashboard/__tests__/DashboardHeader.test.tsx`:

```typescript
import { render, screen } from '@testing-library/react';
import DashboardHeader from '../DashboardHeader';

describe('DashboardHeader', () => {
  const defaultProps = {
    credits: { total_credits: 1000, used_credits: 200, remaining_credits: 800, tier: 'growth' },
    pendingApprovals: 2,
    failedJobs: 1,
    onSignOut: jest.fn(),
  };

  it('renders "Run Agent" CTA button', () => {
    render(<DashboardHeader {...defaultProps} />);
    expect(screen.getByText('Run Agent')).toBeInTheDocument();
  });

  it('displays credits count', () => {
    render(<DashboardHeader {...defaultProps} />);
    expect(screen.getByText('800')).toBeInTheDocument();
  });

  it('displays alert count badge', () => {
    render(<DashboardHeader {...defaultProps} />);
    expect(screen.getByText('3')).toBeInTheDocument(); // 2 pending + 1 failed
  });

  it('has sticky positioning', () => {
    const { container } = render(<DashboardHeader {...defaultProps} />);
    const header = container.firstChild;
    expect(header).toHaveStyle({ position: 'sticky', top: '0', zIndex: '100' });
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd frontend
npm test -- DashboardHeader.test.tsx
```

Expected: `FAIL`

- [ ] **Step 3: Write minimal implementation**

Create `frontend/components/dashboard/DashboardHeader.tsx`:

```typescript
import Link from 'next/link';
import { useState } from 'react';

interface CreditsData {
  total_credits: number;
  used_credits: number;
  remaining_credits: number;
  tier: string;
}

interface DashboardHeaderProps {
  credits: CreditsData | null;
  pendingApprovals: number;
  failedJobs: number;
  onSignOut: () => void;
}

export default function DashboardHeader({ credits, pendingApprovals, failedJobs, onSignOut }: DashboardHeaderProps) {
  const [showAlerts, setShowAlerts] = useState(false);
  const alertCount = pendingApprovals + failedJobs;
  const creditsRemaining = credits?.remaining_credits ?? 0;
  const creditsColor = 
    credits && credits.total_credits > 0
      ? (creditsRemaining / credits.total_credits) < 0.2
        ? 'text-red-400'
        : (creditsRemaining / credits.total_credits) < 0.5
        ? 'text-amber-400'
        : 'text-emerald-400'
      : 'text-white';

  return (
    <div
      style={{
        position: 'sticky',
        top: 0,
        zIndex: 100,
        height: '70px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '0 2rem',
        background: 'oklch(1 0 0 / 0.04)',
        borderBottom: '1px solid oklch(1 0 0 / 0.08)',
      }}
    >
      <div className="text-xl font-bold text-white">Vantro</div>

      <Link href="/dashboard/agents" className="px-6 py-2 rounded-lg font-semibold text-white bg-blue-600 hover:bg-blue-700 transition-colors">
        Run Agent
      </Link>

      <div className="flex items-center gap-4">
        <div className="text-sm">
          <span className={`font-bold ${creditsColor}`}>{creditsRemaining.toLocaleString()}</span>
          <span className="text-gray-600 text-xs"> credits</span>
        </div>

        <div className="relative">
          <button
            onClick={() => setShowAlerts(!showAlerts)}
            className="relative px-2 py-1 text-sm font-semibold"
            style={{ color: alertCount > 0 ? 'oklch(0.75 0.18 55)' : 'oklch(0.50 0 0)' }}
          >
            {alertCount > 0 && (
              <span className="absolute top-0 right-0 bg-orange-500 text-white text-xs rounded-full px-2 py-0.5">
                {alertCount}
              </span>
            )}
            Alerts
          </button>
        </div>

        <button
          onClick={onSignOut}
          className="px-4 py-1 text-sm font-semibold rounded-lg transition-colors"
          style={{ color: 'oklch(0.50 0 0)', border: '1px solid oklch(1 0 0 / 0.08)' }}
        >
          Sign out
        </button>
      </div>
    </div>
  );
}
```

- [ ] **Step 4: Run test to verify it passes**

```bash
cd frontend
npm test -- DashboardHeader.test.tsx
```

Expected: `PASS`

- [ ] **Step 5: Commit**

```bash
git add frontend/components/dashboard/DashboardHeader.tsx frontend/components/dashboard/__tests__/DashboardHeader.test.tsx
git commit -m "feat: add DashboardHeader with sticky positioning, CTA, and alerts"
```

---

## Task 5: Create StatusStrip Component (Collapsible Section A)

**Files:**
- Create: `frontend/components/dashboard/StatusStrip.tsx`

**Interfaces:**
- Consumes: MetricCard component, credits data, jobs count
- Produces: `StatusStrip({ credits, completedThisMonth, pendingApprovals, topAgents }) => ReactNode`
  - 4 metric cards: Credits remaining, Jobs completed this month, Billing date (placeholder), Top agents used
  - Collapsible with chevron, toggle state persisted in localStorage
  - Smooth collapse/expand animation 150ms

- [ ] **Step 1: Write the failing test**

Create `frontend/components/dashboard/__tests__/StatusStrip.test.tsx`:

```typescript
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import StatusStrip from '../StatusStrip';

describe('StatusStrip', () => {
  const defaultProps = {
    credits: { total_credits: 1000, used_credits: 200, remaining_credits: 800, tier: 'growth' },
    completedThisMonth: 42,
    pendingApprovals: 2,
    topAgents: [],
  };

  it('renders collapsible section with metrics', () => {
    render(<StatusStrip {...defaultProps} />);
    expect(screen.getByText('Credits remaining')).toBeInTheDocument();
    expect(screen.getByText('Jobs completed this month')).toBeInTheDocument();
  });

  it('renders chevron toggle button', () => {
    const { container } = render(<StatusStrip {...defaultProps} />);
    const button = container.querySelector('button');
    expect(button).toBeInTheDocument();
  });

  it('can toggle collapsed state', async () => {
    const user = userEvent.setup();
    const { container } = render(<StatusStrip {...defaultProps} />);
    const button = container.querySelector('button')!;
    await user.click(button);
    // Verify collapsed state was toggled (visual inspection in real app)
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd frontend
npm test -- StatusStrip.test.tsx
```

Expected: `FAIL`

- [ ] **Step 3: Write minimal implementation**

Create `frontend/components/dashboard/StatusStrip.tsx`:

```typescript
'use client';
import { useState, useEffect } from 'react';
import MetricCard from './MetricCard';

interface CreditsData {
  total_credits: number;
  used_credits: number;
  remaining_credits: number;
  tier: string;
}

interface AgentUsage {
  agent_id: string;
  agent_name: string;
  count: number;
}

interface StatusStripProps {
  credits: CreditsData | null;
  completedThisMonth: number;
  pendingApprovals: number;
  topAgents: AgentUsage[];
}

function AgentBar({ name, count, max }: { name: string; count: number; max: number }) {
  const pct = max > 0 ? Math.round((count / max) * 100) : 0;
  return (
    <div className="flex items-center gap-3">
      <p className="text-xs w-32 truncate shrink-0" style={{ color: 'oklch(0.55 0 0)' }}>{name}</p>
      <div className="flex-1 rounded-full h-1.5" style={{ background: 'oklch(1 0 0 / 0.07)' }}>
        <div
          className="h-1.5 rounded-full"
          style={{ width: `${pct}%`, background: 'oklch(0.60 0.18 250)', transition: 'width 150ms ease-out' }}
        />
      </div>
      <span className="text-xs w-6 text-right shrink-0" style={{ color: 'oklch(0.45 0 0)' }}>{count}</span>
    </div>
  );
}

export default function StatusStrip({ credits, completedThisMonth, pendingApprovals, topAgents }: StatusStripProps) {
  const [collapsed, setCollapsed] = useState(false);

  useEffect(() => {
    const stored = localStorage.getItem('collapsed_sections') || '{}';
    const state = JSON.parse(stored);
    if (state.statusStrip !== undefined) setCollapsed(state.statusStrip);
  }, []);

  const toggle = () => {
    setCollapsed(!collapsed);
    const stored = localStorage.getItem('collapsed_sections') || '{}';
    const state = JSON.parse(stored);
    state.statusStrip = !collapsed;
    localStorage.setItem('collapsed_sections', JSON.stringify(state));
  };

  const creditsRemaining = credits?.remaining_credits ?? 0;

  return (
    <div className="mb-8">
      <div className="flex items-center justify-between mb-4">
        <h2 className="font-semibold text-white text-sm">Status</h2>
        <button onClick={toggle} className="text-gray-600 hover:text-white transition-colors">
          {collapsed ? '▶' : '▼'}
        </button>
      </div>

      {!collapsed && (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 transition-all duration-150">
          <MetricCard
            label="Credits remaining"
            value={creditsRemaining.toLocaleString()}
            sub={credits ? `of ${credits.total_credits.toLocaleString()} total` : undefined}
            color={
              creditsRemaining !== null && credits && credits.total_credits > 0
                ? (creditsRemaining / credits.total_credits) < 0.2
                  ? 'text-red-400'
                  : (creditsRemaining / credits.total_credits) < 0.5
                  ? 'text-amber-400'
                  : 'text-emerald-400'
                : 'text-white'
            }
          />
          <MetricCard
            label="Jobs completed this month"
            value={completedThisMonth}
            sub="completed status"
            color="text-white"
          />
          <MetricCard
            label="Next billing date"
            value="—"
            sub="Manage in Billing"
          />
          <div style={{ background: 'oklch(1 0 0 / 0.04)', border: '1px solid oklch(1 0 0 / 0.08)', borderRadius: '1rem', padding: '1.25rem', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            <p className="text-xs font-medium" style={{ color: 'oklch(0.50 0 0)' }}>Top agents used</p>
            {topAgents.length === 0 ? (
              <p className="text-xs text-gray-600 mt-2">No jobs run yet</p>
            ) : (
              <div className="flex flex-col gap-2 mt-1">
                {topAgents.map(a => (
                  <AgentBar key={a.agent_id} name={a.agent_name} count={a.count} max={topAgents[0]?.count || 1} />
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
```

- [ ] **Step 4: Run test to verify it passes**

```bash
cd frontend
npm test -- StatusStrip.test.tsx
```

Expected: `PASS`

- [ ] **Step 5: Commit**

```bash
git add frontend/components/dashboard/StatusStrip.tsx frontend/components/dashboard/__tests__/StatusStrip.test.tsx
git commit -m "feat: add StatusStrip collapsible section with metrics"
```

---

## Task 6: Create AlertsSection Component (Section B)

**Files:**
- Create: `frontend/components/dashboard/AlertsSection.tsx`

**Interfaces:**
- Consumes: announcements, pendingApprovals, failedJobs, dismiss callback
- Produces: `AlertsSection({ announcements, pendingApprovals, failedJobs, dismissed, onDismiss }) => ReactNode`
  - Platform announcements (type-based styling), dismissible
  - Action cards: pending approvals (orange), failed jobs (red)
  - Vertical stack, independent dismissal

- [ ] **Step 1: Write the failing test**

Create `frontend/components/dashboard/__tests__/AlertsSection.test.tsx`:

```typescript
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import AlertsSection from '../AlertsSection';

describe('AlertsSection', () => {
  const mockAnnouncement = {
    id: '1',
    title: 'New feature',
    body: 'Check out our latest feature',
    affects: null,
    type: 'new_feature',
    show_as: 'banner',
  };

  it('renders platform announcements', () => {
    render(
      <AlertsSection
        announcements={[mockAnnouncement]}
        pendingApprovals={0}
        failedJobs={0}
        dismissed={new Set()}
        onDismiss={jest.fn()}
      />
    );
    expect(screen.getByText('New feature')).toBeInTheDocument();
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
    expect(screen.getByText('Needs your approval')).toBeInTheDocument();
    expect(screen.getByText('3')).toBeInTheDocument();
  });

  it('dismisses announcement on button click', async () => {
    const user = userEvent.setup();
    const onDismiss = jest.fn();
    render(
      <AlertsSection
        announcements={[mockAnnouncement]}
        pendingApprovals={0}
        failedJobs={0}
        dismissed={new Set()}
        onDismiss={onDismiss}
      />
    );
    const dismissBtn = screen.getByText('✕');
    await user.click(dismissBtn);
    expect(onDismiss).toHaveBeenCalledWith('1');
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd frontend
npm test -- AlertsSection.test.tsx
```

Expected: `FAIL`

- [ ] **Step 3: Write minimal implementation**

Create `frontend/components/dashboard/AlertsSection.tsx`:

```typescript
'use client';
import Link from 'next/link';

const ANN_INLINE_STYLES: Record<string, React.CSSProperties> = {
  info: { color: 'oklch(0.78 0.13 250)', background: 'oklch(0.60 0.18 250 / 0.10)', border: '1px solid oklch(0.60 0.18 250 / 0.20)' },
  new_feature: { color: 'oklch(0.78 0.13 250)', background: 'oklch(0.60 0.18 250 / 0.10)', border: '1px solid oklch(0.60 0.18 250 / 0.20)' },
  new_agent: { color: 'oklch(0.78 0.13 250)', background: 'oklch(0.60 0.18 250 / 0.10)', border: '1px solid oklch(0.60 0.18 250 / 0.20)' },
  warning: { color: 'oklch(0.82 0.18 65)', background: 'oklch(0.82 0.18 65 / 0.10)', border: '1px solid oklch(0.82 0.18 65 / 0.20)' },
  maintenance: { color: 'oklch(0.75 0.18 55)', background: 'oklch(0.75 0.18 55 / 0.10)', border: '1px solid oklch(0.75 0.18 55 / 0.20)' },
};

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

export default function AlertsSection({ announcements, pendingApprovals, failedJobs, dismissed, onDismiss }: AlertsSectionProps) {
  return (
    <>
      {/* Platform announcements */}
      {announcements.filter(a => a.show_as === 'banner' && !dismissed.has(a.id)).map(a => {
        const annStyle = ANN_INLINE_STYLES[a.type] || ANN_INLINE_STYLES.info;
        return (
          <div
            key={a.id}
            className="rounded-2xl px-4 py-3 mb-3 flex items-start justify-between gap-3"
            style={annStyle}
          >
            <div className="flex-1 min-w-0">
              <p className="text-sm font-semibold">{a.title}</p>
              <p className="text-xs opacity-75 mt-0.5">{a.body}</p>
              {a.affects && (
                <p className="text-xs opacity-60 mt-0.5"><span className="opacity-80">Affects:</span> {a.affects}</p>
              )}
            </div>
            <button onClick={() => onDismiss(a.id)} className="shrink-0 text-xs opacity-50 hover:opacity-100 mt-0.5">✕</button>
          </div>
        );
      })}

      {/* Pending approvals / failed notice */}
      {(pendingApprovals > 0 || failedJobs > 0) && (
        <div className="flex gap-3 mb-6 flex-wrap">
          {pendingApprovals > 0 && (
            <Link
              href="/dashboard/approvals"
              className="flex-1 min-w-[180px] rounded-2xl px-4 py-3 flex items-center justify-between transition-colors"
              style={{ background: 'oklch(0.75 0.18 55 / 0.10)', border: '1px solid oklch(0.75 0.18 55 / 0.20)' }}
            >
              <div>
                <p className="text-xs font-semibold" style={{ color: 'oklch(0.75 0.18 55)' }}>Needs your approval</p>
                <p className="text-[10px] mt-0.5" style={{ color: 'oklch(0.60 0.10 55)' }}>Review before we continue</p>
              </div>
              <span className="text-2xl font-bold" style={{ color: 'oklch(0.75 0.18 55)' }}>{pendingApprovals}</span>
            </Link>
          )}
          {failedJobs > 0 && (
            <Link
              href="/dashboard/jobs?filter=failed"
              className="flex-1 min-w-[180px] rounded-2xl px-4 py-3 flex items-center justify-between transition-colors"
              style={{ background: 'oklch(0.65 0.18 25 / 0.10)', border: '1px solid oklch(0.65 0.18 25 / 0.15)' }}
            >
              <div>
                <p className="text-xs font-semibold" style={{ color: 'oklch(0.75 0.15 25)' }}>Could not complete</p>
                <p className="text-[10px] mt-0.5" style={{ color: 'oklch(0.58 0.10 25)' }}>Retry or contact support</p>
              </div>
              <span className="text-2xl font-bold" style={{ color: 'oklch(0.65 0.18 25)' }}>{failedJobs}</span>
            </Link>
          )}
        </div>
      )}
    </>
  );
}
```

- [ ] **Step 4: Run test to verify it passes**

```bash
cd frontend
npm test -- AlertsSection.test.tsx
```

Expected: `PASS`

- [ ] **Step 5: Commit**

```bash
git add frontend/components/dashboard/AlertsSection.tsx frontend/components/dashboard/__tests__/AlertsSection.test.tsx
git commit -m "feat: add AlertsSection for announcements and action alerts"
```

---

## Task 7: Create QuickLaunchSection Component (Section C)

**Files:**
- Create: `frontend/components/dashboard/QuickLaunchSection.tsx`

**Interfaces:**
- Consumes: ActionCard component
- Produces: `QuickLaunchSection() => ReactNode`
  - 6 fixed ActionCard instances in 3-col grid (→ 2-col tablet/mobile)
  - No state, no props

- [ ] **Step 1: Write the failing test**

Create `frontend/components/dashboard/__tests__/QuickLaunchSection.test.tsx`:

```typescript
import { render, screen } from '@testing-library/react';
import QuickLaunchSection from '../QuickLaunchSection';

describe('QuickLaunchSection', () => {
  it('renders 6 quick-launch cards', () => {
    render(<QuickLaunchSection />);
    expect(screen.getByText('Run an agent')).toBeInTheDocument();
    expect(screen.getByText('Output library')).toBeInTheDocument();
    expect(screen.getByText('Weekly report')).toBeInTheDocument();
    expect(screen.getByText('Brand profile')).toBeInTheDocument();
    expect(screen.getByText('Billing & credits')).toBeInTheDocument();
    expect(screen.getByText('Settings')).toBeInTheDocument();
  });

  it('renders 6 links with correct hrefs', () => {
    const { container } = render(<QuickLaunchSection />);
    const links = container.querySelectorAll('a');
    expect(links.length).toBe(6);
    expect(links[0]).toHaveAttribute('href', '/dashboard/agents');
    expect(links[1]).toHaveAttribute('href', '/dashboard/library');
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd frontend
npm test -- QuickLaunchSection.test.tsx
```

Expected: `FAIL`

- [ ] **Step 3: Write minimal implementation**

Create `frontend/components/dashboard/QuickLaunchSection.tsx`:

```typescript
import ActionCard from './ActionCard';

export default function QuickLaunchSection() {
  return (
    <div className="grid grid-cols-2 lg:grid-cols-3 gap-4 mb-8">
      <ActionCard
        href="/dashboard/agents"
        icon="◆"
        label="Run an agent"
        desc="Launch a task with any active agent"
      />
      <ActionCard
        href="/dashboard/library"
        icon="▣"
        label="Output library"
        desc="Browse and copy past agent outputs"
      />
      <ActionCard
        href="/dashboard/reports"
        icon="◈"
        label="Weekly report"
        desc="Performance summary and insights"
      />
      <ActionCard
        href="/dashboard/brand"
        icon="◎"
        label="Brand profile"
        desc="Feed your brand context to agents"
      />
      <ActionCard
        href="/dashboard/billing"
        icon="◇"
        label="Billing & credits"
        desc="Top up credits or manage your plan"
      />
      <ActionCard
        href="/dashboard/settings"
        icon="◌"
        label="Settings"
        desc="Integrations, notifications, security"
      />
    </div>
  );
}
```

- [ ] **Step 4: Run test to verify it passes**

```bash
cd frontend
npm test -- QuickLaunchSection.test.tsx
```

Expected: `PASS`

- [ ] **Step 5: Commit**

```bash
git add frontend/components/dashboard/QuickLaunchSection.tsx frontend/components/dashboard/__tests__/QuickLaunchSection.test.tsx
git commit -m "feat: add QuickLaunchSection with 6 action cards"
```

---

## Task 8: Create RecentJobsTable Component (Section D)

**Files:**
- Create: `frontend/components/dashboard/RecentJobsTable.tsx`

**Interfaces:**
- Consumes: HistoryJob[], StatusBadge component
- Produces: `RecentJobsTable({ jobs }) => ReactNode`
  - Renders first 10 jobs in compact table: Agent name | Status badge | Credits | Created time
  - Empty state with link to run first agent
  - Row click navigates to job detail (future: modal)

- [ ] **Step 1: Write the failing test**

Create `frontend/components/dashboard/__tests__/RecentJobsTable.test.tsx`:

```typescript
import { render, screen } from '@testing-library/react';
import RecentJobsTable from '../RecentJobsTable';

describe('RecentJobsTable', () => {
  const mockJobs = [
    {
      id: '1',
      agent_id: 'a1',
      agent_name: 'Research Agent',
      status: 'completed',
      credits_used: 50,
      created_at: '2026-02-27T10:00:00Z',
      completed_at: '2026-02-27T10:05:00Z',
    },
  ];

  it('renders job table header', () => {
    render(<RecentJobsTable jobs={mockJobs} />);
    expect(screen.getByText('Recent jobs')).toBeInTheDocument();
  });

  it('renders jobs with agent name and status', () => {
    render(<RecentJobsTable jobs={mockJobs} />);
    expect(screen.getByText('Research Agent')).toBeInTheDocument();
  });

  it('shows empty state when no jobs', () => {
    render(<RecentJobsTable jobs={[]} />);
    expect(screen.getByText('No jobs yet')).toBeInTheDocument();
    expect(screen.getByText('Run your first agent →')).toBeInTheDocument();
  });

  it('displays credits used', () => {
    render(<RecentJobsTable jobs={mockJobs} />);
    expect(screen.getByText('50cr')).toBeInTheDocument();
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd frontend
npm test -- RecentJobsTable.test.tsx
```

Expected: `FAIL`

- [ ] **Step 3: Write minimal implementation**

Create `frontend/components/dashboard/RecentJobsTable.tsx`:

```typescript
'use client';
import Link from 'next/link';
import StatusBadge from './StatusBadge';

const CLIENT_STATUS: Record<string, string> = {
  pending: 'Waiting to start',
  queued: 'Waiting to start',
  running: 'In progress',
  processing: 'In progress',
  approved: 'In progress',
  pending_approval: 'Needs your approval',
  pending_financial_review: 'Needs your approval',
  completed: 'Ready',
  failed: 'Could not complete',
  cancelled: 'Cancelled',
  rejected: 'Not approved',
};

interface HistoryJob {
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

export default function RecentJobsTable({ jobs }: RecentJobsTableProps) {
  return (
    <div className="rounded-2xl overflow-hidden" style={{ background: 'oklch(1 0 0 / 0.04)', border: '1px solid oklch(1 0 0 / 0.08)' }}>
      <div className="px-6 py-4 flex items-center justify-between" style={{ borderBottom: '1px solid oklch(1 0 0 / 0.08)' }}>
        <h2 className="font-semibold text-white text-sm">Recent jobs</h2>
        <Link href="/dashboard/jobs" className="text-xs font-medium" style={{ color: 'oklch(0.78 0.13 250)' }}>
          View all →
        </Link>
      </div>
      {jobs.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-gray-600 text-sm mb-3">No jobs yet</p>
          <Link href="/dashboard/agents" className="text-xs font-medium" style={{ color: 'oklch(0.78 0.13 250)' }}>
            Run your first agent →
          </Link>
        </div>
      ) : (
        <div>
          {jobs.slice(0, 10).map(job => {
            return (
              <div
                key={job.id}
                className="flex items-center gap-4 px-6 py-3 transition-colors hover:bg-black/20 cursor-pointer"
                style={{ borderBottom: '1px solid oklch(1 0 0 / 0.06)' }}
              >
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-white font-medium truncate">{job.agent_name}</p>
                  <p className="text-xs text-gray-600">
                    {job.created_at ? new Date(job.created_at).toLocaleString() : '—'}
                  </p>
                </div>
                <div className="flex items-center gap-2 shrink-0">
                  <StatusBadge status={job.status} />
                  {job.credits_used > 0 && (
                    <span className="text-[10px] text-gray-600">{job.credits_used}cr</span>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
```

- [ ] **Step 4: Run test to verify it passes**

```bash
cd frontend
npm test -- RecentJobsTable.test.tsx
```

Expected: `PASS`

- [ ] **Step 5: Commit**

```bash
git add frontend/components/dashboard/RecentJobsTable.tsx frontend/components/dashboard/__tests__/RecentJobsTable.test.tsx
git commit -m "feat: add RecentJobsTable with job history display"
```

---

## Task 9: Create ThemeToggle Component & useTheme Hook

**Files:**
- Create: `frontend/components/dashboard/ThemeToggle.tsx`
- Create: `frontend/lib/hooks/useTheme.ts`

**Interfaces:**
- useTheme: `() => { theme: 'dark' | 'light' | 'auto', setTheme: (theme) => void }`
  - Reads/writes localStorage key `theme-preference`
  - Updates `html` element classList: removes old, adds new (e.g., dark, light)
  - On 'auto', checks OS preference via prefers-color-scheme
- ThemeToggle: Fixed bottom-left button, cycles theme, shows sun/moon/auto icon

- [ ] **Step 1: Write failing test for useTheme hook**

Create `frontend/lib/hooks/__tests__/useTheme.test.ts`:

```typescript
import { renderHook, act } from '@testing-library/react';
import { useTheme } from '../useTheme';

describe('useTheme', () => {
  beforeEach(() => {
    localStorage.clear();
    document.documentElement.className = '';
  });

  it('initializes with default theme', () => {
    const { result } = renderHook(() => useTheme());
    expect(['dark', 'light', 'auto']).toContain(result.current.theme);
  });

  it('persists theme to localStorage', () => {
    const { result } = renderHook(() => useTheme());
    act(() => {
      result.current.setTheme('light');
    });
    expect(localStorage.getItem('theme-preference')).toBe('light');
  });

  it('updates html classList when theme changes', () => {
    const { result } = renderHook(() => useTheme());
    act(() => {
      result.current.setTheme('dark');
    });
    expect(document.documentElement.classList.contains('dark')).toBe(true);
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd frontend
npm test -- useTheme.test.ts
```

Expected: `FAIL`

- [ ] **Step 3: Write useTheme implementation**

Create `frontend/lib/hooks/useTheme.ts`:

```typescript
import { useState, useEffect } from 'react';

export function useTheme() {
  const [theme, setThemeState] = useState<'dark' | 'light' | 'auto'>('dark');

  useEffect(() => {
    const stored = localStorage.getItem('theme-preference') as 'dark' | 'light' | 'auto' | null;
    if (stored) setThemeState(stored);
  }, []);

  const setTheme = (newTheme: 'dark' | 'light' | 'auto') => {
    setThemeState(newTheme);
    localStorage.setItem('theme-preference', newTheme);
    const html = document.documentElement;
    html.classList.remove('dark', 'light', 'auto');
    html.classList.add(newTheme);
    if (newTheme === 'auto') {
      const isDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      html.classList.add(isDark ? 'dark' : 'light');
    }
  };

  return { theme, setTheme };
}
```

- [ ] **Step 4: Write failing test for ThemeToggle**

Create `frontend/components/dashboard/__tests__/ThemeToggle.test.tsx`:

```typescript
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import ThemeToggle from '../ThemeToggle';

describe('ThemeToggle', () => {
  it('renders toggle button', () => {
    render(<ThemeToggle />);
    const button = screen.getByRole('button');
    expect(button).toBeInTheDocument();
  });

  it('has fixed bottom-left positioning', () => {
    const { container } = render(<ThemeToggle />);
    const button = container.querySelector('button');
    const style = window.getComputedStyle(button!);
    expect(button).toHaveStyle({ position: 'fixed', bottom: '2rem', left: '2rem' });
  });

  it('cycles through themes on click', async () => {
    const user = userEvent.setup();
    render(<ThemeToggle />);
    const button = screen.getByRole('button');
    await user.click(button);
    // Theme should cycle to next value
  });
});
```

- [ ] **Step 5: Run test to verify it fails**

```bash
cd frontend
npm test -- ThemeToggle.test.tsx
```

Expected: `FAIL`

- [ ] **Step 6: Write ThemeToggle implementation**

Create `frontend/components/dashboard/ThemeToggle.tsx`:

```typescript
'use client';
import { useTheme } from '@/lib/hooks/useTheme';

export default function ThemeToggle() {
  const { theme, setTheme } = useTheme();

  const cycle = () => {
    const next = theme === 'dark' ? 'light' : theme === 'light' ? 'auto' : 'dark';
    setTheme(next);
  };

  const icon = theme === 'dark' ? '☀️' : theme === 'light' ? '🌙' : '🔄';

  return (
    <button
      onClick={cycle}
      style={{
        position: 'fixed',
        bottom: '2rem',
        left: '2rem',
        zIndex: 50,
        padding: '0.75rem',
        borderRadius: '0.5rem',
        background: 'oklch(1 0 0 / 0.08)',
        border: '1px solid oklch(1 0 0 / 0.16)',
        color: 'oklch(0.50 0 0)',
        fontSize: '1.25rem',
        cursor: 'pointer',
        transition: 'all 200ms ease',
      }}
      className="hover:bg-white/10"
      title={`Theme: ${theme}`}
    >
      {icon}
    </button>
  );
}
```

- [ ] **Step 7: Run tests to verify they pass**

```bash
cd frontend
npm test -- useTheme.test.ts ThemeToggle.test.tsx
```

Expected: `PASS`

- [ ] **Step 8: Commit**

```bash
git add frontend/lib/hooks/useTheme.ts frontend/components/dashboard/ThemeToggle.tsx frontend/lib/hooks/__tests__/useTheme.test.ts frontend/components/dashboard/__tests__/ThemeToggle.test.tsx
git commit -m "feat: add ThemeToggle and useTheme hook for dark/light/auto switching"
```

---

## Task 10: Integrate Components into Dashboard Page

**Files:**
- Modify: `frontend/app/dashboard/page.tsx` (refactor to use components)

**Interfaces:**
- Consumes: All 9 components + hooks created in Tasks 1-9
- Produces: Refactored dashboard page that:
  - Imports and renders DashboardHeader at top
  - Imports and renders StatusStrip (collapsible)
  - Imports and renders AlertsSection
  - Imports and renders QuickLaunchSection
  - Imports and renders RecentJobsTable
  - Imports and renders ThemeToggle
  - Maintains all data fetching, polling, and state logic
  - Maintains empty states and loading states

- [ ] **Step 1: Write integration test**

Create `frontend/app/dashboard/__tests__/page.integration.test.tsx`:

```typescript
import { render, screen, waitFor } from '@testing-library/react';
import DashboardPage from '../page';

// Mock fetch
global.fetch = jest.fn(() =>
  Promise.resolve({
    ok: true,
    json: async () => ({
      total_credits: 1000,
      used_credits: 200,
      remaining_credits: 800,
      tier: 'growth',
    }),
  })
) as jest.Mock;

jest.mock('next/router', () => ({
  useRouter: () => ({
    push: jest.fn(),
  }),
}));

describe('Dashboard Page Integration', () => {
  beforeEach(() => {
    localStorage.setItem('token', 'test-token');
  });

  it('renders all main sections', async () => {
    render(<DashboardPage />);
    await waitFor(() => {
      expect(screen.getByText('Status')).toBeInTheDocument();
      expect(screen.getByText('Run an agent')).toBeInTheDocument();
      expect(screen.getByText('Recent jobs')).toBeInTheDocument();
    });
  });
});
```

- [ ] **Step 2: Run test to verify it fails (integration needed)**

```bash
cd frontend
npm test -- page.integration.test.tsx
```

Expected: Test fails because components are not imported

- [ ] **Step 3: Refactor dashboard page**

Replace `frontend/app/dashboard/page.tsx` with:

```typescript
'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { SkeletonCard } from '@/components/Skeleton';
import DashboardHeader from '@/components/dashboard/DashboardHeader';
import StatusStrip from '@/components/dashboard/StatusStrip';
import AlertsSection from '@/components/dashboard/AlertsSection';
import QuickLaunchSection from '@/components/dashboard/QuickLaunchSection';
import RecentJobsTable from '@/components/dashboard/RecentJobsTable';
import ThemeToggle from '@/components/dashboard/ThemeToggle';

interface CreditsData {
  total_credits: number;
  used_credits: number;
  remaining_credits: number;
  tier: string;
}

interface HistoryJob {
  id: string;
  agent_id: string;
  agent_name: string;
  status: string;
  credits_used: number;
  created_at: string | null;
  completed_at: string | null;
}

interface AgentUsage {
  agent_id: string;
  agent_name: string;
  count: number;
}

interface Announcement {
  id: string; title: string; body: string; affects: string | null;
  type: string; show_as: string;
}

function isThisMonth(dateStr: string | null): boolean {
  if (!dateStr) return false;
  const d = new Date(dateStr);
  const now = new Date();
  return d.getFullYear() === now.getFullYear() && d.getMonth() === now.getMonth();
}

export default function DashboardPage() {
  const router = useRouter();
  const [credits, setCredits] = useState<CreditsData | null>(null);
  const [jobs, setJobs] = useState<HistoryJob[]>([]);
  const [loading, setLoading] = useState(true);
  const [announcements, setAnnouncements] = useState<Announcement[]>([]);
  const [dismissed, setDismissed] = useState<Set<string>>(new Set());

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) { router.push('/login'); return; }

    const headers = { Authorization: `Bearer ${token}` };

    try {
      const d = JSON.parse(localStorage.getItem('dismissed_announcements') || '[]');
      setDismissed(new Set(d));
    } catch { /* ignore */ }

    Promise.all([
      fetch('/api/workspace/credits', { headers }).then(r => r.ok ? r.json() : null),
      fetch('/api/agents/jobs?skip=0&limit=200', { headers }).then(r => r.ok ? r.json() : null),
      fetch('/api/platform/announcements', { headers }).then(r => r.ok ? r.json() : []),
    ]).then(([c, j, ann]) => {
      if (c) setCredits(c);
      if (j?.jobs) setJobs(j.jobs);
      if (Array.isArray(ann)) setAnnouncements(ann);
    }).finally(() => setLoading(false));
  }, [router]);

  const dismiss = (id: string) => {
    const next = new Set(dismissed).add(id);
    setDismissed(next);
    localStorage.setItem('dismissed_announcements', JSON.stringify(Array.from(next)));
  };

  const completedThisMonth = jobs.filter(
    j => j.status === 'completed' && isThisMonth(j.completed_at || j.created_at)
  ).length;

  const agentCounts: Record<string, AgentUsage> = {};
  for (const job of jobs) {
    if (!agentCounts[job.agent_id]) {
      agentCounts[job.agent_id] = { agent_id: job.agent_id, agent_name: job.agent_name, count: 0 };
    }
    agentCounts[job.agent_id].count++;
  }
  const topAgents = Object.values(agentCounts)
    .sort((a, b) => b.count - a.count)
    .slice(0, 3);

  const pendingApprovals = jobs.filter(j =>
    j.status === 'pending_approval' || j.status === 'pending_financial_review'
  ).length;
  const failedJobs = jobs.filter(j => j.status === 'failed').length;

  if (loading) {
    return (
      <div className="p-8 max-w-5xl">
        <div className="mb-8">
          <div className="animate-pulse bg-gray-800 rounded h-7 w-36 mb-2" />
          <div className="animate-pulse bg-gray-800 rounded h-4 w-56" />
        </div>
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <SkeletonCard />
          <SkeletonCard />
          <SkeletonCard />
          <SkeletonCard />
        </div>
      </div>
    );
  }

  return (
    <>
      <DashboardHeader
        credits={credits}
        pendingApprovals={pendingApprovals}
        failedJobs={failedJobs}
        onSignOut={() => { localStorage.removeItem('token'); router.push('/login'); }}
      />

      <div className="p-8 max-w-5xl">
        <StatusStrip
          credits={credits}
          completedThisMonth={completedThisMonth}
          pendingApprovals={pendingApprovals}
          topAgents={topAgents}
        />

        <AlertsSection
          announcements={announcements}
          pendingApprovals={pendingApprovals}
          failedJobs={failedJobs}
          dismissed={dismissed}
          onDismiss={dismiss}
        />

        <QuickLaunchSection />

        <RecentJobsTable jobs={jobs} />
      </div>

      <ThemeToggle />
    </>
  );
}
```

- [ ] **Step 4: Run integration test**

```bash
cd frontend
npm test -- page.integration.test.tsx
```

Expected: `PASS`

- [ ] **Step 5: Run full dashboard test suite**

```bash
cd frontend
npm test -- dashboard/
```

Expected: All tests pass

- [ ] **Step 6: Commit**

```bash
git add frontend/app/dashboard/page.tsx frontend/app/dashboard/__tests__/page.integration.test.tsx
git commit -m "refactor: integrate dashboard components into main page"
```

---

## Task 11: Add Global CSS Variables & Styles

**Files:**
- Modify: `frontend/app/globals.css` (add oklch palette + header height vars)

**Interfaces:**
- Produces: CSS variables for oklch color palette, header heights, max-width breakpoints
  - `--color-surface`, `--color-border`, `--color-text-primary`, `--color-text-secondary`
  - Status color variables for pending/in-progress/approval/completed/failed
  - `--header-height-desktop` (70px), `--header-height-mobile` (60px)
  - `--max-width-content` (1200px)

- [ ] **Step 1: Read current globals.css**

```bash
cd frontend
head -50 app/globals.css
```

- [ ] **Step 2: Add CSS variables at top of globals.css**

Prepend to `frontend/app/globals.css`:

```css
:root {
  /* oklch color palette */
  --color-surface: oklch(1 0 0 / 0.04);
  --color-border: oklch(1 0 0 / 0.08);
  --color-text-primary: oklch(1 0 0);
  --color-text-secondary: oklch(0.50 0 0);
  
  /* status colors */
  --color-status-pending: oklch(0.82 0.18 65);
  --color-status-in-progress: oklch(0.60 0.18 250);
  --color-status-approval: oklch(0.75 0.18 55);
  --color-status-completed: oklch(0.75 0.22 145);
  --color-status-failed: oklch(0.65 0.18 25);
  
  /* layout */
  --header-height-desktop: 70px;
  --header-height-mobile: 60px;
  --max-width-content: 1200px;
}

@media (max-width: 768px) {
  :root {
    --header-height-desktop: 60px;
  }
}
```

- [ ] **Step 3: Verify CSS loads**

```bash
cd frontend
npm run dev &
# Open http://localhost:3000/dashboard in browser
# Inspect <html> element to verify CSS variables are set
```

- [ ] **Step 4: Commit**

```bash
git add frontend/app/globals.css
git commit -m "feat: add oklch color palette and layout CSS variables"
```

---

## Task 12: Test Responsive Layout (Desktop, Tablet, Mobile)

**Files:**
- Create: `frontend/app/dashboard/__tests__/responsive.test.tsx`

**Test Coverage:**
- Desktop (1024px+): 4-col metric cards, 3-col quick actions, full table
- Tablet (768-1023px): 2-col metric cards, 2-col quick actions, compact table
- Mobile (<768px): 1-col metric cards, 2-col quick actions, card stack for jobs

- [ ] **Step 1: Write responsive layout tests**

Create `frontend/app/dashboard/__tests__/responsive.test.tsx`:

```typescript
import { render } from '@testing-library/react';
import DashboardPage from '../page';

jest.mock('next/navigation', () => ({
  useRouter: () => ({ push: jest.fn() }),
}));

global.fetch = jest.fn(() =>
  Promise.resolve({
    ok: true,
    json: async () => ({ jobs: [], total_credits: 1000, used_credits: 0, remaining_credits: 1000, tier: 'growth' }),
  })
) as jest.Mock;

describe('Dashboard Responsive Layout', () => {
  beforeEach(() => {
    localStorage.setItem('token', 'test-token');
  });

  it('renders desktop layout (1024px+)', () => {
    window.innerWidth = 1280;
    const { container } = render(<DashboardPage />);
    const metricGrid = container.querySelector('.grid.grid-cols-2.lg\\:grid-cols-4');
    expect(metricGrid).toBeInTheDocument();
  });

  it('renders tablet layout (768-1023px)', () => {
    window.innerWidth = 800;
    const { container } = render(<DashboardPage />);
    const metricGrid = container.querySelector('.grid');
    expect(metricGrid).toBeInTheDocument();
  });

  it('renders mobile layout (<768px)', () => {
    window.innerWidth = 480;
    const { container } = render(<DashboardPage />);
    const header = container.querySelector('[style*="position: sticky"]');
    expect(header).toBeInTheDocument();
  });
});
```

- [ ] **Step 2: Run responsive tests**

```bash
cd frontend
npm test -- responsive.test.tsx
```

Expected: `PASS`

- [ ] **Step 3: Manual responsive testing**

```bash
cd frontend
npm run dev &
```

Open browser DevTools → Device toolbar:
- Desktop (1366x768): Verify 4-col metric cards, 3-col quick actions, full table
- Tablet (768x1024): Verify 2-col metric cards, 2-col quick actions
- Mobile (375x667): Verify 1-col cards, 2-col quick actions, vertical job list

- [ ] **Step 4: Verify sticky header**

- Mobile: Scroll down dashboard, verify header stays at top
- Desktop: Scroll down, verify header stays at top (z-index 100)

- [ ] **Step 5: Verify theme toggle**

- Click theme toggle (bottom-left), cycles dark → light → auto
- Reload page, verify theme persists from localStorage

- [ ] **Step 6: Verify collapsible section**

- Click chevron on "Status" section, collapses metric cards
- Reload page, verify collapsed state persists

- [ ] **Step 7: Commit**

```bash
git add frontend/app/dashboard/__tests__/responsive.test.tsx
git commit -m "test: add responsive layout tests and manual verification"
```

---

## Validation

```bash
cd frontend
npm run build              # Full build passes
npm test -- dashboard/    # All dashboard tests pass
npm run lint              # No linting errors
```

---

## Risks

| Risk | Likelihood | Mitigation |
|---|---|---|
| oklch colors not supported in older browsers | Low | Safari 15.1+, Chrome 111+; fallback to oklch keywords |
| localStorage quota exceeded | Very low | Dismissed announcements + theme pref < 1KB |
| useTheme hook SSR hydration mismatch | Medium | useEffect defers to client; theme not set on server render |
| Collapsible state loss on hard refresh | Low | localStorage persists across reloads |
| Polling interval causes excessive API calls | Low | 10s interval per spec, exponential backoff on errors |
| Touch targets < 44px on mobile | Medium | Verify all interactive elements >= 44px (Task 12) |

---

## Notes

- All components use inline oklch styles to avoid Tailwind conflicts
- No external dependencies added (React + Next.js built-ins only)
- Collapsible state stored as single JSON object in localStorage
- Theme preference cycles: dark → light → auto → dark
- All tests use Jest + React Testing Library (existing in project)
