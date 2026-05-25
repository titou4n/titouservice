# TitouService

![Python](https://img.shields.io/badge/Python-3.12-blue)
![Flask](https://img.shields.io/badge/Flask-Web%20Framework-000000)
![SQLite](https://img.shields.io/badge/SQLite-Database-lightgrey)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED)
![Nginx](https://img.shields.io/badge/Nginx-Reverse%20Proxy-009639)
![License](https://img.shields.io/badge/License-MIT-green)

Une plateforme web multi-modules construite avec **Flask** et orchestrée par **Docker Compose**. TitouService propose une suite complète de services intégrés : authentification sécurisée, réseau social, gestion bancaire, suivi de projets, salle de chat, recherche de films et bien plus.

**🌐 Instance en ligne** : [https://titouservice.ltjs.net](https://titouservice.ltjs.net)

---

## 📋 Table des matières

- [Fonctionnalités](#-fonctionnalités)
- [Architecture](#-architecture)
- [Stack technologique](#-stack-technologique)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Utilisation](#-utilisation)
- [Structure du projet](#-structure-du-projet)
- [Développement](#-développement)
- [Sécurité](#-sécurité)
- [Dépannage](#-dépannage)
- [Licence](#-licence)

---

## ✨ Fonctionnalités

### Core
- **🔐 Authentification avancée** — Gestion sécurisée des comptes, sessions persistantes, 2FA
- **👤 Gestion des utilisateurs** — Profils, rôles, permissions granulaires, gestion des droits
- **⚙️ Panneau d'administration** — Gestion complète des utilisateurs, rôles et permissions
- **📝 Paramètres utilisateur** — Profils personnalisables, préférences, images de profil

### Social & Communication
- **🤝 Réseau social** — Feed, publications, interactions entre utilisateurs
- **💬 Salle de chat** — Communication temps réel entre utilisateurs
- **📞 Informations d'urgence** — Gestion des contacts et informations d'urgence personnelles

### Finance & Gamification
- **🏦 Module bancaire** — Simulation bancaire avec comptes virtuels et transactions
- **📈 Marché boursier** — Intégration API Twelve Data pour données financières en temps réel
- **💰 Portefeuille virtuel** — Gestion d'actifs et investissements simulés

### Productivité
- **✅ Suivi de tâches (Job Tracker)** — Gestion des projets et tâches avec base de données dédiée
- **🎬 Recherche de films** — Intégration OMDB API pour consulter infos films/séries

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│           Client Web (Navigateur)               │
└────────────────────┬────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────┐
│    Nginx (Reverse Proxy - Port 80/443)         │
└────────────────────┬────────────────────────────┘
                     │
        ┌────────────┘
        ▼
┌─────────────────────────────────────────────────┐
│   Flask Application (Port 5000)                 │
│   ┌─────────────────────────────────────────┐   │
│   │  Blueprints Modulaires                  │   │
│   │  - Auth, Admin, Settings                │   │
│   │  - Bank, Movie, Social, Chatroom        │   │
│   │  - Job Tracker, Emergency Info          │   │
│   └─────────────────────────────────────────┘   │
└────────────────────┬────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        ▼                         ▼
┌──────────────────┐     ┌──────────────────┐
│  SQLite Main DB  │     │  SQLite Job DB   │
│  (database.db)   │     │  (job_tracker)   │
└──────────────────┘     └──────────────────┘
```

### Composants

| Service | Rôle | Port |
|---------|------|------|
| **Nginx** | Reverse proxy, serveur web | 80 (HTTP) |
| **Flask** | Application principale | 5000 (interne) |
| **SQLite (Main)** | Base de données principale | - |
| **SQLite (Job)** | Base de données dédiée Job Tracker | - |

---

## 🛠️ Stack technologique

| Catégorie | Technologies |
|-----------|--------------|
| **Backend** | Python 3.12, Flask 2.3+ |
| **Bases de données** | SQLite |
| **Frontend** | HTML, CSS, Jinja2 |
| **Serveur** | Gunicorn 22+, Nginx |
| **Authentification** | Flask-Login, Flask-Session |
| **Sécurité** | Flask-WTF (CSRF), Rate Limiting |
| **APIs externes** | OMDB, Twelve Data |
| **Containerisation** | Docker, Docker Compose |

---

## 📦 Installation

### Prérequis

- Docker 20.10+
- Docker Compose 2.0+

### Démarrage rapide

1. **Cloner le dépôt**

```bash
git clone https://github.com/titou4n/titouservice.git
cd titouservice
```

2. **Créer les secrets**

Créez un dossier `secrets/` à la racine du projet avec les fichiers suivants :

```
secrets/
├── secret_key.txt              # Clé secrète Flask (chaîne aléatoire sécurisée)
├── username_super_admin.txt    # Identifiant admin initial
├── password_super_admin.txt    # Mot de passe admin initial
├── omdb_api_key.txt            # Clé API OMDB (https://www.omdbapi.com)
├── twelvedata_api_key.txt      # Clé API Twelve Data (https://twelvedata.com)
└── email_app_password.txt      # Mot de passe email Gmail (App Password)
```

**Exemple de création** :

```bash
mkdir -p secrets

# Générer une clé secrète sécurisée
python3 -c "import secrets; print(secrets.token_hex(32))" > secrets/secret_key.txt

# Ajouter les autres secrets
echo "admin_username" > secrets/username_super_admin.txt
echo "admin_password_secure" > secrets/password_super_admin.txt
echo "your-omdb-api-key" > secrets/omdb_api_key.txt
echo "your-twelvedata-api-key" > secrets/twelvedata_api_key.txt
echo "your-gmail-app-password" > secrets/email_app_password.txt
```

> ⚠️ **Important** : Ne jamais versionner le dossier `secrets/`. Il est inclus dans `.gitignore`.

3. **Lancer l'application**

```bash
docker-compose up --build
```

L'application est accessible à : **http://localhost**

---

## ⚙️ Configuration

### Variables d'environnement

Les variables sensibles sont lues depuis les fichiers secrets Docker :

```bash
# En production
ENV_PROD=true
FLASK_ENV=production

# En développement (via .env)
ENV_PROD=false
FLASK_ENV=development
```

### Configuration de la base de données

Deux bases SQLite sont utilisées :
- **database.db** — Données principales (utilisateurs, social, etc.)
- **database_job_tracker.db** — Données du module Job Tracker

Les bases sont stockées dans le volume Docker `db-data`, persisté entre redémarrages.

### Configuration des sessions

Les sessions utilisateur sont stockées sur le système de fichiers (configurable dans `config.py`).

**Paramètres clés** :
- Durée de session : 1 heure
- Secure cookies en production (HTTPS)
- HttpOnly : oui (protection contre accès JavaScript)
- SameSite : Lax

---

## 🎯 Utilisation

### Authentification

1. **Créer un compte** — Inscription via le formulaire d'inscription
2. **Se connecter** — Authentification avec identifiant/mot de passe
3. **Deux facteurs (2FA)** — Activation en paramètres pour sécurité renforcée

### Modules disponibles

#### 📊 **Admin Panel** (`/admin_panel`)
- Gestion des utilisateurs et rôles
- Attribution de permissions
- Consultation des logs

#### 🤝 **Réseau Social** (`/social_network`)
- Créer/consulter publications
- Interagir avec d'autres utilisateurs
- Suivre des profils

#### 💬 **Chatroom** (`/chatroom`)
- Conversations multiples
- Messages persistants

#### 🏦 **Module Bancaire** (`/bank`)
- Comptes virtuels
- Transactions simulées
- Consultation de soldes

#### 📈 **Données Financières** (intégré dans Bank)
- Cotations boursières en temps réel (Twelve Data API)
- Simulation de portefeuille

#### ✅ **Job Tracker** (`/job_tracker`)
- Création et suivi de tâches
- Organisation par projets
- Base de données dédiée

#### 🎬 **Recherche de films** (`/movie_information`)
- Rechercher films/séries via OMDB
- Consulter détails et critiques

#### ⚙️ **Paramètres** (`/settings`)
- Personnalisation du profil
- Gestion des photos de profil
- Préférences utilisateur

#### 📞 **Informations d'urgence** (`/emergency_information`)
- Ajouter contacts d'urgence
- Partager infos de santé personnelles
- Accès par lien public sécurisé

---

## 📂 Structure du projet

```
titouservice/
├── flask/                           # Application Flask
│   ├── app.py                       # Factory Flask
│   ├── config.py                    # Configuration centralisée
│   ├── extensions.py                # Extensions Flask
│   ├── init_db.py                   # Initialisation base de données
│   │
│   ├── blueprints/                  # Modules
│   │   ├── auth/                    # Authentification
│   │   ├── admin/                   # Admin panel
│   │   ├── settings/                # Paramètres utilisateur
│   │   ├── bank/                    # Module bancaire
│   │   ├── social_network/          # Réseau social
│   │   ├── chatroom/                # Salle de chat
│   │   ├── job_tracker/             # Suivi de tâches
│   │   ├── movie_information/       # Recherche films
│   │   ├── emergency_information/   # Infos d'urgence
│   │   └── main/                    # Accueil
│   │
│   ├── models/                      # Modèles de données
│   │   ├── user.py
│   │   ├── candidature.py
│   │   ├── entreprise.py
│   │   └── emergency_information.py
│   │
│   ├── Data/                        # Couche données
│   │   ├── connection.py            # Connexion DB
│   │   ├── database_manager.py      # Gestion DB
│   │   ├── schema/                  # Schémas de table
│   │   ├── repositories/            # Repos. de données
│   │   └── seeders/                 # Données de test
│   │
│   ├── utils/                       # Utilitaires
│   │   ├── decorators.py            # Décorateurs
│   │   ├── email_manager.py         # Envoi emails
│   │   ├── bank_manager.py          # Logique bancaire
│   │   ├── session_manager.py       # Gestion sessions
│   │   ├── twofa_manager.py         # Authentification 2FA
│   │   ├── stock_market_manager.py  # Marché boursier
│   │   └── twelvedata_manager.py    # API Twelve Data
│   │
│   ├── templates/                   # Templates Jinja2
│   ├── static/                      # CSS, JS, images
│   │   ├── css/
│   │   ├── js/
│   │   ├── img/
│   │   └── uploads/
│   │
│   ├── requirements.txt             # Dépendances Python
│   ├── Dockerfile                   # Image Docker Flask
│   └── entrypoint.sh                # Script démarrage
│
├── nginx/                           # Configuration Nginx
│   ├── conf/
│   └── Dockerfile
│
├── docker-compose.yml               # Orchestration
├── Dockerfile                       # (Inutilisé - voir flask/)
├── Makefile                         # Commandes utiles
├── .gitignore
├── LICENSE
└── README.md                        # Ce fichier
```

---

## 👨‍💻 Développement

### Démarrer en mode développement

```bash
# Modifier config.py : ENV_PROD = False
# Créer un fichier .env à la racine flask/
cat > flask/.env << EOF
SECRET_KEY=your-secret-key-dev
USERNAME_SUPER_ADMIN=admin
PASSWORD_SUPER_ADMIN=admin
OMDB_API_KEY=your-key
TWELVEDATA_API_KEY=your-key
EMAIL_APP_PASSWORD=your-password
DEBUG=true
EOF

# Lancer sans Docker
cd flask
pip install -r requirements.txt
python app.py
```

L'application écoute sur `http://127.0.0.1:8080`

### Ajouter un nouveau module

1. Créer un dossier dans `blueprints/`
2. Créer les fichiers :
   - `__init__.py` (blueprint)
   - `routes.py` (endpoints)
   - `services.py` (logique métier)

3. Importer et enregistrer dans `app.py` :

```python
from blueprints.mymodule.routes import bp as mymodule_bp
app.register_blueprint(mymodule_bp, url_prefix='/mymodule')
```

### Réinitialiser la base de données

```bash
# En développement
rm flask/Data/db/database.db
python flask/init_db.py

# En production (via Docker)
docker-compose down -v
docker-compose up --build
```

### Logs et débogage

```bash
# Logs Flask
docker-compose logs -f flask

# Logs Nginx
docker-compose logs -f nginx

# Tous les logs
docker-compose logs -f
```

---

## 🔒 Sécurité

### Points importants

- ✅ **Secrets sécurisés** — Stockés via Docker Secrets, jamais versionés
- ✅ **CSRF protection** — Flask-WTF pour tous les formulaires
- ✅ **Sessions sécurisées** — HttpOnly, Secure (production), SameSite
- ✅ **Rate limiting** — Limitation des appels API
- ✅ **Authentification 2FA** — Support TOTP intégré
- ✅ **Permissions granulaires** — Contrôle d'accès par rôles

### Recommandations production

- ⚠️ Utiliser **HTTPS** (certificats Let's Encrypt)
- ⚠️ Gérer les secrets via **Docker Secrets** ou variables d'environnement sécurisées
- ⚠️ Utiliser une base de données **production-grade** (PostgreSQL) au lieu de SQLite
- ⚠️ Mettre en place un **monitoring** (logs, alertes)
- ⚠️ Configurer une **stratégie de sauvegarde** des données
- ⚠️ Garder les dépendances à jour

---

## 🐛 Dépannage

### Application n'écoute pas sur le port 80

Vérifier que le port 80 est disponible :

```bash
netstat -ano | findstr :80  # Windows
sudo lsof -i :80             # Linux/Mac
```

### Erreur "SECRET_KEY is missing"

Créer le fichier `secrets/secret_key.txt` :

```bash
python3 -c "import secrets; print(secrets.token_hex(32))" > secrets/secret_key.txt
```

### Problèmes de volume Docker

```bash
# Vérifier les volumes
docker volume ls

# Supprimer le volume et recommencer
docker-compose down -v
docker-compose up --build
```

### Connexion à la base de données

Les bases SQLite sont dans le volume `db-data`. Pour les consulter :

```bash
# Copier depuis le conteneur
docker-compose exec flask sqlite3 /app/Data/db/database.db

# Ou depuis l'hôte (une fois extraites)
sqlite3 /path/to/db-data/database.db
```

---

## 📄 Licence

Projet personnel — Titouan SIMON

Voir le fichier [LICENSE](LICENSE) pour les détails.

---

## 📞 Support

Pour les questions, bugs ou suggestions :
- Créer une **issue** sur le dépôt GitHub
- Contacter le développeur

---

**Dernière mise à jour** : 2026-05-26
