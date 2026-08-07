# Contribuir

¡Gracias por tu interés en Aura! Por favor, lee esta guía antes de abrir un PR.

## Setup

```bash
# Backend
cd aura-backend
py -m venv .venv
.venv\Scripts\activate
pip install -r requirements-dev.txt

# Frontend
cd aura-frontend
npm install
```

## Flujo de trabajo

1. Crea una rama desde `main`: `git checkout -b feat/my-feature`.
2. Haz commits pequeños y descriptivos. Conventional Commits preferido (`feat:`, `fix:`, `chore:`, etc.).
3. Antes de push:

   ```bash
   # Backend
   cd aura-backend
   ruff check .
   pytest

   # Frontend
   cd aura-frontend
   npm run lint
   npm test
   npm run build
   ```

4. Abre el PR contra `main`. CI se ejecutará automáticamente.

## Estructura del código

- `aura-backend/app/api/endpoints/` — Cada router en su archivo. Handlers finos.
- `aura-backend/app/services/` — Lógica de negocio. Cero FastAPI imports si es posible.
- `aura-backend/app/core/` — Config, DB, auth, security headers. Punto único de verdad.
- `aura-backend/app/models/` — SQLAlchemy. Mantén las migraciones simples.

## Tests

- Cada bug fix debe incluir un test que lo reproduzca.
- Cada feature nuevo debe incluir tests para los happy paths.
- Apuntamos a >80% de cobertura en backend (`pytest --cov=app`).

## Code style

### Python

- Line length: 100 (configurado en `ruff.toml`).
- Type hints obligatorios en funciones nuevas.
- Docstrings en español o inglés (consistente con el archivo).
- `from __future__ import annotations` solo si es necesario.

### JavaScript/React

- Functional components + hooks. No class components.
- Destructura props en la firma.
- Usa `useCallback` y `useMemo` solo cuando hay un beneficio medible.
- Nombres en inglés para variables, español para UI strings.

## Despliegue

La rama `main` se considera estable. Los despliegues a producción se hacen con tags:

```bash
git tag -a v2.0.1 -m "Release v2.0.1"
git push origin v2.0.1
```
