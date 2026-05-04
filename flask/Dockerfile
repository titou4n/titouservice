FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Dépendances système
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Code
COPY . .

# Permissions
RUN chmod +x entrypoint.sh

EXPOSE 5000

# PRODUCTION SERVER
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:create_app()"]