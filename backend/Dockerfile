FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port (Render sets PORT dynamically)
EXPOSE 8000

# Run with uvicorn — Render injects $PORT
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
