# Architecture Evaluation — Mini-ATAM

## 1. Quality Attribute Scenarios

### Scenario 1 — Performance
**Stimulus**: 50 concurrent users during demo, each fetching product listings  
**Measure**: p95 API latency < 300ms  
**Current Status**: ✅ PASS (SQLite in-memory responds in ~20-50ms for simple queries)  
**Top Risk**: Latency degrades under write-heavy load due to synchronous DB commits blocking the thread  
**Mitigation**: Introduce connection pooling; consider async drivers for read paths  

### Scenario 2 — Availability
**Stimulus**: Database restart during active session  
**Response**: API should return graceful 503 on `/ready` and recover within 30s after DB is back  
**Current Status**: ✅ PASS (readiness check validates DB connection; returns 503 when disconnected)  
**Top Risk**: No automatic retry logic — client must poll `/ready` to detect recovery  
**Mitigation**: Add circuit-breaker pattern with exponential backoff for DB connections  

### Scenario 3 — Security
**Stimulus**: Unauthorized access attempt to protected endpoints  
**Response**: Return 401/403, no data leak, log the event  
**Current Status**: ⚠️ PARTIAL (login returns 401 correctly; JWT validation not yet enforced on product endpoints)  
**Top Risk**: Product endpoints are currently open — no token verification middleware  
**Mitigation**: Add `@jwt_required` decorator to all product mutation endpoints; enforce role-based access control  

---

## 2. Top 3 Risks

| # | Risk | Impact | Likelihood | Mitigation |
|---|------|--------|------------|------------|
| 1 | **Secret key hardcoded in config** | High — credential leakage if repo is public | Medium | Move to environment variables; use `.env` files with `.gitignore` |
| 2 | **No rate limiting** | Medium — API abuse during demo could crash server | High | Add `flask-limiter` with per-endpoint thresholds |
| 3 | **Synchronous DB calls block threads** | Medium — slow queries starve request workers | Medium | Switch to connection pool; consider async SQLAlchemy for reads |

---

## 3. Next Steps

1. **Short-term (Week 10)**: Enforce JWT validation on product endpoints; fix `/ready` semantics ✅
2. **Medium-term**: Add rate limiting and request logging middleware
3. **Long-term**: Migrate to async HTTP server (FastAPI or Quart) for better concurrency
