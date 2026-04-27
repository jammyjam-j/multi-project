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

### P0 (must do): Fix `/ready` endpoint semantics
**Problem**: The readiness endpoint returns 200 even when the database connection fails silently. This masks failures during deployment and makes troubleshooting difficult.  
**Impact**: Blocks reliable demo — system appears healthy when it is not.

### P1 (should do): Add consistent error handling and HTTP status codes
**Problem**: Missing validation returns 500 instead of 400; unhandled exceptions crash the server.  
**Impact**: Improves reliability and API contract compliance.

### P2 (nice to do): Complete documentation with ADRs and architecture diagrams
**Problem**: No architectural decisions are documented; new team members cannot understand design rationale.  
**Impact**: Improves clarity for defense and future maintenance.

---

## Week 10 Lab — Fix Evidence

### Fix: `/ready` endpoint now returns accurate database status

**BEFORE** (failing case):
```bash
# DB connection fails but endpoint returns 200
curl http://localhost:5000/ready
# {"status": "ready"}  ← INCORRECT when DB is down
```

**AFTER** (correct behavior):
```bash
# DB connection fails — endpoint returns 503 with details
curl http://localhost:5000/ready
# {"status": "not_ready", "error": "connection refused"}

# After DB restart — endpoint returns 200
curl http://localhost:5000/ready
# {"status": "ready", "database": "connected"}
```

**Commands to verify**:
```bash
# Start the API
python run.py

# Test health endpoint
curl http://localhost:5000/health

# Test readiness endpoint
curl http://localhost:5000/ready

# Run test suite
pytest -v
```
