# Production Deployment Guide

## Architecture

```
Client (HTTPS) → Nginx (443/SSL) → Flask (5000/HTTP internal)
```

### Key Points:
- **External**: Client communicates with Nginx via HTTPS
- **Internal**: Nginx → Flask uses HTTP (both on Docker network)
- **Flask doesn't handle HTTPS** - Nginx adds proper headers for Flask to understand the request

## Setup

### 1. Prepare Secrets
Create `./secrets/` directory with:
```
secret_key.txt                  # Flask SECRET_KEY
username_super_admin.txt        # Super admin username
password_super_admin.txt        # Super admin password
email_app_password.txt          # Gmail app password
omdb_api_key.txt               # OMDB API key
twelvedata_api_key.txt         # Twelve Data API key
```

### 2. Generate SSL Certificates
```bash
# For development/testing:
chmod +x generate-certs.sh
./generate-certs.sh

# Certificates will be created in ./certs/
```

For production, use Let's Encrypt:
```bash
certbot certonly --standalone -d titouservice.ltjs.net
# Copy certificates to ./certs/
```

### 3. Deploy
```bash
# Build images
docker-compose build

# Start services
docker-compose up -d
```

## Environment Variables

### Flask (via docker-compose.yml)
- `ENV_PROD=true` - Enables production mode (reads secrets, disables debug)
- `FLASK_ENV=production` - Flask environment

### Database Reset Flags
⚠️ **DISABLED BY DEFAULT** in `config.py`:
- `NEED_TO_RESET_ALL_DB=False`
- `NEED_TO_RESET_ROLES_PERMISSIONS_TABLES=False`

Never enable these in production!

## HTTP/HTTPS Flow (Fixes)

### ✅ Before (Broken)
- Nginx generated self-signed cert during build
- Flask port 5000 exposed directly (could bypass SSL)
- Flask received `X-Forwarded-Proto=$scheme` (dynamic, could be wrong)
- Session cookies might use insecure scheme

### ✅ After (Fixed)
- Certificates mounted from `./certs/` volume
- Flask NOT exposed (port 5000 removed from docker-compose)
- Nginx sends `X-Forwarded-Proto=https` (static, always HTTPS for external)
- Flask via ProxyFix correctly understands HTTPS scheme
- SESSION_COOKIE_SECURE=true works correctly in production

## Nginx Configuration

```
Port 80 (HTTP):   → Redirects all to HTTPS
Port 443 (HTTPS): → Serves with SSL → Proxies to Flask:5000
```

Headers Flask receives:
```
X-Forwarded-Proto: https
X-Forwarded-For: <client-ip>
X-Real-IP: <client-ip>
X-Forwarded-Host: titouservice.ltjs.net
X-Forwarded-Port: 443
```

ProxyFix reconstructs the URL as: `https://titouservice.ltjs.net/...`

## Gunicorn Production Settings

```
--workers=4           # 4 worker processes
--worker-class=sync   # Synchronous workers
--timeout=120         # 120s request timeout
--bind=0.0.0.0:5000   # Listen on Docker network
```

## Monitoring

### Check Flask logs:
```bash
docker logs titouservice-flask
```

### Check Nginx logs:
```bash
docker exec titouservice-nginx cat /var/log/nginx/error.log
```

### Test HTTPS:
```bash
curl -k https://localhost:8443
```

## Troubleshooting

### Infinite redirect loop
- ✅ Fixed: Nginx now sends static `X-Forwarded-Proto: https`
- Check: Flask should see `request.is_secure=True`

### 502 Bad Gateway
- Check Flask container is running: `docker ps`
- Check Flask logs: `docker logs titouservice-flask`

### SSL certificate errors
- Regenerate certificates: `./generate-certs.sh`
- Or copy valid Let's Encrypt certs to `./certs/`

### Database reset on startup
- Check `config.py` - reset flags must be False
- In `docker-compose.yml`, `ENV_PROD=true` is set
