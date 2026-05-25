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

# Production server
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:create_app()"]