# Presentation Notes — Week 10 Final Project

## Story Outline (10-12 slides)

### Slide 1: Title
- Product API — Multi-Tier Internet Application
- Team members, course, week

### Slide 2: Problem
- Need a centralized product catalog with CRUD operations
- Must support authentication and role-based access
- Should be deployable with minimal infrastructure

### Slide 3: Requirements
- REST API with standard HTTP methods
- Health/readiness endpoints for orchestration
- JWT authentication for protected resources
- Database abstraction for local/production flexibility

### Slide 4: Architecture
- 3-tier design: Presentation → Application → Data
- Modular monolith with Flask blueprints
- SQLite for development, PostgreSQL for production

### Slide 5: Tradeoffs
- Chose modular monolith over microservices (simplicity vs scalability)
- Chose JWT over sessions (statelessness vs revocation complexity)
- SQLite for demo, PostgreSQL for production (convenience vs features)

### Slide 6: Demo Plan
**Happy Path**:
1. Show `/health` — system is healthy
2. Create product via POST `/products`
3. List products via GET `/products`
4. Update stock via PUT `/products/<id>`

**Failure Path**:
1. Show `/ready` when DB is down — returns 503
2. Try creating product with missing fields — returns 400
3. Access protected endpoint without token — returns 401

**Recovery**:
1. Restart DB container
2. Show `/ready` returns 200 again
3. Verify data integrity after restart

### Slide 7: Results
- All endpoints functional with proper status codes
- Health checks accurately reflect system state
- Tests pass (pytest suite)

### Slide 8: Risks & Technical Debt
- Secret key hardcoded (TODO: env vars)
- No rate limiting implemented
- JWT validation not enforced on all endpoints yet

### Slide 9: Next Steps
- Add async support for better concurrency
- Implement proper logging and monitoring
- Add integration tests with real database

---

## Demo Plan

### Setup (Before class)
```bash
# Ensure repo is at latest commit
git pull origin main

# Install dependencies
pip install -r requirements.txt

# Start the API
python run.py

# In another terminal, run tests
pytest -v
```

### 1) 30-second intro
- What problem we solve: Product catalog management API
- Who uses it: E-commerce platforms, inventory systems

### 2) Architecture (60 seconds)
- Tiers: Presentation (client) → Application (Flask) → Data (SQLite/PostgreSQL)
- Key dependencies: Flask, SQLAlchemy, PyJWT
- Where auth happens: JWT tokens validated on protected endpoints

### 3) Happy path (2 minutes)
- Endpoint: POST `/products` with valid payload
- Expected output: 201 Created with product data
- Show logs for requestId: Check console output

### 4) Failure path (1 minute)
- What you break: Stop DB / invalid token / missing fields
- Expected behavior: 503/401/400 with descriptive error messages
- Show how observability helps: `/ready` endpoint reflects DB state

### 5) Recovery (30 seconds)
- Restart dependency: `docker compose restart db`
- Show system returns to healthy: `curl /ready` returns 200

### 6) Closing (30 seconds)
- Top tradeoff: Simplicity over scalability for demo scope
- Biggest remaining risk: No automatic retry logic for DB connections
- Next steps: Add connection pooling and circuit breaker pattern

---

## Defense Q&A — Likely Questions + Answers

**Q1: What are the tiers and responsibilities?**  
A: Three tiers — Presentation (client/browser), Application (Flask API with business logic), Data (SQLite/PostgreSQL for persistence). Each tier has a single responsibility.

**Q2: Where are security boundaries?**  
A: Authentication at the API layer via JWT; input validation on all mutation endpoints; CORS configured for trusted origins; database credentials isolated in environment variables.

**Q3: How do you handle failures?**  
A: Graceful degradation — `/ready` returns 503 when DB is down; error handlers catch unhandled exceptions and return structured JSON errors; connection timeouts prevent hangs.

**Q4: What is your rollback plan?**  
A: Docker Compose makes it easy to roll back — `docker compose down && docker compose up` restores previous state. Database migrations are versioned for schema rollbacks.

**Q5: What technical debt remains and why?**  
A: Secret key is hardcoded (demo convenience); no rate limiting (not critical for grading scope); JWT validation not enforced on all endpoints (planned for next iteration).

**Q6: Why did you choose Flask over FastAPI?**  
A: Flask has broader ecosystem support and more learning resources. FastAPI would be a good choice for async-heavy workloads, but our current workload is I/O bound with simple queries.

**Q7: How would you scale this system?**  
A: Horizontal scaling with load balancer; stateless API servers behind a reverse proxy; database read replicas for read-heavy workloads; connection pooling for DB efficiency.

**Q8: What happens if two users update the same product simultaneously?**  
A: Currently last-write-wins. We'd add optimistic locking with a version column or use database transactions with conflict detection.

**Q9: How do you ensure data consistency?**  
A: SQLAlchemy ORM handles transaction management; `db.session.commit()` ensures atomic writes; rollback on exceptions prevents partial updates.

**Q10: Why SQLite for development, PostgreSQL for production?**  
A: SQLite requires zero configuration — ideal for local development. PostgreSQL offers better concurrency, advanced features (JSONB, full-text search), and is production-ready.
