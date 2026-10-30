FROM nginx:alpine
# Redirecciones (dominio canónico y URLs antiguas), caché, gzip y cabeceras
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY dist /usr/share/nginx/html
EXPOSE 80
