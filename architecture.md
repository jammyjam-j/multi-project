# Architecture

## Overview

E-commerce Lite is implemented as a three-tier modular monolith:

- Presentation tier: vanilla JavaScript frontend, HTML shell, CSS, browser `localStorage` cart/auth state
- Application tier: Flask app exposing a REST API under `/api/v1`
- Data tier: SQLAlchemy models backed by SQLite for `python run.py` or PostgreSQL under Docker Compose

Flask serves both the frontend assets and the API, so deployment stays simple for a student project while the code still keeps frontend, backend, and data concerns separated.

## System diagram

```text
+-----------------------------+
| Browser                     |
| - HTML shell                |
| - Vanilla JS views          |
| - localStorage cart/auth    |
+-------------+---------------+
              |
              | HTTP
              v
+-----------------------------------------------+
| Flask Application                              |
|                                               |
|  Frontend delivery                            |
|  - /                                          |
|  - /static/*                                  |
|                                               |
|  API v1                                       |
|  - /api/v1/auth/register, .../auth/login      |
|  - /api/v1/products                           |
|  - /api/v1/categories                         |
|  - /api/v1/orders                             |
|  - /api/v1/orders/.../simulate-payment        |
|  - /api/v1/health (+ /health alias)           |
|  - /api/v1/ready (+ /ready alias)             |
|                                               |
|  Internal modules                             |
|  - auth + auth_service                        |
|  - product/category routes + catalog_service  |
|  - order routes + order_service               |
|  - validators                                 |
|  - cache_service                              |
+-------------------+---------------------------+
                    |
                    | ORM / SQL
                    v
+----------------------------------+
| SQLite or PostgreSQL via ORM     |
| - users                          |
| - categories                     |
| - products                       |
| - orders                         |
| - order_items                    |
+----------------------------------+
```

## Modular-monolith boundaries

The project is not split into microservices. It is a single deployable Flask app with internal module boundaries that are small enough to explain and test.

### Presentation tier

Main files:

- `app/templates/index.html`
- `app/static/js/app.js`
- `app/static/js/api.js`
- `app/static/js/store.js`
- `app/static/js/views/*.js`

Responsibilities:

- render catalog, cart, login, customer orders, and admin dashboard views
- call the REST API using `fetch`
- keep cart state in browser `localStorage`
- keep login token and role in browser storage
- show user-facing error messages for login, checkout, and access failures

Important boundary:

- the frontend does not access the database directly
- the frontend talks only to `/api/v1`

### Application tier

Main files:

- `app/__init__.py`
- `app/api/*.py`
- `app/services/*.py`
- `app/auth.py`

Responsibilities:

- serve the frontend shell
- expose versioned API routes
- enforce authentication and role checks
- validate requests
- run catalog/order/auth business logic
- produce JSON responses with consistent status codes
- expose health/readiness endpoints
- emit structured JSON logs

Internal application modules:

| Module | Main files | Responsibility |
|---|---|---|
| Auth | `app/api/auth_routes.py`, `app/services/auth_service.py`, `app/auth.py` | Login, JWT creation, token verification, role checks |
| Catalog | `app/api/product_routes.py`, `app/services/catalog_service.py` | Product/category reads and admin-facing management actions |
| Orders | `app/api/order_routes.py`, `app/services/order_service.py` | Checkout, own-order listing, admin all-order listing |
| Shared services | `app/services/validators.py`, `app/services/cache_service.py` | Input validation and in-memory product-list cache |

Boundary rules in practice:

- route modules own HTTP concerns
- service modules own business operations and database mutations
- models define persistence structure and relationships
- shared helpers stay small and reusable

This is not a strict repository pattern. For a course project, controller/service/model separation is present, but some queries still occur directly in route modules. That is acceptable for the current scope and is tracked as debt.

### Data tier

Main files:

- `models.py`
- `app/extensions.py`
- `seed.py`

Entities:

- `User`
- `Category`
- `Product`
- `Order`
- `OrderItem`

Responsibilities:

- persist catalog, users, and order history
- keep product/category and order/order-item relationships
- preserve order history even if a product is later deleted

Important implementation detail:

- `OrderItem.product_id` uses `SET NULL` behavior, while `product_name` is stored on the order item so order history remains readable after catalog changes

## Main flows

### Customer flow

1. Browser loads `/`
2. Frontend fetches `/api/v1/products` and `/api/v1/categories`
3. Customer signs up via `POST /api/v1/auth/register` or logs in through `POST /api/v1/auth/login`
4. JWT is stored in browser storage
5. Cart remains client-side until checkout
6. Checkout posts to `POST /api/v1/orders`
7. Backend validates stock, creates `Order` and `OrderItem` rows with status `pending_payment`, reduces product stock, and commits
8. Customer completes a fake payment through `POST /api/v1/orders/<id>/simulate-payment`, moving the order to `paid`
9. Customer views personal history through `GET /api/v1/orders/mine`

### Admin flow

1. Admin logs in through `POST /api/v1/auth/login`
2. Admin opens the dashboard
3. Frontend loads all orders, products, and categories
4. Admin creates or deletes products/categories through protected endpoints
5. Admin reviews all orders through `GET /api/v1/orders`

## Authentication and authorization

Authentication:

- username/password login
- passwords stored as hashes
- backend issues JWT bearer tokens

Authorization:

- `admin` is required for catalog mutations (products and categories), `GET /api/v1/orders` (all orders), and related admin UI actions
- `customer` is required for checkout, simulated payment, and `GET /api/v1/orders/mine`
- `user` is still accepted as a compatibility alias alongside `customer` in some role checks

## Health, readiness, caching, and observability

Health/readiness:

- `GET /api/v1/health` and `GET /health` return a liveness response
- `GET /api/v1/ready` and `GET /ready` check database availability and map failure to `503`

Caching:

- product-list responses use a simple in-memory cache keyed by page/per-page
- cache entries expire after a short TTL
- catalog writes invalidate cached product-list keys

Observability:

- request/response logs are emitted in JSON format
- this is enough to support course demos and basic troubleshooting

## Deployment shape

Current delivery setup:

- one Docker image for the Flask app
- Docker Compose runs two containers: the Flask app plus PostgreSQL 15
- Compose sets `DATABASE_URL` to PostgreSQL; the app entrypoint runs `db.create_all()` on startup
- local `python run.py` development typically uses SQLite via `.env` (`DATABASE_URL`)
- the `instance/` volume mount remains available for SQLite file storage when you run the container against SQLite for experiments
- CI workflow runs tests plus `docker compose config` and image build checks

This matches the course expectation for a reproducible multi-container local environment while keeping SQLite as a fast path for machines without Docker.
