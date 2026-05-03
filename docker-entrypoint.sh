#!/bin/sh
set -e

# Wait for PostgreSQL to be ready
echo "Waiting for database..."
until python -c "
import psycopg2
try:
    conn = psycopg2.connect(
        dbname='${POSTGRES_DB:-ecommerce}',
        user='${POSTGRES_USER:-ecommerce_user}',
        password='${POSTGRES_PASSWORD:-ecommerce_pass}',
        host='db',
        port=5432
    )
    conn.close()
    print('Database is ready.')
except Exception:
    pass
"; do
    sleep 1
done

# Run Alembic migrations (or fall back to create_all if no alembic.ini)
if [ -f "alembic.ini" ]; then
    echo "Running Alembic migrations..."
    alembic upgrade head || echo "Alembic failed, falling back to create_all"
    python -c "
from app import create_app, db
app = create_app()
with app.app_context():
    db.create_all()
"
else
    echo "No alembic.ini found, using db.create_all()"
    python -c "
from app import create_app, db
app = create_app()
with app.app_context():
    db.create_all()
"
fi

echo "Database tables ensured."
exec "$@"
