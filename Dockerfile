# AIQUAA AI Analysis MS - Production Dockerfile
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements first for better layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p logs data

# Copy startup script
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

# Set Python path
ENV PYTHONPATH=/app

# Expose port
EXPOSE 8000

# Health check (disabled for Railway - will use Railway's healthcheck)
# HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
#     CMD python -c "import httpx; httpx.get('http://localhost:${PORT:-8000}/api/v1/salud').raise_for_status()"

# Run application using startup script
CMD ["/app/start.sh"]
