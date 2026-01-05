FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY backend/requirements.txt ./backend/

# Install Python dependencies
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy application code maintaining structure
COPY backend/ ./backend/

# Create directories for cache and logs
RUN mkdir -p /app/backend/cache /app/backend/logs

# Set Python path to include /app so 'backend' module can be imported
ENV PYTHONPATH=/app

# Expose port (internal network only)
EXPOSE 8000

# Run application
# Note: Host 0.0.0.0 allows Docker network access, but port is NOT exposed to host
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]


