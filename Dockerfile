# Use an official Python runtime as a parent image
# Matching the version from .github/workflows/ci.yml
FROM python:3.10-slim

# Set environment variables to prevent Python from buffering stdout/stderr
# and to prevent creation of .pyc files
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory in the container
WORKDIR /app

# Install system dependencies required for building Python packages
# libpq-dev is often needed for PostgreSQL adapters
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Create a non-root user for security (optional but recommended)
RUN useradd -m appuser && chown -R appuser /app
USER appuser
# Default command to run the pipeline
# Users can override this command (e.g., to run specific scripts)
CMD ["python", "-m","api_server.main"]
