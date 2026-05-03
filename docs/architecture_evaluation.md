# Architecture Evaluation

## Why this file exists

This is a short check of the current architecture against a few likely demo or defense scenarios.

## Scenario 1: Several users browse and order during the demo

### Scenario

Multiple users open the catalog, add items to the cart, and place orders around the same time.

### What helps

- the frontend is simple and light
- product list responses are cached in memory
- the app can run with PostgreSQL in Compose

### Main risks

- the cache only works inside one app process
- the cart lives in the browser, so item counts can get stale before checkout
- there is no serious load-test setup in the repo

### Mitigation

- check stock again during checkout
- keep the demo on one app instance
- use the cache only as a small improvement, not as a big architecture claim

## Scenario 2: Someone tries to use a protected route

### Scenario

A guest or normal user tries to call an admin-only endpoint.

### What helps

- protected routes require a token
- role checks return `401` or `403`
- the test suite covers several auth cases

### Main risks

- some compatibility role handling is still in place
- tokens are stored in browser storage, which is simple but not ideal

### Mitigation

- keep the role model simple in the presentation: `admin` and `customer`
- show one real `403` example in the demo
- keep secrets out of the repo

## Scenario 3: The database goes down

### Scenario

The database is unavailable when the app is running.

### What helps

- `/health` stays simple
- `/ready` checks the database
- readiness failures return `503`

### Main risks

- there is no automatic failover
- observability is basic

### Mitigation

- use `/ready` in the demo when showing dependency failure
- restart the database and show that the app recovers

## Overall

For this project, one Flask app was a reasonable choice. It is easier to run, easier to explain, and enough to show the course requirements. The weak points are mostly around hardening, not missing core features.
