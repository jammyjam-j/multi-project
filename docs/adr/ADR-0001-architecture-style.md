# ADR-0001: Architecture Style (Monolith vs Modular vs Microservices)

## Status
Accepted

## Context
- Team size and delivery timeline: 4 students, 10-week semester project
- Expected scope and future growth: Product catalog API with CRUD operations, authentication, and basic reporting
- Constraints (hosting, tooling, skills): Single deployment target (Docker Compose); team familiar with Flask and SQLite/PostgreSQL; limited infrastructure experience

## Decision
We chose: **Modular Monolith**

Reasons:
- Simpler deployment — single container, no service mesh or inter-service networking
- Easier debugging during development — all logs in one place
- Shared database eliminates data consistency issues across services
- Blueprints in Flask provide natural module boundaries (products, auth, health)

## Consequences
Pros:
- Fast iteration — no distributed tracing needed
- Single codebase is easier to onboard new team members
- Lower operational overhead for demo and grading

Cons / risks:
- No independent scaling of modules
- Tight coupling if module boundaries are not respected
- Risk of becoming a "big ball of mud" without discipline

Follow-up actions:
- Enforce import rules between modules (no circular dependencies)
- Document module contracts in README
- Consider extraction to microservices only if traffic patterns demand it

## Alternatives
- **Microservices**: Overkill for current scope; would introduce networking, serialization, and deployment complexity
- **Single-file monolith**: Already too large; blueprints provide necessary structure
- **Serverless (Lambda)**: Not suitable for demo with stateful connections and local database
