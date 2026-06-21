# ADR 0001: Authentication Strategy

**Date:** 2026-06-21  
**Status:** Accepted

## Context

Vantro AI needs a stateless authentication mechanism suitable for a SaaS platform serving many concurrent users across a Next.js frontend and a FastAPI backend.

## Decision

Use **JWT (JSON Web Tokens)** with the `PyJWT` library for stateless bearer token authentication.

- Tokens are signed with `HS256` using a `SECRET_KEY` environment variable
- Token expiry is 24 hours
- Passwords are hashed with `bcrypt` via `passlib`
- The frontend stores the token in `localStorage` and sends it as `Authorization: Bearer <token>`

## Consequences

**Positive:**
- No server-side session storage required — scales horizontally
- Simple to implement and verify in tests
- Standard pattern well-understood by future contributors

**Negative:**
- Tokens cannot be individually revoked before expiry (acceptable for MVP)
- `localStorage` is vulnerable to XSS — mitigated by `X-Content-Type-Options: nosniff` and strict CSP headers set in `next.config.js`

## Alternatives considered

- **Session cookies + Redis**: Provides revocation but adds Redis infrastructure dependency
- **OAuth2 / third-party SSO**: Deferred to post-MVP
