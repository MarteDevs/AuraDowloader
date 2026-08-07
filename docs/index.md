# Aura Music Downloader

Aplicación cliente-servidor para buscar, resolver y descargar música en la máxima calidad posible (FLAC Lossless + MP3 320kbps).

## Características

- **Búsqueda multi-motor** — YouTube (default) y Deezer (con ARL token para FLAC).
- **Sistema de fallback automático** — Si Deezer FLAC no está disponible, descarga de YouTube en 320k.
- **Etiquetado ID3 automático** — Cover art, artista, álbum, año incrustados.
- **Cola de descargas en tiempo real** — WebSocket con progreso, velocidad y ETA.
- **Historial persistente** — MySQL o SQLite, con favoritos.
- **Autenticación por token** — Bearer token configurable en el backend.
- **HTTPS automático** — Caddy reverse proxy con Let's Encrypt.
- **Rate limiting** — slowapi protege los endpoints upstream.

## Stack

| Capa | Tecnología |
|---|---|
| Frontend | React 18, Vite, Tailwind, react-router-dom, sonner |
| Backend | Python 3.10+, FastAPI, SQLAlchemy, yt-dlp, httpx |
| Proxy | Caddy (TLS automático) |
| BD | MySQL 8 (prod) / SQLite (dev) |

## Estructura

```
AuraDowloader/
├── aura-backend/        # FastAPI + SQLAlchemy
├── aura-frontend/       # React + Vite
├── deploy/              # Caddyfile, scripts
├── docs/                # MkDocs
└── scripts/             # rotate_cookies.py, etc.
```

## Inicio rápido (desarrollo local)

```bash
# Backend
cd aura-backend
py -m venv .venv
.venv\Scripts\activate
pip install -r requirements-dev.txt
uvicorn app.main:app --host 127.0.0.1 --port 9000 --reload

# Frontend
cd aura-frontend
npm install
npm run dev
```

Abre <http://localhost:5173>.

## Tests

```bash
# Backend
cd aura-backend
pytest

# Frontend
cd aura-frontend
npm test
```
