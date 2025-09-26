#!/bin/bash
# Production startup script for Render deployment

echo "🚀 Starting SEO AutoPilot for production deployment..."

# Set environment variables for production
export PYTHONPATH=/opt/render/project/src
export FLASK_ENV=production

# Use the PORT environment variable provided by Render
if [ -z "$PORT" ]; then
    export SEO_ANALYZER_PORT=5000
else
    export SEO_ANALYZER_PORT=$PORT
fi

echo "📡 Server will start on port: $SEO_ANALYZER_PORT"

# Verify Python environment
echo "🐍 Python version: $(python --version)"
echo "📦 pip version: $(pip --version)"

# Install package in production mode
pip install -e .

# Start the application
echo "🎯 Starting SEO AutoPilot API server..."
exec python -m pyseoanalyzer.api