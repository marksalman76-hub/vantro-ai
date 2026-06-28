# Dashboard Redesign Spec

**Date:** 2026-02-27  
**Project:** Vantro Dashboard  
**Approach:** C Layout (Sticky Header + Full Sections)  
**Target:** Premium, dense, power-user-focused

---

## Requirements

- **Hybrid usage:** Support both quick action (run agent fast) and monitoring (status, approvals, failures)
- **Visual direction:** Dark cinematic + dense/efficient (matches recent hero redesign)
- **All info scannable:** No hidden tabs; everything visible in one scroll (desktop)
- **Mobile-responsive:** Stacks vertically on mobile; header sticky throughout

---

## Layout Architecture

### Sticky Header (Height: 70px desktop / 60px mobile)

**Left:**
- Vantro logo + workspace name

**Center:**
- Large "Run Agent" button (primary CTA, link to `/dashboard/agents`)
- Premium accent color, cinematic styling

**Right:**
- Credits meter (compact, color-coded warning: red <20%, amber <50%, green ≥50%)
- Alerts badge (count of pending approvals + failed jobs; collapsible via chevron)
- Sign-out button (icon + dropdown menu)

**Behavior:**
- Sticky to top on scroll (z-index: 100)
- Dark gradient background, subtle shadow below
- All interactive elements keyboard-accessible

---

### Main Content Sections (Full Width, Stacked)

#### Section A: Status Strip (Collapsible)

**Grid layout:**
- Desktop: 4 cards (Credits, Jobs this month, Plan tier, Pending approvals)
- Mobile: 2 cards stacked (Credits + Jobs, Plan + Approvals)

**Cards:**
- **Credits remaining:** Value + subtext "of X total"; color-coded (red/amber/green)
- **Jobs completed this month:** Count + subtext "completed status"
- **Plan tier:** Badge with current plan name (starter/growth/business/enterprise)
- **Pending approvals:** Count + link to `/dashboard/approvals`

**Collapsible:**
- Chevron icon in section header toggles open/close
- Visible by default; state persisted in localStorage
- Smooth collapse/expand animation (100–150ms)

---

#### Section B: Alerts & Announcements

**Platform Announcements:**
- Render each dismissible banner (if `show_as === 'banner'` and not dismissed)
- Type-based styling: info (blue), new_feature (blue), warning (amber), maintenance (orange)
- Each has title, body, optional "affects" callout, dismiss button

**Action Cards:**
- **Pending approvals:** Prominent card (orange accent) if count > 0; links to `/dashboard/approvals`
  - Shows count + "Review before we continue"
- **Failed jobs:** Red accent card if count > 0; links to `/dashboard/jobs?filter=failed`
  - Shows count + "Retry or contact support"

**Stacking:** Vertical; each dismissible independently.

---

#### Section C: Quick-Launch Agents

**Grid:**
- Desktop: 3 columns
- Tablet: 2 columns
- Mobile: 2 columns (full width on very small)

**6 Cards:**
1. **Run an agent** → `/dashboard/agents`
2. **Output library** → `/dashboard/library`
3. **Weekly report** → `/dashboard/reports`
4. **Brand profile** → `/dashboard/brand`
5. **Billing & credits** → `/dashboard/billing`
6. **Settings** → `/dashboard/settings`

**Card styling:**
- Dark card (oklch bg + border)
- Icon (emoji or symbol) + label + description
- Hover state: subtle brightness increase, smooth transition
- Large touch targets: min 44px height, 1rem padding

---

#### Section D: Recent Jobs (Dense Table)

**Columns:**
1. **Agent name** (truncate on overflow)
2. **Status badge** (colored inline: yellow/blue/green/red/gray)
3. **Credits used** (right-aligned)
4. **Created timestamp** (right-aligned, relative time or locale string)

**Behavior:**
- Show 15 rows by default
- Sortable by status, date, credits (click column header)
- "Load more" button at bottom; or infinite scroll on demand
- Row click → navigate to job detail page (future: modal)
- Empty state: "No jobs yet" + link to run first agent

