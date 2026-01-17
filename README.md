# TitouService

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Flask](https://img.shields.io/badge/Flask-Web%20Framework-black)
![Docker](https://img.shields.io/badge/Docker-Container-blue)
![Nginx](https://img.shields.io/badge/Nginx-Reverse%20Proxy-green)
![SQLite](https://img.shields.io/badge/SQLite-Database-lightgrey)

TitouService est une **application web** développée avec **Flask**, déployée via **Docker**, et servie par **Nginx** en tant que reverse proxy.  
Ce projet est conçu pour offrir une plateforme web simple, et facilement déployable sur serveur ou NAS.

## Présentation

TitouService propose une plateforme web qui permet :

- La **gestion de comptes utilisateurs**  
- La **recherche de films via une API externe**  
- La **persistance des données** (connexion, historique, utilisateurs)  

Ce projet sert à la fois de **service fonctionnel** et de **support pédagogique** pour l’apprentissage du développement web backend et du déploiement conteneurisé.

## Objectifs techniques

- Architecture **Flask + Nginx**  
- Orchestration avec **Docker Compose**  
- Gestion sécurisée des secrets (clé Flask, clé API)  
- Base de données **SQLite**  
- Projet backend structuré et maintenable  

## Technologies utilisées

- **Python / Flask**
- **HTML / CSS**
- **SQLite**
- **Docker & Docker Compose**
- **Nginx**

## Architecture

```text
    Client (Navigateur)
        |
        v
    Nginx (Reverse Proxy)
        |
        v
    Flask (Application)
        |
        v
    SQLite (Base de données)
```

## Installation & Lancement

### Prérequis
- Docker
- Docker Compose

### Lancement
1. Cloner le dépôt

```bash
git clone https://github.com/titou4n/titouservice.git
```

2. Configurer les variables et secrets
    - clé Flask -> secrets\secret_key.txt
    - clé API   -> secrets\omdb_api_key.txt

3. Lancer les conteneurs :

```bash
docker-compose up --build
```

4. Accéder à l’application :

```bash
http://localhost:8080
```

## Auteur

Développé par Titouan SIMON - Projet personnel