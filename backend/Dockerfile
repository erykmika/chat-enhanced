FROM python:3.13-slim

EXPOSE 8000

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Ensure we run from the project root so `backend` is importable.
WORKDIR /app

COPY pyproject.toml ./pyproject.toml
COPY README.md ./README.md

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir build \
    && python -m build --wheel --outdir /tmp/dist \
    && pip install --no-cache-dir /tmp/dist/*.whl \
    && rm -rf /tmp/dist

# Copy backend package into the image (keep /app as import root).
COPY backend/ /app/backend/

ENV PYTHONUNBUFFERED=1

# Serve the Flask app via gunicorn. Use the fully-qualified module path.
CMD ["gunicorn", "-b", "0.0.0.0:8000", "backend.webapp.app:app", "--workers", "1"]
