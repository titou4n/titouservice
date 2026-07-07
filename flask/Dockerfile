FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

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

# Non-root user. Data/db/ and static/uploads/ are excluded from the build
# context by .dockerignore (they're populated at runtime / mounted as a
# volume), so they're created here explicitly with the right ownership
# *before* USER switches away from root - Docker Compose's db-data volume
# copies this directory's existing ownership into the volume on first
# mount, so appuser keeps write access after the volume is attached.
#RUN useradd --create-home --uid 1000 appuser \
#    && mkdir -p Data/db static/uploads/profile_pictures \
#    && chmod +x entrypoint.sh \
#    && chown -R appuser:appuser /app

#USER appuser

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

EXPOSE 5000

# Use entrypoint instead of CMD
ENTRYPOINT ["./entrypoint.sh"]