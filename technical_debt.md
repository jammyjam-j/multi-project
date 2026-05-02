# Technical Debt

## Scope

This list covers the most important debt items in the current E-commerce Lite codebase. The focus is on issues that affect correctness, maintainability, or demo reliability.

## Debt items

### 1. Transitional role alias behavior is still in the core authorization path

Current state:

- `role_required()` treats `customer` and `user` as aliases in some checks

Why it matters:

- useful for migration compatibility
- makes the long-term role model less clear

Paydown plan:

- keep alias behavior only as long as compatibility requires it
- migrate remaining callers/tests to `customer`
- remove alias handling once the compatibility window closes

### 2. Layer boundaries are improved but not fully consistent

Current state:

- route modules and service modules exist
- some route handlers still query models directly before calling services

Why it matters:

- boundaries become harder to explain
- business rules can spread across HTTP and service layers

Paydown plan:

- move more read/write orchestration into service functions
- keep routes focused on request parsing, auth, and response mapping
- add small service-level tests where logic becomes shared

### 3. The in-memory cache is simple but limited

Current state:

- product lists are cached in process memory with a short TTL

Why it matters:

- cache contents are lost on restart
- it does not work across multiple app instances
- there is no visibility into hit/miss behavior

Paydown plan:

- keep the current cache for the course requirement
- add basic cache metrics/logging if more evidence is needed
- replace with Redis only if multi-instance behavior is required

### 4. Compose uses PostgreSQL while many tests still use SQLite

Current state:

- automated tests run against in-memory SQLite for speed
- production-like Compose path uses PostgreSQL

Why it matters:

- rare dialect or migration issues would not be caught in CI
- `db.create_all()` is not a substitute for versioned migrations

Paydown plan:

- add Alembic migrations if the project survives beyond the course milestone
- optionally add one integration job that boots Compose and hits `/ready`

### 5. Payment is explicitly simulated

Current state:

- checkout creates `pending_payment` orders; `simulate-payment` marks `paid`

Why it matters:

- no card data, no PSP, no reconciliation

Paydown plan:

- keep the flow as a teaching surface; document that it is intentional

### 6. Frontend state is intentionally simple and partly trust-based

Current state:

- cart and auth state live in browser storage
- the backend re-validates stock at checkout time

Why it matters:

- the cart can become stale
- browser-stored tokens are a reasonable course tradeoff but not the strongest model

Paydown plan:

- keep backend validation as the source of truth
- document the tradeoff in ADRs

## Priority order

1. tighten route/service boundaries if the codebase keeps growing
2. remove or reduce role alias compatibility when safe
3. add migrations if the schema must evolve after the course
4. improve cache and frontend-state hardening only if later milestones require it

## Rationale

The project does not need enterprise-scale refactoring. The most valuable debt work is the work that keeps the architecture internally consistent and easy to defend during review.
