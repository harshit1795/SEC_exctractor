FROM python:3.13-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH /app

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Ensure data files are in expected locations (if they are in parent dir, you might need to copy them explicitly)
# Based on current structure, fundamentals_tall.parquet is inside finq-backend
# If secedgarticker.json is needed, ensure it is copied as well

# Expose port
EXPOSE 8000

# Run uvicorn
CMD sh -c "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"
