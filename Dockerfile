# Use Python 3.11 lightweight base image
FROM python:3.11-slim

# Set working directory inside container
WORKDIR /app

# Prevent Python from writing .pyc files and buffer stdout
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# Install essential system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt-get/lists/*

# Install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code and built static assets
COPY . .

# Expose port 8000
EXPOSE 8000

# Run Uvicorn server bound to 0.0.0.0 and PORT environment variable (for GCP Cloud Run)
CMD exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
