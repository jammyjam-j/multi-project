# ADR-0001: Architecture Style

## Status

Accepted

## Context

The project needed:

- a frontend
- a backend API
- a database layer
- something simple enough to run and explain in class

The app is not large, and splitting it into services would have added extra setup and extra failure cases to explain.

## Decision

I used one Flask app with internal modules instead of microservices.

The app still keeps frontend, API, and data concerns separate:

- frontend files in `app/static/js/` and `app/templates/`
- API routes in `app/api/`
- business logic in `app/services/`
- persistence in `models.py`

## Why

- easier to build in the time available
- easier to run locally and in Docker Compose
- easier to present during defense

## Downsides

- everything is deployed together
- module boundaries depend on code discipline
- it would be harder to scale pieces separately

## Alternatives considered

### Microservices

I did not choose this because the project was too small to justify the extra complexity.

### Looser monolith

I also did not want everything mixed into a few large files, because that would be harder to test and explain.
