# ADR-0002: Authentication & Authorization Approach

## Status
Accepted

## Context
- User types and roles: `admin` (full access), `user` (read/write products), `viewer` (read-only)
- Threats considered (basic): Token theft, expired sessions, unauthorized access to mutation endpoints
- Constraints (SPA vs server-rendered, mobile, etc.): API consumed by browser-based frontend; tokens stored in HTTP-only cookies or localStorage

## Decision
We chose: **JWT (JSON Web Tokens)**

Implementation notes:
- Where token/session lives: Client stores token in memory or localStorage; sent in `Authorization: Bearer <token>` header
- How roles are enforced: Middleware extracts `role` claim from JWT; route decorators check minimum required role
- Token expiry: 24 hours; refresh endpoint planned for future iteration

## Consequences
Pros:
- Stateless authentication — no server-side session storage required
- Easy to integrate with frontend (no cookie complexity)
- Self-contained token carries user identity and role

Cons / risks:
- Tokens cannot be invalidated server-side before expiry (no revocation list yet)
- Sensitive data in payload if payload is not encrypted
- Secret key must be protected — currently hardcoded (TODO: move to env vars)

Follow-up actions:
- Add token refresh mechanism
- Implement role-based middleware decorators
- Move secret key to environment variables

## Alternatives
- **Sessions**: Simpler for server-rendered apps; requires session storage (Redis/DB); harder to scale horizontally
- **OAuth provider (Google/GitHub)**: Adds complexity; not needed for demo scope
- **API Keys**: Suitable for service-to-service; not ideal for user-facing authentication
