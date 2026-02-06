# ============================================================================
# Pi Command Center - Telegram Bot
# ============================================================================
# Multi-stage build for minimal image size
# Supports ARM64 (Raspberry Pi) and AMD64 (development)
# ============================================================================

# Stage 1: Builder
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim

LABEL maintainer="judariva"
LABEL description="Pi Command Center - Telegram Bot for home network control"
LABEL version="1.0.0"

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    nmap \
    arp-scan \
    wakeonlan \
    iputils-ping \
    dnsutils \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy application code
COPY config.py .
COPY main.py .
COPY monitor.py .
COPY handlers/ handlers/
COPY services/ services/
COPY keyboards/ keyboards/
COPY utils/ utils/

# Create non-root user
RUN useradd -m -u 1000 pibot && \
    chown -R pibot:pibot /app

# Create data directory
RUN mkdir -p /app/data && chown pibot:pibot /app/data

# Environment
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Switch to non-root user
USER pibot

# Health check
HEALTHCHECK --interval=60s --timeout=15s --start-period=30s --retries=3 \
    CMD python -c "import requests; requests.get('https://api.telegram.org', timeout=10)" || exit 1

# Run
CMD ["python", "main.py"]
