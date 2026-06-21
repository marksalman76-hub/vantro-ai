# Contributing to Vantro AI

## Development workflow

1. Fork the repo and create a branch from `main`
2. Make your changes with tests
3. Ensure all tests pass: `python -m pytest backend/tests/ -v`
4. Push and open a pull request against `main`

## Branch naming

- `feat/short-description` — new feature
- `fix/short-description` — bug fix
- `chore/short-description` — tooling, deps, docs

## Commit messages

Follow Conventional Commits:

```
feat(auth): add password reset flow
fix(api): correct /api/auth/login path prefix
chore(ci): add Playwright E2E job
```

## Backend changes

See [backend/DEVELOPMENT.md](backend/DEVELOPMENT.md) for setup and test instructions.

All new backend routes must have:
- Corresponding pytest tests in `backend/tests/`
- Input validation via Pydantic models
- Proper HTTP status codes

## Frontend changes

See [frontend/DEVELOPMENT.md](frontend/DEVELOPMENT.md) for setup and test instructions.

All new pages must have:
- A corresponding Playwright E2E test in `frontend/tests/e2e/`
- TypeScript types (no implicit `any`)

## CI checks

All PRs must pass:
- `Backend — pytest` (all auth tests green)
- `Frontend — lint & typecheck` (no ESLint or TypeScript errors)
- `Frontend — Playwright E2E` (all E2E tests green against production)

## Architecture decisions

Major technical decisions are documented in [docs/adr/](docs/adr/).
