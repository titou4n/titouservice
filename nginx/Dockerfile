# ==================================================
# TitouService - Nginx Web Server Image
# ==================================================

# Use a specific, updated patch version of the nginx Alpine image to reduce known vulnerabilities
FROM nginx:1.26.4-alpine

# Copier uniquement la config nginx
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80
EXPOSE 443

CMD ["nginx", "-g", "daemon off;"]