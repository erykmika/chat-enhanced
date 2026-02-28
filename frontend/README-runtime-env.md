# Runtime env config for the frontend

Vite embeds `import.meta.env.VITE_*` variables at **build time**.
When deploying a pre-built static bundle behind nginx (like this repo),
`docker-compose.yml` `environment:` variables are **runtime**, so they won't
show up in `import.meta.env`.

This frontend image supports runtime configuration by generating `/env.js`
at container start.

## How it works
- `frontend/docker-entrypoint.sh` writes `/usr/share/nginx/html/env.js`.
- `frontend/index.html` loads `/env.js` before the Vite bundle.
- `frontend/src/helpers/api.js` reads `window.__ENV__.VITE_API_BASE_URL` first.

## Usage
In `docker-compose.yml`:

- `VITE_API_BASE_URL=http://backend:8000`

Only put **non-secret** values in runtime env, since `env.js` is public.

