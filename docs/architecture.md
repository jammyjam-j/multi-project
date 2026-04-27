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
│  Auth: JWT (PyJWT)                                           │
└─────────────────────────────────────────────────────────────┘
              │ SQL/SQLite
              ▼
┌─────────────────────────────────────────────────────────────┐
│                      Database                                │
│  Tables: products, users                                     │
│  Driver: SQLAlchemy ORM                                      │
└─────────────────────────────────────────────────────────────┘
```

## Container View

```
┌─────────────────────────────────────────────────────────────┐
│                        Docker Compose                        │
│                                                               │
│  ┌─────────────────┐         ┌─────────────────┐            │
│  │   API Container  │────────▶  DB Container    │            │
│  │  (Flask + Python)│         │ (PostgreSQL)    │            │
│  │  Port: 5000      │         │ Port: 5432      │            │
│  └─────────────────┘         └─────────────────┘            │
│                                                               │
│  Local Development: SQLite (file-based)                      │
│  Production: PostgreSQL (container)                          │
└─────────────────────────────────────────────────────────────┘
```

## Tier Responsibilities

| Tier | Component | Responsibility |
|------|-----------|----------------|
| **Presentation** | Client (Browser/Postman) | User interaction, request formatting |
| **Application** | Flask API | Business logic, authentication, validation |
| **Data** | SQLite/PostgreSQL | Persistence, data integrity |

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
