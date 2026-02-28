FROM python:3.13-slim

EXPOSE 8000

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Ensure we run from the project root so `backend` is importable.
WORKDIR /app

COPY pyproject.toml ./pyproject.toml
COPY README.md ./README.md

# Alembic config is stored at repo root and used by the entrypoint.
COPY alembic.ini ./alembic.ini

# The wheel build needs the package sources present.
COPY backend/ ./backend/

# Copy entrypoint that runs Alembic migrations (optional) before starting the app.
COPY backend/docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir build \
    && python -m build --wheel --outdir /tmp/dist \
    && pip install --no-cache-dir /tmp/dist/*.whl \
    && rm -rf /tmp/dist

ENV PYTHONUNBUFFERED=1

ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]

# Serve the Flask app via gunicorn. Use the fully-qualified module path.
CMD ["gunicorn", "-b", "0.0.0.0:8000", "backend.webapp.app:app", "--workers", "1"]
