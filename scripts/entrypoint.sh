#!/bin/sh
set -e

echo "Waiting for PostgreSQL..."
until python -c "
from sqlalchemy import create_engine, text
from app.config import settings
engine = create_engine(settings.database_url)
with engine.connect() as conn:
    conn.execute(text('SELECT 1'))
" 2>/dev/null; do
  sleep 1
done

echo "Running migrations..."
alembic upgrade head

echo "Starting application..."
exec "$@"
