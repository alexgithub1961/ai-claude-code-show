# Multi-stage Dockerfile for VanEck ETF Data Downloader
# This Dockerfile creates an optimized production image for the ETF downloader application

# Stage 1: Build stage
FROM python:3.12-alpine AS builder

# Set build arguments
ARG BUILD_DATE
ARG VERSION=1.0.0
ARG VCS_REF

# Set labels for metadata
LABEL maintainer="VanEck Data Team <data@vaneck.com>"
LABEL org.label-schema.build-date=$BUILD_DATE
LABEL org.label-schema.name="vaneck-etf-downloader"
LABEL org.label-schema.description="ETF Data Downloader for VanEck"
LABEL org.label-schema.version=$VERSION
LABEL org.label-schema.vcs-ref=$VCS_REF
LABEL org.label-schema.schema-version="1.0"

# Install build dependencies
RUN apk add --no-cache \
    gcc \
    musl-dev \
    libffi-dev \
    openssl-dev \
    python3-dev \
    yaml-dev \
    build-base

# Set up Python environment
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# Create application directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt requirements-prod.txt ./

# Install Python dependencies
# Pin setuptools to avoid compatibility issues
RUN pip install --upgrade pip "setuptools<71" wheel && \
    pip install --no-build-isolation -r requirements-prod.txt

# Copy source code
COPY src/ ./src/
COPY config/ ./config/

# Stage 2: Runtime stage
FROM python:3.12-alpine AS runtime

# Install runtime dependencies only
RUN apk add --no-cache \
    ca-certificates \
    tzdata \
    tini

# Create non-root user for security
RUN addgroup -g 1001 -S appgroup && \
    adduser -u 1001 -S appuser -G appgroup -h /app -s /bin/sh

# Set up directories
WORKDIR /app
RUN mkdir -p /app/data /app/logs /app/config && \
    chown -R appuser:appgroup /app

# Copy Python packages from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code from builder
COPY --from=builder --chown=appuser:appgroup /app/src /app/src
COPY --from=builder --chown=appuser:appgroup /app/config /app/config

# Copy additional files
COPY --chown=appuser:appgroup docker-entrypoint.sh /app/
COPY --chown=appuser:appgroup config/config.yaml.example /app/config/

# Make entrypoint script executable
RUN chmod +x /app/docker-entrypoint.sh

# Set Python path
ENV PYTHONPATH="/app:$PYTHONPATH"

# Health check configuration
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import sys; sys.path.insert(0, '/app'); from src.utils.health import check_health; exit(0 if check_health() else 1)"

# Switch to non-root user
USER appuser

# Set default environment variables
ENV DATA_DIR="/app/data"
ENV LOG_LEVEL="INFO"
ENV CONFIG_FILE="/app/config/config.yaml"

# Expose port for health checks (if needed)
EXPOSE 8080

# Use tini as init system
ENTRYPOINT ["/sbin/tini", "--", "/app/docker-entrypoint.sh"]

# Default command
CMD ["python", "src/main.py"]