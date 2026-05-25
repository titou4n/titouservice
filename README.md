# TitouService

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Flask](https://img.shields.io/badge/Flask-Web%20Framework-black)
![Docker](https://img.shields.io/badge/Docker-Container-blue)
![Nginx](https://img.shields.io/badge/Nginx-Reverse%20Proxy-green)
![SQLite](https://img.shields.io/badge/SQLite-Database-lightgrey)

## À propos

TitouService est une application web moderne permettant la gestion de comptes utilisateurs et la recherche de films. 
Développée avec **Flask**, orchestrée par **Docker Compose** et servie par **Nginx**, elle offre une architecture 
production-ready facilement déployable sur serveur ou NAS.

**Instance en ligne** : [https://titouservice.ltjs.net](https://titouservice.ltjs.net) (auto-hébergée)

---

## Fonctionnalités

- ✅ **Authentification utilisateur** - Gestion sécurisée des comptes et sessions
- ✅ **Recherche de films** - Intégration API externe (OMDB)
- ✅ **Historique utilisateur** - Persistance des données en SQLite
- ✅ **Interface web responsive** - HTML/CSS moderne
- ✅ **Déploiement containerisé** - Docker Compose pour faciliter l’installation

---

## Stack technologique

| Composant | Technologie |
|-----------|------------|
| **Backend** | Python 3.11 + Flask |
| **Frontend** | HTML / CSS |
| **Base de données** | SQLite |
| **Orchestration** | Docker & Docker Compose |
| **Serveur web** | Nginx (Reverse Proxy) |

---

## Architecture

```
┌─────────────────────┐
│   Client Browser    │
└──────────┬──────────┘
           │
           v
┌─────────────────────┐
│  Nginx (Port 8080)  │ ← Reverse Proxy
└──────────┬──────────┘
           │
           v
┌─────────────────────┐
│  Flask Application  │ ← Application Web
└──────────┬──────────┘
           │
           v
┌─────────────────────┐
│   SQLite Database   │ ← Persistance
└─────────────────────┘
```

---

## Démarrage rapide

### Prérequis

- [Docker](https://www.docker.com/get-started)
- [Docker Compose](https://docs.docker.com/compose/install/)

### Installation

1. **Cloner le dépôt**

```bash
git clone https://github.com/titou4n/titouservice.git
cd titouservice
```

2. **Configurer les secrets**

Créez un dossier `secrets/` à la racine du projet et ajoutez les fichiers suivants :

```
secrets/
├── secret_key.txt        # Clé secrète Flask (chaîne aléatoire)
└── omdb_api_key.txt      # Clé API OMDB
```

**Exemple** (ne pas utiliser en production) :

```bash
mkdir -p secrets
echo "your-secret-key-here" > secrets/secret_key.txt
echo "your-omdb-api-key" > secrets/omdb_api_key.txt
```

3. **Démarrer l’application**

```bash
docker-compose up --build
```

4. **Accéder à l’application**

Ouvrez votre navigateur et allez à : [http://localhost:8080](http://localhost:8080)

---

## Utilisation

- **Créer un compte** - Inscription via le formulaire
- **Se connecter** - Authentification avec identifiant/mot de passe
- **Rechercher des films** - Utiliser la barre de recherche alimentée par l’API OMDB
- **Consulter l’historique** - Accès à vos recherches précédentes

---

## Arrêter l’application

```bash
docker-compose down
```

Pour supprimer complètement les conteneurs et volumes :

```bash
docker-compose down -v
```

---

## Développement

### Structure du projet

```
titouservice/
├── app/                    # Application Flask
│   ├── __init__.py
│   ├── models/            # Modèles de données
│   ├── routes/            # Routes et contrôleurs
│   ├── templates/         # Templates HTML
│   └── static/            # Fichiers CSS, JS, images
├── nginx/                 # Configuration Nginx
├── secrets/               # Fichiers de configuration (non versionné)
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

### Modifier l’application

Les modifications sont appliquées en temps réel si vous avez un volume configuré dans Docker.

```bash
docker-compose up --build
```

---

## Sécurité

⚠️ **Points importants** :

- Les clés secrètes sont stockées en fichiers isolés (ne pas les commiter)
- Les identifiants de base de données doivent être protégés en production
- Utilisez toujours HTTPS en environnement de production
- Les variables sensibles sont gérées via des fichiers `secrets/` ou variables d’environnement

---

## Logs et Debugging

Consulter les logs de l’application :

```bash
docker-compose logs -f app
```

Logs Nginx :

```bash
docker-compose logs -f nginx
```

---

## Licence

Projet personnel - Titouan SIMON

---

## Contact

Pour toute question ou contribution, merci de contacter le développeur.
