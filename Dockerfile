# syntax=docker/dockerfile:1
FROM python:3.11-slim

# Install system dependencies:
# - ffmpeg: Required for VP9 WebM video sticker generation
# - libwebp & demux: Required for Pillow WebP animated frame decoding
# - curl: Required for healthcheck and entrypoint validation
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libwebp7 \
    libwebpmux3 \
    libwebpdemux2 \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code and scripts
COPY signer_server.py .
COPY app/ ./app/
COPY bot.py .
COPY entrypoint.sh .

RUN chmod +x entrypoint.sh

# Environment defaults for Render
ENV PORT=10000
ENV HOST=0.0.0.0
ENV PYTHONUNBUFFERED=1

EXPOSE 10000

# Container-level healthcheck against FastAPI health endpoint
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
  CMD curl -f http://localhost:${PORT}/health || exit 1

ENTRYPOINT ["/app/entrypoint.sh"]
