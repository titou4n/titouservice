FROM python:3.12-slim

# Variables d'environnement
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=app.py
#ENV FLASK_ENV=production
ENV FLASK_ENV=development
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5000

# Définir le répertoire de travail
WORKDIR /app

# Dépendances système minimales
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Installer les dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le reste de l'application
COPY . /app

# Permissions (simple)
RUN chmod +x entrypoint.sh

# Exposer le port interne Flask
EXPOSE 5000

# Lancer l'app
ENTRYPOINT ["./entrypoint.sh"]