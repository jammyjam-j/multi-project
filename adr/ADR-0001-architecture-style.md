# ADR-0001: Use a Three-Tier Modular Monolith

## Status

Accepted

## Context

The current course project is an E-commerce Lite application with:

- a browser frontend built with vanilla JavaScript
- a Flask backend that serves both the frontend shell and the REST API
- a SQLite database accessed through SQLAlchemy

Course constraints matter here:

- the app must be easy to run locally and in Docker Compose
- the team must be able to explain the architecture during defense
- the project needs clear frontend/backend/data separation
- the system is small enough that microservice overhead would dominate the value

The final objective also allows a modular monolith as the recommended Week 8 path.

## Decision

We use a three-tier modular monolith:

- presentation tier: static frontend assets served by Flask
- application tier: Flask app with versioned REST endpoints under `/api/v1`
- data tier: SQLite with SQLAlchemy models and relationships

Within the Flask application, responsibilities are split into modules:

- route modules for HTTP concerns
- service modules for application logic
- model definitions for persistence
- shared auth, validation, and caching helpers

This keeps the deployment to one app container while still giving the codebase clear internal boundaries.

## Consequences

### Benefits

- simpler local setup and demo flow
- one deployable unit for Docker and Compose
- fewer moving parts during debugging
- easier for students to explain than service discovery, inter-service auth, and distributed data ownership
- enough structure to satisfy the course architecture requirements

### Drawbacks

- no independent scaling of modules
- module boundaries depend on team discipline rather than process boundaries
- frontend and API are coupled to the same deployment unit
- SQLite is a practical demo choice, not a scalability strategy

## Alternatives considered

### Microservices

Rejected for current scope.

Why:

- would add network boundaries, failure handling, and deployment complexity that the current app does not need
- would make the project harder to defend if the codebase does not genuinely benefit from the split

### Single-file or weakly structured monolith

Rejected.

Why:

- harder to test, explain, and evolve
- encourages mixing routes, business logic, and persistence concerns

### Separate frontend server plus backend API server

Deferred.

Why:

- the project already meets the multi-tier requirement without separate deployment units
- serving the frontend from Flask keeps the setup reproducible for grading and demos

## Follow-up

- keep internal boundaries documented in `architecture.md`
- continue moving business rules into service modules where practical
- revisit database and deployment choices only if the project scope grows beyond demo scale