**Data refresh:**
- Poll API every 10s for running jobs
- Manual refresh button (icon) in section header
- Optimistic updates for status changes

---

## Visual Language

### Color Palette
- Background: `oklch(1 0 0 / 0.04)` dark surface
- Cards/borders: `oklch(1 0 0 / 0.08)` subtle divide
- Text: `oklch(1 0 0)` primary, `oklch(0.50 0 0)` secondary
- Accents: oklch hues per status
  - Pending: `oklch(0.82 0.18 65)` yellow
  - In progress: `oklch(0.60 0.18 250)` blue
  - Approval needed: `oklch(0.75 0.18 55)` orange
  - Completed: `oklch(0.75 0.22 145)` green
  - Failed/Error: `oklch(0.65 0.18 25)` red

### Typography
- Headings: Bold, clear hierarchy (h1 > h2 > h3)
- Body: Regular, readable on mobile
- Status badges: Small (10–12px), semibold
- Subtext: Muted color, 0.875x scale

### Spacing
- Header height: 70px (desktop), 60px (mobile)
- Section padding: 2rem (desktop), 1rem (mobile)
- Card gap: 1rem
- Internal card padding: 1.25rem

### Motion
- Collapse/expand: 150ms ease-out
- Hover/focus: 200ms smooth
- Toast/feedback: fade-in 100ms, fade-out 300ms
- Avoid bloat: no decorative animation

---

## Responsive Behavior

**Desktop (≥1024px):**
- Sticky header fixed
- Full-width sections (max-width: 1200px)
- All 4 status cards visible
- 3-column grid for quick actions
- Dense table with horizontal scroll fallback

**Tablet (768–1023px):**
- Sticky header fixed
- 2-column status cards
- 2-column quick-action grid
- Table compresses; small columns may hide on mobile

**Mobile (<768px):**
- Sticky header (60px)
- 2-column status cards stack to 1 column
- 2-column quick-action grid maintained (full width)
- Table becomes card stack (Agent name + Status | Credits + Time)
- Horizontal overflow for dense data tables

---

## Component Details

### MetricCard (A-Section)
- Props: `label`, `value`, `sub`, `color`
- Inline styles for oklch colors
- Flex column, gap 0.25rem

### ActionCard (C-Section)
- Props: `href`, `icon`, `label`, `desc`
- Large touch targets
- Hover brightness increase

### StatusBadge (D-Section)
- Props: `status` (string from `CLIENT_STATUS`)
- Lookup style from `STATUS_INLINE_STYLES`
- Inline styles, border-radius 9999px

### RecentJobsTable
- Virtualized on mobile (render visible rows + buffer)
- Sortable columns (click header)
- Polled refresh with exponential backoff

---

## Footer

**Bottom left:** Light/dark mode toggle
- Sun/moon icon
- Click cycles: dark → light → auto (OS preference)
- State in localStorage (`theme-preference`)

---

## Error Handling

- API fetch error: show inline toast, fallback to cached data
- Missing data: render empty state with actionable next step
- Slow polling: show "loading…" spinner, don't block UI

---

## Testing

- Unit: Each component in isolation
- Integration: Sections load data independently (no hydration cascade)
- E2E: User can run agent, see status update, check approvals
- Mobile: Responsive layout, touch targets ≥44px
- Accessibility: WCAG AA, keyboard nav, screen reader friendly

---

## Migration Path

1. Rename old `page.tsx` → `page.old.tsx` (backup)
2. Create new `page.tsx` with section components
3. Extract `MetricCard`, `ActionCard`, `RecentJobsTable` to `/components/dashboard/*`
4. Update imports in layout middleware if needed
5. Test against API (local dev server running)
6. Deploy with feature flag (optional) or direct rollout

---

## Known Constraints

- Max width: 1200px (future: may add sidebar for nav; adjust width then)
- Polling interval: 10s (configurable per workspace tier)
- Jobs limit: 200 rows fetched (pagination/infinite scroll handles rest)
- Theme: CSS variables only (no Tailwind theme merge conflicts)

