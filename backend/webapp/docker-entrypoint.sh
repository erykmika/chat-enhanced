#!/bin/sh
set -eu

: "${RUN_MIGRATIONS:=1}"

if [ "${RUN_MIGRATIONS}" != "0" ]; then
  echo "[entrypoint] Running Alembic migrations..."
  alembic -c /app/alembic.ini upgrade head
  echo "[entrypoint] Migrations complete."
else
  echo "[entrypoint] RUN_MIGRATIONS=0, skipping migrations."
fi

exec "$@"

