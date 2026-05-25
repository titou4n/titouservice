FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Permissions
RUN chmod +x entrypoint.sh

EXPOSE 5000

# Production server with gunicorn (accessible only from Docker network)
CMD ["gunicorn", "--workers=4", "--worker-class=sync", "--bind=0.0.0.0:5000", "--timeout=120", "--access-logfile=-", "--error-logfile=-", "app:create_app()"]