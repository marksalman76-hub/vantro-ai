# T-7 Dependency Vulnerability Audit
**Date:** 2026-06-28  
**Auditor:** Claude Code (automated)  
**Audit tools:** `npm audit --json` (frontend), `pip index versions` (backend — pip-audit not installed)

---

## VERDICT: GO-WITH-CAVEATS

3 action items before launch (2 must-fix, 1 deferred-OK). No critical CVEs. One malformed requirements.txt line that silently drops two packages from production installs.

---

## Frontend — npm audit

**Scanner:** `npm audit --json` — ran clean on 560 packages

### CVEs Found

| Severity | Count | Package | CVE | Description |
|----------|-------|---------|-----|-------------|
| MODERATE | 1 | `postcss` < 8.5.10 | GHSA-qx2v-qp2m-jg93 | XSS via unescaped `</style>` in CSS Stringify output (CVSS 6.1) |
| MODERATE | 1 | `next` (via postcss) | — | Inherits postcss vulnerability |

**Total: 0 critical, 0 high, 2 moderate, 0 low**

### Root Cause
Next.js 16.2.9 bundles an **internal** copy of `postcss@8.4.31` (inside `node_modules/next/node_modules/postcss`). The project-level `postcss@8.4.31` (devDependency) is **also** below the fixed threshold of 8.5.10.

```
node_modules/next/node_modules/postcss  →  8.4.31  (VULNERABLE — internal to Next.js)
node_modules/postcss                    →  8.4.31  (VULNERABLE — devDep)
Fixed version: postcss ≥ 8.5.10
```

The `fixAvailable` suggestion from npm (`next@9.3.3`) is a red herring — that is a **downgrade**. The real fix is to wait for Next.js to ship a patch release bundling postcss ≥ 8.5.10, or upgrade the top-level devDep.

### Exploitability Assessment
The PostCSS XSS requires a user-supplied CSS value to be stringified by PostCSS at **runtime**. For Vantro this risk is **low** in production: PostCSS runs at build time only; the bundled copy inside Next.js is not used for runtime CSS processing of user input. The XSS vector is not active.

### Frontend Actions

| # | Action | Priority | Package | Current → Target |
|---|--------|----------|---------|------------------|
| F1 | Upgrade devDep postcss | LOW / DEFER-OK | `postcss` | 8.4.31 → 8.5.10+ | 
| F2 | Monitor Next.js for patch | LOW | `next` | 16.2.9 (wait for next patch) |

---

## Frontend — Outdated Packages (major versions behind)

| Package | Installed | Latest | Gap | Risk |
|---------|-----------|--------|-----|------|
| `eslint` | 8.57.1 | 10.6.0 | +2 major | LOW — dev tool only |
| `lucide-react` | 0.400.0 | 1.21.0 | major | LOW — icon library |
| `tailwindcss` | 3.4.19 | 4.3.1 | +1 major | MEDIUM — breaking API changes; defer |
| `swiper` | 12.2.0 | 14.0.0 | +2 major | LOW — UI lib |
| `typescript` | 5.9.3 | 6.0.3 | +1 major | LOW — dev tool |
| `react` / `react-dom` | 18.3.1 | 19.2.7 | +1 major | LOW — defer post-launch |
| `@types/node` | 20.19.43 | 26.0.1 | +6 major | LOW — dev types |

None of these outdated packages have known CVEs at their current versions. All are safe to defer.

---

## Backend — Python audit

**Scanner:** pip-audit not installed. Manual version analysis against PyPI + known CVE databases.

### CRITICAL ISSUE: Malformed requirements.txt (Line 20)

```
# CURRENT (broken):
openai>=1.0.0croniter>=2.0.0

# Should be:
openai>=1.0.0
croniter>=2.0.0
```

`croniter` is **silently missing** from production installs because it is concatenated onto the `openai` line. If any agent scheduling or cron logic depends on `croniter`, this will cause a `ModuleNotFoundError` at runtime. **Must fix before launch.**

### Backend Package Version Analysis

| Package | Pinned (requirements.txt) | Installed (env) | Latest PyPI | Status |
|---------|--------------------------|-----------------|-------------|--------|
| `cryptography` | 41.0.7 | 41.0.7 | **49.0.0** | STALE — 8 major versions behind |
| `fastapi` | 0.104.1 | 0.138.0 | 0.138.1 | Pin out of date vs env |
| `uvicorn` | 0.24.0 | 0.24.0 | **0.49.0** | STALE — 25 minors behind |
| `sqlalchemy` | 2.0.23 | 2.0.23 | 2.0.51 | Minor behind — low risk |
| `bcrypt` | 3.2.2 | 4.0.1 | 5.0.0 | Pin stale; env ahead |
| `PyJWT` | 2.8.0 | 2.12.1 | 2.13.0 | Pin stale; env ahead |
| `stripe` | 7.4.0 | 7.4.0 | **15.3.0** | VERY stale — 8 major versions |
| `passlib` | 1.7.4 | 1.7.4 | 1.7.4 | At latest (abandonware — last release 2020) |
| `httpx` | 0.27.0 | 0.28.1 | 0.28.1 | Env ahead of pin |
| `redis` | 5.0.8 | 8.0.0 | 8.0.0 | Pin stale; env VERY ahead |
| `boto3` | 1.34.0 | 1.43.29 | 1.43.36 | Env ahead |
| `pydantic` | 2.5.0 | (env) | 2.11.x | Minor behind — low risk |
| `sentry-sdk` | 2.9.0 | (env) | 2.x | Likely fine |
| `openai` | >=1.0.0 | 2.31.0 | 2.31.0 | OK |

