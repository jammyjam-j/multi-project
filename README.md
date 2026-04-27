# Product API — Multi-Tier Internet Application

A Flask-based REST API for product management with authentication, health checks, and database integration.

## Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Client    │────▶│   Flask API  │────▶│   SQLite /  │
│  (Browser)  │     │   (Tier 2)   │     │  PostgreSQL │
└─────────────┘     └─────────────┘     └─────────────┘
   Tier 1              Tier 2               Tier 3
 (Presentation)     (Application/Business)  (Data Persistence)
```

## Contributors

| Name | Student ID |
|------|------------|
| Myroslav Abdeljawwad | 74448 |
| Elmehdi Lamrani | 70698 |

## Quick Start

### Prerequisites
- Python 3.11+
- pip
- Docker + Docker Compose (optional)

### Local Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Run the API
python run.py

# Run tests
pytest
```

### Docker Setup
```bash
docker compose up --build
```

### Environment Variables
| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite:///products.db` | Database connection string |
| `SECRET_KEY` | `dev-secret-key-change-in-production` | JWT secret key |
| `API_TIMEOUT` | `30` | Timeout for external calls (seconds) |

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/ready` | Readiness probe (DB check) |
| POST | `/auth/login` | User login |
| GET | `/products` | List products (paginated) |
| GET | `/products/<id>` | Get product by ID |
| POST | `/products` | Create product |
| PUT | `/products/<id>` | Update product |
| DELETE | `/products/<id>` | Delete product |

## Project Structure
```
week10/
├── app/            # Flask application factory
│   ├── __init__.py # App initialization
├── models.py       # Database models (Product, User)
├── routes.py       # API endpoints & blueprints
├── config.py       # Configuration
├── run.py          # Entry point
├── tests/          # Test suite
│   └── test_api.py # API tests
├── docs/           # Documentation
│   └── adr/        # Architecture Decision Records
├── Dockerfile      # Container definition
├── docker-compose.yml # Multi-service orchestration
└── requirements.txt # Python dependencies
```

---

## Week 10 Lab — Priorities

### P0 (must): Hash passwords + enforce JWT on product mutations
- **Hashed passwords** using `werkzeug.security.generate_password_hash` / `check_password_hash` — plain-text passwords no longer stored
- **JWT enforced** on all product mutations (POST, PUT, DELETE) via `@token_required` decorator — unauthenticated requests return 401

### P1 (should): Fix compose DB config; sanitize `/ready` errors
- **docker-compose.yml** simplified to SQLite-only (matches local dev config); removed unused PostgreSQL dependency
- **`/ready` endpoint** no longer leaks raw exception text — returns generic `"database unavailable"` message

### P1 (should): Configuration hardening with environment variables
- **Secrets moved to `.env`** — JWT secret and database config no longer hardcoded in source code

### P2 (nice): Price numeric type + stronger validation + expand auth tests
- **Price field** changed from `db.Float` to `db.Numeric(precision=10, scale=2)` for financial accuracy
- **Validation** added: name cannot be empty, price must be non-negative, stock cannot be negative
- **Auth tests** expanded: login success, invalid credentials, nonexistent user, unauthenticated mutation attempts

### P2 (nice): Additional edge-case tests
- **Extra tests added** — covers invalid input, expired tokens, and boundary values
---

## Week 10 Lab — Fix Evidence

### Fix: `/ready` endpoint no longer leaks raw exception text

**BEFORE**:
```json
{"status": "not_ready", "error": "connection refused: (2003) Can't connect to server..."}
```

**AFTER**:
```json
{"status": "not_ready", "reason": "database unavailable"}
```

### Fix: Passwords are hashed, not stored in plain text

| Before | After |
|--------|-------|
| `user.password_hash = 'admin123'` | `user.password_hash = 'pbkdf2:sha256:...` |

### Fix: Product mutations require JWT

| Endpoint | Without token | With token |
|----------|---------------|------------|
| `POST /products` | 401 Unauthorized | 201 Created |
| `PUT /products/1` | 401 Unauthorized | 200 OK |
| `DELETE /products/1` | 401 Unauthorized | 200 OK |
