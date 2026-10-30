FROM nginx:alpine
# nginx.conf (redirecciones, caché, cabeceras) está en el repositorio pero no se usa
# todavía: se desactivó para descartarlo como causa de un 502 tras el despliegue.
COPY dist /usr/share/nginx/html
EXPOSE 80
