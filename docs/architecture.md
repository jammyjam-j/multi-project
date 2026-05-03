# Architecture

## Overview

This project uses a simple three-tier setup:

- frontend: vanilla JavaScript, HTML, CSS
- backend: Flask API under `/api/v1`
- data layer: SQLAlchemy models with SQLite locally or PostgreSQL in Compose

I kept it as one Flask app because that was easier to build and explain for the course.

## Diagram

```text
+-----------------------------+
| Browser                     |
| - HTML shell                |
| - JS views                  |
| - localStorage auth/cart    |
+-------------+---------------+
              |
              | HTTP
              v
+-----------------------------------------------+
| Flask app                                     |
|                                               |
|  Frontend delivery                            |
|  - /                                          |
|  - /static/*                                  |
|                                               |
|  API                                          |
|  - /api/v1/auth/*                             |
|  - /api/v1/products                           |
|  - /api/v1/categories                         |
|  - /api/v1/orders                             |
|  - /api/v1/health                             |
|  - /api/v1/ready                              |
|                                               |
|  Internal code                                |
|  - auth                                       |
|  - catalog service                            |
|  - order service                              |
|  - validation                                 |
|  - cache                                      |
+-------------------+---------------------------+
                    |
                    | ORM / SQL
                    v
+----------------------------------+
| SQLite or PostgreSQL             |
| - users                          |
| - categories                     |
| - products                       |
| - orders                         |
| - order_items                    |
+----------------------------------+
```

## Frontend

Main files:

- `app/templates/index.html`
- `app/static/js/app.js`
- `app/static/js/api.js`
- `app/static/js/store.js`
- `app/static/js/views/*.js`

The frontend:

- loads the catalog
- keeps cart/auth state in browser storage
- calls the API with `fetch`
- shows messages for login, checkout, and permission errors

## Backend

Main files:

- `app/__init__.py`
- `app/api/*.py`
- `app/services/*.py`
- `app/auth.py`

The backend:

- serves the frontend shell
- exposes versioned API routes
- checks auth and roles
- validates input
- handles catalog and order logic
- returns JSON responses
- exposes `/health` and `/ready`

The split is not strict everywhere. Some logic is in services, but there are still places where routes touch models directly. That is one of the cleanup items in `technical_debt.md`.

## Data layer

Main files:

- `models.py`
- `app/extensions.py`
- `seed.py`

Main entities:

- `User`
- `Category`
- `Product`
- `Order`
- `OrderItem`

One detail worth pointing out: order items keep `product_name`, so old orders are still readable even if a product is deleted later.

## Main flows

### Customer flow

1. Open `/`
2. Frontend loads products and categories
3. User logs in or registers
4. Cart stays in the browser until checkout
5. Checkout calls `POST /api/v1/orders`
6. Payment simulation calls `POST /api/v1/orders/<id>/simulate-payment`
7. User views own orders with `GET /api/v1/orders/mine`

### Admin flow

1. Admin logs in
2. Admin opens the dashboard
3. Admin creates or deletes products/categories
4. Admin views all orders

## Auth and roles

- login uses username/password
- passwords are stored as hashes
- backend returns JWT tokens
- `admin` can manage catalog data and view all orders
- `customer` can place orders and view own orders

The older `user` role is still accepted in some places for compatibility.

## Health, readiness, and cache

- `/health` returns a liveness response
- `/ready` checks whether the database is available
- product list responses use a small in-memory cache

## Deployment

Current setup:

- local development usually uses SQLite
- Docker Compose runs the Flask app with PostgreSQL
- CI runs tests and basic container checks

This is enough for the course project and for a live demo.
