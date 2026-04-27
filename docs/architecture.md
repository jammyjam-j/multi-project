# Architecture Documentation

## C4 Context Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                       External User                          │
│                  (Browser / Postman / CLI)                   │
└─────────────┬───────────────────────────────────────────────┘
              │ HTTP/REST
              ▼
┌─────────────────────────────────────────────────────────────┐
│                        Flask API                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │  Health BP   │  │   Auth BP   │  │ Products BP │         │
│  │ /health      │  │ /auth/login │  │ /products   │         │
│  │ /ready       │  │             │  │ (CRUD)      │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
│                                                              │
│  Middleware: CORS, Error Handling                            │
│  Auth: JWT (PyJWT) + RBAC (admin/user/viewer)               │
└─────────────────────────────────────────────────────────────┘
              │ SQL/SQLite
              ▼
┌─────────────────────────────────────────────────────────────┐
│                      Database                                │
│  Tables: products, users                                     │
│  Driver: SQLAlchemy ORM                                      │
│  Default: SQLite (file-based)                                │
│  Optional: PostgreSQL (production upgrade)                   │
└─────────────────────────────────────────────────────────────┘
```

## Container View

```
┌─────────────────────────────────────────────────────────────┐
│                        Docker Compose                        │
│                                                               │
│  ┌─────────────────┐                                        │
│  │   API Container  │                                        │
│  │  (Flask + Python)│                                        │
│  │  Port: 5000      │                                        │
│  └─────────────────┘                                        │
│                                                               │
│  Database: SQLite (file-based, mounted volume)               │
│  Production: PostgreSQL via DATABASE_URL environment variable│
└─────────────────────────────────────────────────────────────┘
```

## Tier Responsibilities

| Tier | Component | Responsibility |
|------|-----------|----------------|
| **Presentation** | Client (Browser/Postman) | User interaction, request formatting |
| **Application** | Flask API | Business logic, authentication, validation |
| **Data** | SQLite (default) / PostgreSQL | Persistence, data integrity |

## Key Dependencies
- **Flask**: Web framework (routing, request handling)
- **SQLAlchemy**: ORM for database abstraction
- **PyJWT**: Token-based authentication
- **Flask-CORS**: Cross-origin resource sharing for frontend integration

## Security Boundaries
1. **Authentication**: JWT tokens validate user identity on protected endpoints
2. **Authorization**: Role-based access control (admin/user/viewer)
3. **Input Validation**: Required field checks on product creation/update
4. **CORS**: Configured to allow only trusted origins in production
5. **Secret Management**: SECRET_KEY enforced via environment variable; dev defaults blocked in production

## Deployment Plan
- **Development**: SQLite (file-based, zero configuration)
- **Production**: PostgreSQL — set `DATABASE_URL` environment variable to switch
- Secrets are injected via environment variables or `.env` files — never hardcoded

