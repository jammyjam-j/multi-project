# Architecture Evaluation

## Purpose

This document evaluates the current E-commerce Lite architecture against realistic course-project scenarios. It is not a production readiness claim. The goal is to show where the current modular-monolith design works well, where it is weak, and what mitigations are already present or planned.

## Scenario 1: Demo-day customer checkout load

### Scenario

Several users browse the catalog at the same time during a classroom demo, add items to the cart, and place orders close together.

### What helps today

- product-list reads are cached in memory for a short time (this satisfies the course minimum for scalability/performance alongside the optional future work of publishing `wrk` or `k6` results)
- the frontend is static and lightweight
- Docker Compose can run PostgreSQL for a more realistic data tier than SQLite alone
- order creation and simulated payment stay in one modular monolith deployment

### Risks

- the cache is per-process only, so it does not help across multiple app instances
- without published load tests, you have narrative evidence (cache + tests) rather than benchmark tables
- the browser cart is client-side only, so users can end up with stale quantities before checkout

### Mitigations

- keep catalog reads cheap with the existing cache
- validate stock again at checkout instead of trusting the cart
- keep the demo on a single app instance, which matches the current architecture
- optionally run a small scripted load test before presentation if the rubric is interpreted strictly

## Scenario 2: Unauthorized access to protected actions

### Scenario

A guest or a logged-in non-admin user tries to call protected endpoints directly, such as deleting a product or reading all orders.

### What helps today

- protected endpoints require bearer tokens
- role-based decorators return `401` for missing/invalid auth and `403` for insufficient permissions
- tests already cover several auth success and failure paths
- passwords are hashed before storage

### Risks

- role handling still includes compatibility alias behavior (`user` and `customer`)
- JWTs are stateless, so there is no token revocation list
- tokens are stored in browser storage, which is a reasonable course-project tradeoff but not the safest browser storage model

### Mitigations

- keep the role model documented clearly: primary roles are `admin` and `customer`
- continue covering `401` and `403` behavior with tests
- keep secrets in environment variables and avoid committing real secrets

## Scenario 3: Dependency failure or partial outage

### Scenario

The database is unavailable when the app handles traffic or when a readiness check is performed.

### What helps today

- `GET /api/v1/health` (and `GET /health`) stays focused on liveness
- `GET /api/v1/ready` (and `GET /ready`) performs a database check
- readiness failures are mapped to a safe `503` response instead of leaking raw exception details
- structured logs provide some debugging support during demos

### Risks

- there is no automated recovery or failover path
- Compose still depends on PostgreSQL as a single writable data store
- observability is basic: there are no metrics, traces, or alerting

### Mitigations

- use readiness, not health, as the demo indicator for dependency state
- show recovery by bringing the database container back and re-running `/ready`
- keep logs available for explaining what happened during the presentation

## Overall assessment

For the current E-commerce Lite scope, the modular monolith is the right level of complexity:

- simple to run locally with SQLite
- easy to demonstrate end-to-end including simulated payment
- small enough for students to explain
- structured enough to satisfy the course architecture requirements

Remaining weaknesses are mostly hardening and hygiene (migrations, benchmarks, cache distribution) rather than missing microservices.
