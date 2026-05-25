# ==================================================
# TitouService - Nginx Web Server Image
# ==================================================

FROM nginx:1.25-alpine

# Copy only nginx config
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80
EXPOSE 443

CMD ["nginx", "-g", "daemon off;"]