# ADR-0002: Use JWT Bearer Authentication with Role-Based Authorization

## Status

Accepted

## Context

E-commerce Lite needs:

- login for both `admin` and `customer`
- protected API endpoints with visible `401` and `403` behavior
- a frontend that can call the REST API without server-side session setup
- a solution that is easy to demo and straightforward to explain

The current code already uses password hashing and JWTs. The frontend stores the token in browser storage and sends it as `Authorization: Bearer <token>`.

The main role story is:

- `admin`: catalog management and all-order review
- `customer`: browse, checkout, and own-order history

The code still contains transitional `user` alias behavior for compatibility with older assumptions/tests.

## Decision

We use JWT bearer authentication plus server-side role checks.

Implementation shape:

- users log in with username/password at `POST /api/v1/auth/login`
- passwords are stored as hashes
- the backend returns a signed JWT containing `user_id`, `role`, and expiry
- protected routes use `token_required`
- role checks use `role_required(...)`

Current client-side handling:

- the vanilla JS frontend stores auth state in browser storage
- protected API requests attach the JWT in the `Authorization` header
- a `401` response clears stored auth and redirects the user back into the login flow where needed

## Consequences

### Benefits

- simple for a small SPA-style frontend
- no server-side session store required
- explicit and testable `401` versus `403` behavior
- easy to demonstrate across customer and admin flows

### Drawbacks

- browser storage for tokens is a security tradeoff
- tokens are stateless, so there is no revocation list
- authorization consistency still depends on route definitions being correct
- transitional alias handling makes the role model less clean than it should be

## Alternatives considered

### Server-side sessions

Rejected for the current project.

Why:

- would be simpler in some Flask apps, but the current frontend/API interaction already fits bearer tokens well
- would require explaining session storage and cookie behavior instead of using a more explicit API token flow

### OAuth or third-party identity provider

Rejected.

Why:

- unnecessary complexity for the course scope
- would shift focus away from core architecture and domain flows

### API keys

Rejected.

Why:

- unsuitable for end-user login and role-based customer/admin flows

## Follow-up

- tighten catalog authorization so admin management rules are consistent everywhere
- remove the transitional `user` alias once compatibility is no longer needed
- revisit token storage strategy only if the project scope expands beyond a classroom demo
