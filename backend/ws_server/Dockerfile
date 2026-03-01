FROM python:3.13-slim

EXPOSE 8001

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml ./pyproject.toml
COPY README.md ./README.md
COPY backend/ ./backend/

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir build \
    && python -m build --wheel --outdir /tmp/dist \
    && pip install --no-cache-dir /tmp/dist/*.whl \
    && rm -rf /tmp/dist

ENV PYTHONUNBUFFERED=1

CMD ["python", "-m", "backend.ws_server.server"]

