#!/bin/sh
set -eu

db_wait_attempt=1
db_wait_max_attempts="${DB_WAIT_MAX_ATTEMPTS:-30}"
db_wait_delay="${DB_WAIT_DELAY_SECONDS:-2}"

until python -m app.wait_for_database; do
  if [ "$db_wait_attempt" -ge "$db_wait_max_attempts" ]; then
    echo "Database did not become available after ${db_wait_max_attempts} attempts." >&2
    exit 1
  fi

  echo "Database is not available yet; retrying in ${db_wait_delay}s..." >&2
  db_wait_attempt=$((db_wait_attempt + 1))
  sleep "$db_wait_delay"
done

if [ "${RUN_MIGRATIONS:-true}" = "true" ]; then
  alembic upgrade head
fi

if [ "${SEED_DEMO_DATA:-false}" = "true" ]; then
  python -m app.seed
fi

exec uvicorn app.main:app --host 0.0.0.0 --port 8000