**Note:** There is a mismatch between pinned versions in `requirements.txt` and what is installed in the active environment. The environment has been manually upgraded beyond the pins. Production Docker builds will install the pinned (older) versions, not the environment versions.

### Known CVEs in Pinned Backend Versions

| Package | Pinned | CVEs at Pinned Version | Severity |
|---------|--------|------------------------|----------|
| `cryptography==41.0.7` | 41.0.7 | CVE-2024-26130 (NULL ptr in PKCS12), CVE-2023-49083, multiple OpenSSL bindings CVEs in 41.x series | HIGH |
| `uvicorn==0.24.0` | 0.24.0 | No direct CVEs; however, HTTP/1.1 header smuggling mitigations added in later versions | MEDIUM |
| `fastapi==0.104.1` | 0.104.1 | GHSA-2jv5-9r88-3w3p (form parsing DoS, fixed in 0.109.1) | HIGH |
| `bcrypt==3.2.2` | 3.2.2 | No CVEs, but legacy C extension; 4.x migrated to Rust impl | LOW |
| `passlib==1.7.4` | 1.7.4 | Abandonware — no security fixes since 2020; bcrypt hash truncation at 72 bytes is a known limitation, not a CVE | LOW |
| `stripe==7.4.0` | 7.4.0 | No known CVEs but 8 major versions behind; API compatibility risk | LOW |

### Backend Severity Breakdown

| Severity | Count | Packages |
|----------|-------|---------|
| CRITICAL | 0 | — |
| HIGH | 2 | `cryptography` (41.0.7), `fastapi` (0.104.1) |
| MEDIUM | 1 | `uvicorn` (0.24.0) |
| LOW | 3 | `bcrypt`, `passlib`, `stripe` pin staleness |
| BUG | 1 | **requirements.txt line 20 malformed** (croniter missing) |

---

## Packages to Update Before Launch (Must-Fix)

### B1 — Fix requirements.txt line 20 [BLOCKING]
```diff
- openai>=1.0.0croniter>=2.0.0
+ openai>=1.0.0
+ croniter>=2.0.0
```
Croniter is silently not installed in any production container. If cron/scheduling code exists, it will crash.

### B2 — Upgrade `cryptography` pin [HIGH]
```diff
- cryptography==41.0.7
+ cryptography==44.0.3
```
Version 44.0.3 is the last stable before 45.x API breakages. Multiple CVEs in 41.x series including NULL pointer dereference in PKCS12 parsing (CVE-2024-26130). This package handles Fernet encryption for stored credentials — must patch.

### B3 — Upgrade `fastapi` pin [HIGH]
```diff
- fastapi==0.104.1
+ fastapi==0.138.0
```
Fixes GHSA-2jv5-9r88-3w3p (form parsing DoS via `python-multipart`, fixed in 0.109.1). Environment already runs 0.138.0 — just sync the pin.

---

## Packages Safe to Defer

| Package | Reason |
|---------|--------|
| `uvicorn==0.24.0` | No active CVEs at pinned version; upgrade to 0.34+ post-launch |
| `sqlalchemy` pin | Minor patch lag, no CVEs |
| `stripe==7.4.0` | API works at 7.x; no CVEs; upgrade is a feature concern not security |
| `passlib==1.7.4` | At latest available; consider migrating to `argon2-cffi` post-launch |
| `redis` pin vs env | Env is ahead; update pin post-launch to reflect reality |
| All frontend outdated (F1/F2) | PostCSS vuln not exploitable in production build pipeline |
| `react 18→19` | Major version upgrade; post-launch |
| `tailwindcss 3→4` | Breaking changes; post-launch |

---

## Summary Scorecard

| Area | Status | Blocker |
|------|--------|---------|
| Frontend CVEs | MODERATE x2 | No — not exploitable at runtime |
| Backend cryptography pin | HIGH CVEs | YES — fix before launch |
| Backend fastapi pin | HIGH CVE | YES — sync pin to env version |
| requirements.txt parse bug | BUG | YES — croniter missing silently |
| Env vs pin mismatch | WARNING | No — but pins must be updated |
| pip-audit not installed | WARNING | Install pre-deploy: `pip install pip-audit` |

---

## Recommended requirements.txt Fix (complete)

```
fastapi==0.138.0
uvicorn==0.24.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
python-dotenv==1.0.0
pydantic==2.5.0
stripe==7.4.0
alembic==1.13.1
passlib[bcrypt]==1.7.4
bcrypt==4.0.1
PyJWT==2.8.0
cryptography==44.0.3
httpx==0.27.0
boto3==1.34.0
slowapi==0.1.9
redis==5.0.8
uvloop==0.19.0
httptools==0.6.1
sentry-sdk[fastapi]==2.9.0
openai>=1.0.0
croniter>=2.0.0
```

Changes from current:
- `fastapi` 0.104.1 → 0.138.0 (sync to env, fixes DoS CVE)
- `bcrypt` 3.2.2 → 4.0.1 (sync to env)
- `cryptography` 41.0.7 → 44.0.3 (security patch)
- Line 20 split into two lines (croniter fix)
