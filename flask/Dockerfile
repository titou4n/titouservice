FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Create user no-root
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# System dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Entry point permissions
RUN chmod +x entrypoint.sh

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Utiliser l'utilisateur non-root
USER appuser

EXPOSE 5000

# Use entrypoint instead of CMD
ENTRYPOINT ["./entrypoint.sh"]