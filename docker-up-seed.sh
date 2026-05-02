#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

if [[ ! -f .env ]] && [[ -f .env.example ]]; then
  cp .env.example .env
  echo "Created .env from .env.example"
fi

echo "Starting Docker Compose..."
docker compose up --build -d

echo "Waiting for http://127.0.0.1:5000/ready ..."
max_attempts=45
attempt=0
until curl -sf http://127.0.0.1:5000/ready >/dev/null 2>&1; do
  attempt=$((attempt + 1))
  if [[ $attempt -ge $max_attempts ]]; then
    echo "Timed out waiting for readiness. Recent app logs:"
    docker compose logs --tail 80 ecommerce-lite
    exit 1
  fi
  sleep 2
done

echo "Seeding demo data..."
docker compose exec -T ecommerce-lite python seed.py

echo ""
echo "App: http://127.0.0.1:5000/"
echo "Follow logs: docker compose logs -f"
echo "Stop stack: docker compose down"
