# Seguridad

## Resumen

Aura implementa varias capas de seguridad. Esta página describe qué está protegido y qué sigue siendo responsabilidad tuya.

## Autenticación

!!! info "Token estático Bearer"
    Configura `AUTH_TOKEN` en `aura-backend/.env` con un valor aleatorio de al menos 32 caracteres. Genera uno con:
    ```bash
    python3 -c "import secrets; print(secrets.token_urlsafe(48))"
    ```

- El backend valida cada request excepto `/api/health`, `/api/auth/*`, `/docs`, `/openapi.json`.
- El WebSocket valida el token del query string y cierra con código 1008 si no coincide.
- El frontend guarda el token en `localStorage` con clave `aura.authToken.v1`.

!!! warning "HTTPS obligatorio"
    Sin TLS, el token viaja en claro. Configura Caddy o Nginx con Let's Encrypt antes de habilitar `AUTH_TOKEN`.

## Cookies de YouTube

- `youtube_cookies.txt` está en `.gitignore`.
- Rota las cookies periódicamente con `scripts/rotate_cookies.py`.
- Si accidentalmente se suben al repo, **rota de inmediato** y limpia el historial de git con `git filter-repo`.

## Headers de seguridad

El backend añade a cada respuesta:

- `Content-Security-Policy: default-src 'self'; ...`
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `Referrer-Policy: no-referrer`
- `Permissions-Policy: microphone=(), camera=(), geolocation=()`
- `Strict-Transport-Security` (cuando `HSTS_ENABLED=1`)

## Path traversal

`safe_alpath()` valida cada `download_dir` y cada `file_path` servido contra una whitelist de directorios. Cualquier intento de `..` o ruta absoluta fuera de la whitelist devuelve 403 o 400.

## Rate limiting

- Búsqueda: 30/min por IP
- Descarga individual: 10/min
- Álbum completo: 5/min

Configurable con `RATE_LIMIT_STORAGE_URI` (default `memory://`, recomendado `redis://...` en multi-worker).

## Lo que **no** está protegido todavía

- ⚠️ **Sin rate limit en `/api/auth/login`** — un atacante puede hacer brute-force del token. Mitigación: el token tiene 32+ caracteres, así que el espacio de búsqueda es ~10^57. Pero si quieres, añade slowapi también ahí.
- ⚠️ **Sin protección CSRF** — no se usa sesión/cookie de auth, así que el navegador no envía credenciales automáticamente. Pero si en el futuro añades cookie-based auth, debes añadir CSRF tokens.
- ⚠️ **El frontend hace `localStorage.setItem('aura.authToken.v1', ...)`** — un XSS podría robarlo. Mitigamos con CSP estricta (`script-src 'self' 'unsafe-inline'`), pero considera reducir el alcance a `'self'` cuando viertas inline handlers.

## Reportar vulnerabilidades

Email: security@your-domain.example (configurar cuando despliegues).

No abras issues públicos para problemas sensibles.
