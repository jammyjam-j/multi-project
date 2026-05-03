# E-commerce Lite

**Author:** Myroslav Abdeljawwad - Student ID **74448** 
** Mohammad Fateh Naeem - Student ID **70281** 
Course project for Design of Multi-Tier Internet Applications.

## What the project does

This project is a small e-commerce app built for the course. It has three parts:

- a frontend written in vanilla JavaScript
- a Flask REST API under `/api/v1`
- a database layer through SQLAlchemy

For local work I use SQLite. In Docker Compose I use PostgreSQL.

There are two main roles:

- `customer`: browse products, use the cart, place an order, and view own orders
- `admin`: manage products/categories and view all orders

The repo still accepts the older `user` role in a few places for compatibility, but the main roles are `admin` and `customer`.

The app also includes:

- `GET /health` and `GET /api/v1/health`
- `GET /ready` and `GET /api/v1/ready`
- a simple in-memory cache for product list responses
- a simulated payment step that changes an order from `pending_payment` to `paid`

## Project structure

```text
app/
  api/                       Flask routes
  services/                  Business logic
  static/js/                 Frontend code
  templates/                 HTML shell
docs/                        Course docs
adr/                         Older ADR copy
models.py                    SQLAlchemy models
seed.py                      Demo data script
README.md
tests/
```

## Run locally

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

Then open `http://127.0.0.1:5000/`.

Notes:

- Flask serves both the frontend and the API.
- The default local database comes from `DATABASE_URL` in `.env`.
- `seed.py` can be run more than once without duplicating the demo data.

## Run with Docker Compose

Compose starts PostgreSQL and the Flask app.

```bash
copy .env.example .env
docker compose up --build
```

After the app starts, seed the demo data:

```bash
docker compose exec ecommerce-lite python seed.py
```

Then open `http://127.0.0.1:5000/`.

## Environment variables

| Variable | Required | Example | Purpose |
|---|---|---|---|
| `SECRET_KEY` | Yes outside local dev | `replace-with-a-local-dev-secret` | Flask/JWT secret |
| `DATABASE_URL` | Yes for predictable setup | `sqlite:///products.db` | Database connection |
| `API_TIMEOUT` | No | `30` | Reserved config value |
| `ENV` | No | `development` | Environment name |

Important:

- do not use the fallback development secret outside development
- `.env.example` is included, but real secrets are not committed
- `config.py` loads `.env` through `python-dotenv`

Product prices use `Numeric` instead of float. Validation rejects empty names and negative price/stock values.

## Tests

Run:

```bash
pytest tests/ -v --tb=short
```

The tests cover:

- login and registration
- `401` and `403` responses
- product/category CRUD
- order creation and payment simulation
- health/readiness routes
- seed-data behavior

## Demo steps

### Customer flow

1. Start the app and run `python seed.py`.
2. Open `http://127.0.0.1:5000/`.
3. Browse the catalog.
4. Add products to the cart.
5. Log in as `customer1 / customer123`.
6. Place an order.
7. Open **My Orders** and click **Pay (simulated)**.
8. Show the order history.

### Admin flow

1. Log out.
2. Log in as `admin / admin123`.
3. Open `Admin`.
4. Create a category or product.
5. Show the updated data.
6. Show the full order list.

## Failure-path demo ideas

1. Try to place an order as a guest.  
   Expected: the frontend asks the user to log in.
2. Log in as `customer1` and call an admin-only endpoint like `DELETE /api/v1/products/1`.  
   Expected: `403`.
3. Send bad credentials to `POST /api/v1/auth/login`.  
   Expected: `401`.
4. Try to buy more stock than is available.  
   Expected: validation error.
5. Stop the database and call `GET /ready`.  
   Expected: `503`, then `200` again after restart.

## Seed data

The seed script creates:

- users: `admin`, `customer1`
- categories: `Electronics`, `Peripherals`, `Audio`, `Accessories`
- products: 8 sample items

## Main libraries used

- `Flask`
- `Flask-SQLAlchemy`
- `PyJWT`
- `Flask-CORS`
- `Werkzeug`
- `pytest`
- `python-dotenv`
- `psycopg2-binary`

## Docs

The main course documents are here:

- [docs/architecture.md](docs/architecture.md)
- [docs/architecture_evaluation.md](docs/architecture_evaluation.md)
- [docs/technical_debt.md](docs/technical_debt.md)
- [docs/adr/](docs/adr/)
- [Presentation_Notes.md](Presentation_Notes.md)

There are still some root-level copies from earlier work, but `docs/` is the folder to check.
