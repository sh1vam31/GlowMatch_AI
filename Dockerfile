# Use Python 3.11 lightweight base image
FROM python:3.11-slim

WORKDIR /app

# Set environment variables for Render deployment
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV OMP_NUM_THREADS=1
ENV MKL_NUM_THREADS=1
ENV OPENBLAS_NUM_THREADS=1
ENV PORT=10000

# Install essential system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt-get/lists/*

COPY requirements.txt .

# Install CPU-only PyTorch to save ~400MB RAM before installing other dependencies
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

# Expose port 10000
EXPOSE 10000

# Run Uvicorn server bound to 0.0.0.0 and PORT (Render port 10000)
CMD exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-10000}
