# Production Dockerfile for SEO AutoPilot - Render Optimized
FROM python:3.9-slim

# Set environment variables for production
ENV PYTHONPATH=/app
ENV FLASK_ENV=production
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Install the package in production mode
RUN pip install .

# Create non-root user for security
RUN groupadd -r appgroup && useradd --no-log-init -r -g appgroup appuser
RUN chown -R appuser:appgroup /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT:-5000}/api/health || exit 1

# Start the web server (Render will set PORT environment variable)
CMD python -m pyseoanalyzer.api
