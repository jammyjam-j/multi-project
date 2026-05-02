# E-commerce Lite

**Author:** Myroslav Abdeljawwad — Student ID **74448**  
Course project: Design of Multi-Tier Internet Applications (simulation / demo scope).

## What the system does

E-commerce Lite is a course project that demonstrates a three-tier web application:

- A vanilla JavaScript frontend served by Flask
- A versioned Flask REST API under `/api/v1`
- A SQLAlchemy data tier (SQLite for local dev, PostgreSQL when using Docker Compose)

The app supports two primary roles:

- `customer`: log in, browse the catalog, manage a cart in the browser, check out, **run a simulated payment**, and view personal orders
- `admin`: log in, create and delete categories/products, and review all orders

The codebase still contains transitional `user` alias handling so older tests and flows continue to work, but the main system story is `admin` plus `customer`.

Core health endpoints (course brief + versioned API):

- `GET /health` and `GET /api/v1/health` (liveness)
- `GET /ready` and `GET /api/v1/ready` (readiness; `503` when the database is unavailable)

The implementation includes a small in-memory cache for paginated product-list responses.

**Simulated payments:** new orders are created in `pending_payment`. The customer completes checkout in the UI with **Pay (simulated)**, which calls `POST /api/v1/orders/<id>/simulate-payment` and sets status to `paid`.

## Project structure

```text
app/
  api/                       Flask route modules for auth, health, products, categories, orders
  services/                  Application logic for auth, catalog, orders, validation, cache
  static/js/                 Frontend app, API client, local state, view modules
  templates/                 Frontend HTML shell
adr/                         Architecture Decision Records (ADRs)
models.py                    SQLAlchemy models
seed.py                      Demo data seeding script
architecture.md              Architecture overview + diagram
architecture_evaluation.md   Scenario evaluation
technical_debt.md            Debt tracking
README.md
tests/
```

## How to run locally

### Prerequisites

- Python 3.11+
- `pip`

### Setup

```bash
python -m venv .venv
. .venv/Scripts/activate
pip install -r requirements.txt
copy .env.example .env
python seed.py
python run.py
```

Open `http://127.0.0.1:5000/`.

Notes:

- Flask serves both the frontend shell and the API.
- The default local database is SQLite (`DATABASE_URL` in `.env`).
- `seed.py` backfills the expected demo users, categories, and products without duplicating them.

## How to run with Docker Compose

Compose starts **two containers**: PostgreSQL 15 and the Flask app. The compose file sets `DATABASE_URL` to PostgreSQL (overriding `.env` for that service).

```bash
copy .env.example .env
docker compose up --build
```

In a second terminal (after the app is up), load demo data once:

```bash
docker compose exec ecommerce-lite python seed.py
```

Open `http://127.0.0.1:5000/`.

The `./instance` volume is still mounted for optional SQLite experiments; the default Compose path uses PostgreSQL inside the `db` service.

## Required environment variables

| Variable | Required | Example | Purpose |
|---|---|---|---|
| `SECRET_KEY` | Yes outside local dev | `replace-with-a-local-dev-secret` | JWT signing key and Flask secret |
| `DATABASE_URL` | Yes for predictable setup | `sqlite:///products.db` locally; Compose injects PostgreSQL | SQLAlchemy connection string |
| `API_TIMEOUT` | No | `30` | Reserved config value for API timeout-related settings |
| `ENV` | No | `development` | Keeps local development aligned with config expectations |

Important:

- Do not rely on the fallback development secret outside development.
- The repo includes `.env.example`, but not a committed real secret. JWT and database settings are intended to come from the environment, not from hardcoded values in source.
- `config.py` loads `.env` automatically via `python-dotenv` when the config module is imported.

Product prices use `Numeric` (not float) for safer money handling. Validation rejects empty names and negative price or stock. Tests cover auth success and failure paths, invalid input, expired tokens, and related edge cases (see [How to test](#how-to-test)).

## How to test

Install dependencies, then run:

```bash
pytest tests/ -v --tb=short
```

The test suite covers:

- login success/failure
- `401` and `403` auth behavior
- product/category CRUD behavior
- order creation, simulated payment, and order listing
- health/readiness endpoints (including `/health` and `/ready` aliases)
- seed-data backfill behavior

## Demo steps for happy path

### Customer flow

1. Start the app and run `python seed.py` (or `docker compose exec ecommerce-lite python seed.py` under Compose).
2. Open the browser at `http://127.0.0.1:5000/`.
3. Browse the catalog without logging in.
4. Add one or more products to the cart.
5. Open `Login` and sign in as `customer1 / customer123`.
6. Return to the cart and place an order (status **pending_payment**).
7. Open **My Orders** and click **Pay (simulated)** so the order becomes **paid**.
8. Confirm the order history shows line items and total.

### Admin flow

1. Log out.
2. Log in as `admin / admin123`.
3. Open `Admin`.
4. Create a category or product.
5. Show the updated catalog/admin list.
6. Open the orders section in the admin dashboard and show all recorded orders.

## Demo steps for failure path

Use one or more of these during the presentation:

1. Open the cart as a guest and try to place an order.  
   Expected result: the frontend asks the user to log in first.
2. Log in as `customer1` and attempt an admin-only API call in Postman or browser dev tools, such as `DELETE /api/v1/products/1`.  
   Expected result: `403 Insufficient permissions`.
3. Submit bad login credentials to `POST /api/v1/auth/login`.  
   Expected result: `401 Invalid credentials`.
4. Try to order more items than are in stock.  
   Expected result: a validation error such as `Insufficient stock for product ...`.
5. Stop the database (for example `docker compose stop db`), then call `GET /ready` or `GET /api/v1/ready`.  
   Expected result: `503` with a safe JSON body. Start `db` again to show recovery.

## Seed data

The seed script prepares a repeatable demo state with:

- users: `admin`, `customer1`
- categories: `Electronics`, `Peripherals`, `Audio`, `Accessories`
- products: 8 sample catalog items with stock counts and category assignments

## Key external libraries used

- `Flask`: web framework and routing
- `Flask-SQLAlchemy`: ORM integration
- `PyJWT`: JWT creation and verification
- `Flask-CORS`: CORS support for the frontend/API boundary
- `Werkzeug` password hashing utilities: secure password storage
- `pytest`: automated testing
- `python-dotenv`: local environment file loading support
- `psycopg2-binary`: PostgreSQL driver for the Compose deployment path

## Delivery notes

This project is intentionally course-scale, not production-ready. Documentation required by the course brief lives in the **repository root**: [architecture.md](architecture.md), [architecture_evaluation.md](architecture_evaluation.md), [technical_debt.md](technical_debt.md), and [adr/](adr/). (`final_objective.txt` references `docs/…`; this repo keeps the same filenames at the repository root.)

Optional folders such as `docs/` (plans, tooling notes) and `Presentation_Notes.md` are listed in `.gitignore` so they stay local if you prefer a minimal submission tree.
