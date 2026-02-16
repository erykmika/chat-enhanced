FROM python:3.13-slim

EXPOSE 8000

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Ensure we run from the project root so `backend` is importable.
WORKDIR /app

# Install deps first for better layer caching.
COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend package into the image (keep /app as import root).
COPY backend/ /app/backend/

ENV PYTHONUNBUFFERED=1

# Serve the Flask app via gunicorn. Use the fully-qualified module path.
CMD ["gunicorn", "-b", "0.0.0.0:8000", "backend.webapp.app:app", "--workers", "1"]
