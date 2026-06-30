# Frontend Development Guide

## Prerequisites

- Node.js 20+
- npm 10+

## Setup

```bash
cd frontend
npm install
```

## Environment variables

Create `frontend/.env.local`:

```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

For production this is set to `https://api.vantro.ai` via Vercel.

## Running locally

```bash
npm run dev
```

App available at `http://localhost:3000`.

## Building for production

```bash
npm run build
npm run start
```

## Running E2E tests (Playwright)

```bash
# Install browsers (first time only)
npx playwright install --with-deps chromium

# Run against local dev server (auto-starts)
npx playwright test

# Run against production
BASE_URL=https://vantro.ai npx playwright test

# Show HTML report
npx playwright show-report
```

## Project structure

```
frontend/
├── app/
│   ├── api/           # Next.js API routes (proxy to backend)
│   ├── login/         # Login page
│   ├── signup/        # Signup page
│   ├── dashboard/     # Dashboard page
│   └── layout.tsx     # Root layout
├── components/        # Shared React components
├── lib/               # Utility functions
├── src/
│   ├── components/    # Feature-specific components
│   └── data/          # Static JSON data files
└── tests/
    └── e2e/           # Playwright E2E tests
```

## Key conventions

- `@/` path alias maps to the `frontend/` root
- `src/` components use relative imports for files within `src/`
- All API calls go through Next.js `/api/` routes which proxy to the backend
- Auth token is stored in `localStorage` under the key `token`
