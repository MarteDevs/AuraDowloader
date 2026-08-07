# Aura Music Downloader 🎵

> Cliente-servidor audiófilo para buscar, resolver y descargar música en máxima calidad (FLAC Lossless + MP3 320kbps) con etiquetado ID3, progreso en tiempo real y biblioteca persistente.

![Status](https://img.shields.io/badge/status-active-success)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![React](https://img.shields.io/badge/react-18-blue)
![License](https://img.shields.io/badge/license-MIT-green)

---

## ✨ Características

- **Búsqueda multi-motor**: YouTube (default) y Deezer con ARL para FLAC.
- **Fallback automático** a 320k si FLAC no está disponible.
- **Cola de descargas** con WebSocket y progreso en tiempo real.
- **Etiquetado ID3** con carátula y metadatos.
- **Biblioteca + Favoritos** persistentes en MySQL/SQLite.
- **Autenticación** con Bearer token.
- **HTTPS automático** vía Caddy + Let's Encrypt.
- **Rate limiting** y **path-traversal protection** por defecto.

## 📚 Documentación

- [Inicio rápido](docs/index.md)
- [API Reference](docs/api.md)
- [Despliegue en VPS](docs/deploy.md)
- [Seguridad](docs/security.md)
- [Contribuir](docs/contributing.md)

## 🏗️ Estructura

```
AuraDowloader/
├── aura-backend/        # FastAPI + SQLAlchemy
├── aura-frontend/       # React 18 + Vite
├── deploy/              # Caddyfile
├── docs/                # MkDocs
├── scripts/             # rotate_cookies.py, etc.
└── .github/workflows/   # GitHub Actions CI
```

## 🚀 Quick start

```bash
# Backend
cd aura-backend
py -m venv .venv && .venv\Scripts\activate
pip install -r requirements-dev.txt
uvicorn app.main:app --host 127.0.0.1 --port 9000 --reload

# Frontend (en otra terminal)
cd aura-frontend
npm install
npm run dev
```

Abre <http://localhost:5173>.

## 🧪 Tests

```bash
# Backend (48 tests)
cd aura-backend && pytest

# Frontend (17 tests)
cd aura-frontend && npm test

# E2E con Playwright
cd aura-frontend && npm run e2e:install && npm run e2e
```

## 📦 Producción

Ver [deploy.md](docs/deploy.md) para el setup completo en VPS con Caddy + PM2 + MySQL.

## 🛡️ Seguridad

Ver [security.md](docs/security.md). Aura implementa:
- Auth Bearer con `AUTH_TOKEN`
- Headers CSP / HSTS / X-Frame-Options
- Path-traversal protection
- Rate limiting
- CORS explícito

## 📝 Licencia

MIT.
