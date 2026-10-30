# Web Zirotti — código fuente

Sitio estático (HTML + CSS, sin frameworks). `dist/` es lo que se publica; **no se edita a mano**: se genera.

```bash
python3 src/build.py    # genera dist/ (borra y recrea la carpeta)
python3 src/check.py    # valida SEO: title, description, H1, hreflang, enlaces, JSON-LD
python3 -m http.server 8765 --directory dist   # ver en http://localhost:8765
```

## Dónde se cambia cada cosa

| Qué | Dónde |
| --- | --- |
| Textos ES/EN de cada página | `src/build.py` (función `build_<página>`; ES y EN van juntos con `t(L, "es", "en")`) |
| Title y description por página | `src/build.py`, al inicio de cada `build_<página>` |
| URLs (slugs) | `PATHS` en `src/build.py` (si se cambia, añadir 301 en `nginx.conf`) |
| Diseño | `src/assets/style.css` |
| Formulario / cabecera | `src/assets/site.js` y `contact_form()` en `build.py` |
| Datos estructurados | `org_node`, `person_node`, `service_node` en `build.py` |
| Imagen al compartir / icono | `python3 src/make_images.py` (solo macOS; ya generadas en `src/`) |

## Publicar

`Dockerfile` copia `dist/` y `nginx.conf` en una imagen `nginx:alpine`. Tras cambiar algo: `build.py` → commit de `src/` **y** `dist/` → redeploy.

`nginx.conf` redirige `zirotti.com` → `www.zirotti.com` y las URLs antiguas (`/forma.html`, etc.) a las nuevas.
