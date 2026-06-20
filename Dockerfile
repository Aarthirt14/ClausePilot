# syntax=docker/dockerfile:1
FROM python:3.11-slim AS base

# System deps for pdfplumber (relies on pillow) and matplotlib.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libfreetype6-dev \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install deps first so this layer is cached across code-only changes.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Production-only image: install gunicorn for serving (the Flask dev
# server used by `app.py` directly is not meant for production traffic).
RUN pip install --no-cache-dir gunicorn~=22.0

COPY . .

# Uploaded contracts and evaluation artifacts live outside the image.
RUN mkdir -p uploads evaluation

ENV FLASK_DEBUG=0 \
    FLASK_HOST=0.0.0.0 \
    FLASK_PORT=5000 \
    PYTHONUNBUFFERED=1

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s \
    CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://localhost:5000/healthz').status in (200,503) else 1)"

# gunicorn, not the Flask dev server: multiple workers, no debugger,
# production-grade request handling. Each worker loads its own model
# copy on first request (see src/inference.py's per-process cache).
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "120", "app:app"]
