# ==================================================
# TitouService - Nginx Web Server Image
# ==================================================

FROM nginx:latest

# Copier uniquement la config nginx
COPY nginx/nginx.conf /etc/nginx/nginx.conf

EXPOSE 80
EXPOSE 443

CMD ["nginx", "-g", "daemon off;"]