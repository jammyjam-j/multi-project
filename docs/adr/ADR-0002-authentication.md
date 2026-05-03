# ADR-0002: Authentication

## Status

Accepted

## Context

The app needed:

- login for admin and customer users
- protected API routes
- something easy to connect to a JS frontend

## Decision

I used JWT bearer tokens.

The flow is:

- user logs in with username and password
- password is checked against a stored hash
- backend returns a JWT
- protected routes read the token and check the role

## Why

- simple to use from the frontend
- no server-side session store needed
- easy to test `401` and `403` behavior

## Downsides

- token storage in the browser is a trade-off
- there is no token revocation mechanism

## Alternatives considered

### Server-side sessions

This would also have worked, but JWT was simpler for this project structure.

### OAuth or third-party login

Not needed for the course scope.
