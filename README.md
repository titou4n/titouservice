# TitouService

A comprehensive web platform built with Flask and Docker Compose. TitouService provides a complete suite of integrated services including user authentication, social networking, banking simulation, project tracking, and real-time data integration.

**Live**: [https://titouservice.ltjs.net](https://titouservice.ltjs.net)

## Overview

TitouService is a production-ready web application designed with a modular architecture. Each feature is isolated as a blueprint, making the codebase maintainable and extensible. The application uses SQLite for data persistence and Nginx as a reverse proxy for reliable serving in production environments.

## Technology Stack

- **Backend**: Python 3.12, Flask 2.3+
- **Database**: SQLite
- **Frontend**: HTML, CSS, Jinja2 templating
- **Server**: Gunicorn, Nginx
- **Containerization**: Docker, Docker Compose
- **Key Libraries**: Flask-Login, Flask-Session, Flask-WTF, Flask-Limiter

## Quick Start

### Prerequisites

- Docker 20.10+
- Docker Compose 2.0+

### Installation

1. Clone the repository:

```bash
git clone https://github.com/titou4n/titouservice.git
```

```bash
cd titouservice
```

2. Create secrets directory with required configuration files:

```bash
mkdir -p secrets
```

Create the following files in the `secrets/` directory:

- `secret_key.txt` - Flask secret key
- `username_super_admin.txt` - Super admin username
- `password_super_admin.txt` - Super admin password
- `omdb_api_key.txt` - OMDB API key
- `twelvedata_api_key.txt` - Twelve Data API key
- `email_app_password.txt` - Gmail app password

Example:

```bash
python3 -c "import secrets; print(secrets.token_hex(32))" > secrets/secret_key.txt
echo "admin" > secrets/username_super_admin.txt
echo "secure_password" > secrets/password_super_admin.txt
```

3. Start the application:

```bash
docker-compose up --build
```

Access the application at `http://localhost`

## Architecture

```
Client → Nginx (Port 80) → Flask (Port 5000) → SQLite Database
```

The application follows a modular blueprint pattern with clear separation of concerns. Each module handles its own routes, services, and data access logic.

## Project Structure

```
titouservice/
├── flask/
│   ├── app.py                    # Flask factory
│   ├── config.py                 # Configuration
│   ├── extensions.py             # Flask extensions
│   ├── blueprints/               # Feature modules
│   ├── models/                   # Data models
│   ├── Data/                     # Data layer
│   ├── utils/                    # Utilities
│   ├── templates/                # Jinja2 templates
│   ├── static/                   # CSS, JS, assets
│   └── requirements.txt
├── nginx/                        # Nginx configuration
└── docker-compose.yml
```

## Features

The application includes integrated modules for:

- User authentication and account management
- Role-based access control and administration
- Social networking capabilities
- Real-time messaging
- Banking simulation
- Task tracking and project management
- Media search integration
- Emergency contact management
- User settings and profile management

## Configuration

Application configuration is handled through `config.py`. In production, sensitive values are read from Docker secrets. In development, configuration can be provided via environment variables in a `.env` file.

## Security

- CSRF protection on all forms
- Secure session management with HttpOnly and Secure flags
- Rate limiting on API endpoints
- Two-factor authentication support
- Role-based access control
- Secrets management via Docker Secrets

For production deployments, ensure:
- HTTPS is enabled
- All secrets are properly managed
- Database backups are configured
- Monitoring and logging are in place

## Development

### Local Development

```bash
# Set ENV_PROD=false in config.py
cd flask
pip install -r requirements.txt
python app.py
```

Application runs on `http://127.0.0.1:8080`

### Database

Reset the database during development:

```bash
rm flask/Data/db/database.db
python flask/init_db.py
```

### Logs

```bash
docker-compose logs -f flask
docker-compose logs -f nginx
```

## Deployment

The application is containerized and ready for deployment. All components are orchestrated through Docker Compose.

```bash
docker-compose up --build
```

The application will be accessible on port 80 (HTTP) in production.

## License

Apache License Version 2.0 - See LICENSE file for details

## Author

Titouan SIMON
