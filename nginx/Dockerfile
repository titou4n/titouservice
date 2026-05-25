# ==================================================
# TitouService - Nginx Web Server Image
# ==================================================

FROM nginx:1.25-alpine

# Create self-signed certificate for development
RUN apk add --no-cache openssl && \
    mkdir -p /etc/nginx/certs && \
    openssl req -x509 -newkey rsa:2048 -nodes \
    -out /etc/nginx/certs/cert.pem -keyout /etc/nginx/certs/key.pem \
    -days 365 -subj "/CN=titouservice.ltjs.net" && \
    apk del openssl

# Copy only nginx config
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80
EXPOSE 443

CMD ["nginx", "-g", "daemon off;"]