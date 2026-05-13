# Use a slim Python base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for Docker layer caching
COPY backend/requirements.txt .

# Install Python dependencies (CPU-only torch to save space/memory)
RUN pip install --no-cache-dir \
    --extra-index-url https://download.pytorch.org/whl/cpu \
    -r requirements.txt

# Copy all backend code
COPY backend/ ./backend/

# Create the database directory
RUN mkdir -p /app/database

# Expose port (Railway will provide $PORT, we default to 8000)
ENV PORT=8000
EXPOSE $PORT

# Start the FastAPI app (Shell form allows $PORT expansion)
CMD uvicorn backend.app:app --host 0.0.0.0 --port $PORT
