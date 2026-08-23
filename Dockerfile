# Use Python 3.11 lightweight base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables for Hugging Face Spaces (Port 7860)
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=7860
ENV HOME=/tmp

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

# Set permissions for Hugging Face container user
RUN chmod -R 777 /app /tmp

# Expose port 7860 required by Hugging Face Spaces
EXPOSE 7860

# Run Uvicorn server bound to 0.0.0.0 and PORT 7860
CMD exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-7860}
