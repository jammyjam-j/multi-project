# Technical Debt

## Notes

These are the main things I would clean up next if I had more time.

## 1. Role compatibility code is still around

Current state:

- some auth checks still treat `customer` and `user` as aliases

Why it matters:

- it keeps old behavior working
- it also makes the role model less clear

Next step:

- move everything fully to `customer`
- remove the compatibility handling when it is no longer needed

## 2. Route/service boundaries are not fully consistent

Current state:

- there are route files and service files
- some queries still happen directly in routes

Why it matters:

- it makes the structure harder to explain
- logic can end up split between layers

Next step:

- move more shared logic into services
- keep routes focused on request parsing and response handling

## 3. Cache is basic

Current state:

- product lists are cached in process memory

Why it matters:

- cache is lost on restart
- it does not help if there are multiple app instances

Next step:

- keep it as-is for the course project
- switch to Redis only if the project grows

## 4. Migrations and startup are mixed

Current state:

- Alembic files exist
- the Docker entrypoint still has a `create_all()` fallback

Why it matters:

- schema handling is not as clean as it could be
- SQLite and PostgreSQL differences may be missed

Next step:

- rely more clearly on migrations
- add stronger PostgreSQL checks in CI if needed

## 5. Payment is only simulated

Current state:

- checkout creates `pending_payment`
- a second endpoint marks the order as `paid`

Why it matters:

- this is fine for the course demo
- it is not a real payment flow

Next step:

- keep it documented as a deliberate simplification

## 6. Frontend state is simple

Current state:

- cart and auth state are stored in the browser

Why it matters:

- cart contents can go stale
- browser token storage is a trade-off

Next step:

- keep the backend as the source of truth at checkout
- document the trade-off clearly
