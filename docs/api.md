# API Reference

La API sigue REST + WebSocket. Por defecto escucha en `http://127.0.0.1:9000`.

## Autenticación

Si el backend está configurado con `AUTH_TOKEN`, todas las rutas excepto `/api/health`, `/api/auth/*`, `/docs` y `/openapi.json` requieren:

```
Authorization: Bearer <token>
```

El WebSocket (`/ws/downloads`) y la descarga de archivos (`/api/download/file/{id}`) aceptan el token como query string:

```
ws://host:9000/ws/downloads?token=<token>
GET /api/download/file/abc?token=<token>
```

## Health

### `GET /api/health`

Sin auth. Devuelve estado del servidor.

**Response 200**
```json
{ "status": "online", "app": "Aura Music Downloader", "version": "2.0.0" }
```

## Auth

### `GET /api/auth/status`

Sin auth. Indica si el backend requiere token.

```json
{ "auth_required": true, "version": "2.0.0" }
```

### `POST /api/auth/login`

Sin auth. Comprueba token (no-op si `AUTH_TOKEN` está vacío).

**Request body**
```json
{ "token": "your-token" }
```

**Response 204** en éxito, **401** si el token no coincide.

## Search

### `GET /api/search`

Busca canciones.

| Param | Tipo | Default | Notas |
|---|---|---|---|
| `q` | string | requerido | min 1 char |
| `engine` | string | `youtube` | `youtube` o `deezer` |
| `limit` | int | 15 | 1–50 |

Rate limit: **30/min por IP**.

**Response 200**
```json
{
  "query": "Daft Punk",
  "engine": "youtube",
  "count": 15,
  "results": [
    {
      "id": "...",
      "title": "Get Lucky",
      "artist": "Daft Punk",
      "album": "...",
      "duration": "06:09",
      "duration_sec": 369,
      "thumbnail": "https://...",
      "url": "https://www.youtube.com/watch?v=...",
      "engine": "youtube",
      "quality_badge": "HQ (256k)",
      "available_qualities": ["standard", "320k"]
    }
  ]
}
```

### `GET /api/search/albums`

Igual que `/api/search` pero para álbumes.

### `GET /api/album/{album_id}/tracks`

Lista las pistas de un álbum.

| Param | Tipo | Default |
|---|---|---|
| `album_id` | string | requerido en path |
| `engine` | string | `youtube` |

## Download

### `POST /api/download`

Inicia la descarga de una canción.

**Request body**
```json
{
  "id": "youtube_video_id",
  "title": "Get Lucky",
  "artist": "Daft Punk",
  "thumbnail": "https://...",
  "url": "https://www.youtube.com/watch?v=...",
  "engine": "youtube",
  "quality": "320k"
}
```

Calidades válidas:
- `flac` — solo con `engine=deezer` y ARL configurado.
- `320k` — MP3 320kbps.
- `standard` — MP3 160kbps.

Si la calidad pedida no es compatible con el motor, el backend la reduce automáticamente a `320k`.

Rate limit: **10/min por IP**.

**Response 200**
```json
{
  "status": "queued",
  "download_id": "uuid",
  "item": { ... }
}
```

### `POST /api/download/album`

Inicia la descarga de varias pistas en bloque. Body:

```json
{
  "album_id": "...",
  "album_title": "...",
  "artist": "...",
  "engine": "youtube",
  "quality": "320k",
  "tracks": [ { "id": "...", "title": "...", "url": "..." } ]
}
```

Rate limit: **5/min por IP**.

### `GET /api/download/queue`

Devuelve el estado actual de la cola (items en memoria + cacheados de DB).

### `POST /api/download/cancel/{download_id}`

Cancela una descarga en curso. No-op si ya está completada o en error.

### `POST /api/download/retry/{download_id}`

Re-encola una descarga cancelada o en error (si su `track_info` sigue en memoria).

### `DELETE /api/download/{download_id}`

Elimina un item de la cola (no borra el archivo del disco).

### `GET /api/download/file/{download_id}`

Devuelve el archivo MP3/FLAC. **Importante:** los navegadores no pueden enviar headers en `<a download>`, así que se usa el query string `?token=...` para autorizar.

## Library & Favorites

### `GET /api/library`

Historial completo de canciones descargadas, ordenadas por fecha desc.

### `GET /api/favorites`

Solo las marcadas como favoritas.

### `POST /api/favorites/{track_id}/toggle`

Alterna el flag `is_favorite` de una canción en la DB.

## Settings

!!! danger "El backend ya NO expone el ARL token en `GET /settings`"
    Solo devuelve `has_arl: bool`. El token se mantiene interno.

### `GET /api/settings`

```json
{
  "has_arl": true,
  "default_quality": "flac",
  "download_dir": "D:\\...",
  "cookies_file": "D:\\...\\youtube_cookies.txt"
}
```

### `POST /api/settings`

Body:

```json
{
  "arl_token": "...",
  "default_quality": "flac",
  "download_dir": "D:\\...",
  "cookies_file": "D:\\...\\youtube_cookies.txt"
}
```

`download_dir` se valida contra la whitelist de paths permitidos.

## WebSocket

### `WS /ws/downloads`

Acepta conexiones para recibir eventos de progreso en tiempo real.

**Eventos emitidos:**

| Tipo | Payload |
|---|---|
| `download_queued` | `{ type, item }` |
| `download_progress` | `{ type, item }` (cada 1s aprox.) |
| `download_completed` | `{ type, item }` |
| `download_error` | `{ type, item }` |
| `download_cancelled` | `{ type, item }` |

**Ejemplo con JS:**

```js
const ws = new WebSocket(`ws://host:9000/ws/downloads?token=${token}`);
ws.onmessage = (e) => {
  const event = JSON.parse(e.data);
  console.log(event.type, event.item);
};
```
