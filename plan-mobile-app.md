# Aura Mobile — Plan de Implementación

> App móvil cliente del backend FastAPI existente (`aura-backend`, v2.0.0).
> El backend **ya expone todo lo necesario**; no se requieren cambios en el servidor
> salvo un ajuste de CORS (solo si se usa una variante WebView) y asegurar que
> `HOST=0.0.0.0` en el `.env` del VPS para aceptar conexiones externas.

---

## 1. Stack recomendado

**React Native + Expo** es la opción natural:

| Razón | Detalle |
|---|---|
| Mismo lenguaje que el frontend web | React/JS; patrones de `aura-frontend/src/services/api.js` se portan casi 1:1 |
| WebSocket nativo incluido | `WebSocket` global disponible sin plugins |
| Ecosistema de descarga/archivos | `expo-file-system`, `expo-media-library` para guardar audio en el dispositivo |
| Notificaciones | `expo-notifications` para avisar "descarga completada" en background |
| OTA updates | Expo EAS para despliegues sin pasar por stores en cada fix |

Alternativa válida: **Flutter** (con `dio`, `web_socket_channel`, `path_provider`), pero implica reescribir la lógica en Dart.

---

## 2. Mapa completo de APIs a consumir

Base URL: `https://<tu-vps>:9000/api` (configurable en la app, ver §6).

### 2.1 Autenticación

| Método | Endpoint | Auth | Descripción |
|---|---|---|---|
| GET | `/api/auth/status` | No | `{ auth_required: bool, version }` — primer call al arrancar |
| POST | `/api/auth/login` | No | Body `{ "token": "..." }` → `204` OK / `401` inválido |

**Flujo:** al abrir la app → `GET /auth/status`. Si `auth_required=true` y no hay token guardado → pantalla de login (igual que `LoginScreen.jsx`). El token se persiste en **almacenamiento seguro** (`expo-secure-store`, NO AsyncStorage).

**Header en todas las llamadas autenticadas:**
```
Authorization: Bearer <token>
```
El backend también acepta `?token=` en query string (necesario para el WebSocket y para la descarga de archivos, ver §2.5).

### 2.2 Health

| Método | Endpoint | Auth | Descripción |
|---|---|---|---|
| GET | `/api/health` | No | `{ status: "online" }` — ping cada 30 s para el indicador de conexión |

### 2.3 Búsqueda (rate limit: 30/min)

| Método | Endpoint | Descripción |
|---|---|---|
| GET | `/api/search?q={q}&engine={youtube\|deezer}&limit={1-50}` | Canciones → `{ count, results[] }` |
| GET | `/api/search/albums?q=...&engine=...` | Álbumes → `{ count, results[] }` |
| GET | `/api/album/{album_id}/tracks?engine=...` | Tracks de un álbum → `{ count, tracks[] }` |

**Nota:** si `engine=deezer` no devuelve resultados, el backend ya hace fallback a YouTube internamente — la app no necesita reintentar.

### 2.4 Descargas (rate limit: 10/min singles, 5/min álbumes)

| Método | Endpoint | Body / Respuesta |
|---|---|---|
| POST | `/api/download` | Body: `{ id, title, artist, thumbnail, url, engine, quality }` → `{ status: "queued", download_id, item }` |
| POST | `/api/download/album` | Body: `{ album_id, album_title, artist, engine, quality, tracks[] }` → `{ status: "album_queued", total_tracks, items[] }` |
| GET | `/api/download/queue` | → `{ count, items[] }` (estado actual, se pide una vez al conectar) |
| POST | `/api/download/cancel/{id}` | → `{ status: "cancelled" }` (404 si ya terminó) |
| POST | `/api/download/retry/{id}` | → `{ status: "queued", item }` |
| DELETE | `/api/download/{id}` | → `{ status: "removed" }` |

**Reglas de calidad** (el backend las normaliza, pero la app debería pre-validar):
- `flac` → solo `deezer`
- `320k` / `standard` → `youtube` y `deezer`

**Modelo `DownloadItem`:**
```json
{
  "id": "uuid",
  "title": "...", "artist": "...", "thumbnail": "https://...",
  "engine": "youtube|deezer", "quality": "flac|320k|standard",
  "status": "queued|downloading|processing|completed|error|cancelled",
  "progress": 0.0, "speed": "1.2 MB/s", "eta": "01:23",
  "file_name": "...", "file_path": "...",
  "error_message": "", "created_at": 1720000000.0
}
```

### 2.5 Obtener el archivo resultante

| Método | Endpoint | Descripción |
|---|---|---|
| GET | `/api/download/file/{download_id}?token=<token>` | Binario del audio (MP3/FLAC). Solo disponible cuando `status == "completed"` |

En móvil **no se puede** abrir un `<a download>` como en web: hay que descargar con `expo-file-system`:
```js
FileSystem.downloadAsync(
  `${API}/download/file/${id}?token=${token}`,
  FileSystem.documentDirectory + fileName
)
```
y luego opcionalmente registrarlo en la galería de medios con `expo-media-library`.

### 2.6 Biblioteca y Favoritos

| Método | Endpoint | Descripción |
|---|---|---|
| GET | `/api/library` | `{ count, tracks[] }` — todo lo descargado (persistido en MySQL) |
| GET | `/api/favorites` | `{ count, tracks[] }` — solo favoritos |
| POST | `/api/favorites/{track_id}/toggle` | → `{ is_favorite }` (404 si el track no existe en DB) |

**Modelo `Track`:**
```json
{
  "id": "...", "title": "...", "artist": "...", "album": "...",
  "thumbnail": "...", "duration": "3:24", "duration_sec": 204,
  "file_path": "...", "file_name": "...",
  "quality": "320k", "engine": "youtube",
  "is_favorite": false, "created_at": "2026-08-07T..."
}
```

### 2.7 Settings

| Método | Endpoint | Descripción |
|---|---|---|
| GET | `/api/settings` | `{ has_arl, default_quality, download_dir, cookies_file }` |
| POST | `/api/settings` | Guarda ajustes (el backend normaliza `download_dir` inválido al default) |

En móvil, `download_dir`/`cookies_file` son rutas del **servidor** — mostrarlas read-only o en una sección "Avanzado". Lo relevante para el usuario móvil es `default_quality`.

### 2.8 WebSocket — tiempo real

| Canal | Auth | Eventos |
|---|---|---|
| `WS /ws/downloads?token=<token>` | Query param | `download_queued`, `download_progress`, `download_completed`, `download_error`, `download_cancelled` |

Payload de cada evento: `{ type: "<evento>", item: DownloadItem }`.

**Lógica de reconexión** (portar de `websocket.js`): backoff exponencial 1 s → 30 s máx, cancelar reconexión si el servidor cierra con código `1008` (token rechazado → volver a login).

**Importante:** el WS cierra si el cliente no envía nada nunca (`receive_text()` bloquea). La app debe mandar un ping periódico (texto vacío o `"ping"` cada ~25 s) para mantener viva la conexión en background.

---

## 3. Arquitectura de la app

```
aura-mobile/
├── app/                      # Expo Router (file-based routing)
│   ├── (auth)/login.tsx
│   ├── (tabs)/
│   │   ├── index.tsx         # Buscar
│   │   ├── library.tsx       # Biblioteca
│   │   ├── favorites.tsx     # Favoritos
│   │   └── queue.tsx         # Cola de descargas (badge con activos)
│   └── _layout.tsx           # AuthGate + WebSocketProvider
├── src/
│   ├── api/
│   │   ├── client.ts         # fetch wrapper con Bearer + manejo de 401
│   │   ├── auth.ts           # status / login
│   │   ├── search.ts
│   │   ├── downloads.ts
│   │   ├── library.ts
│   │   └── settings.ts
│   ├── ws/
│   │   └── downloadSocket.ts # port de aura-frontend/src/services/websocket.js
│   ├── store/
│   │   ├── authStore.ts      # Zustand: token, isAuthenticated
│   │   └── queueStore.ts     # Zustand: cola mergeada WS + REST
│   ├── components/           # SongCard, AlbumCard, QualityBadge (port del frontend)
│   └── lib/
│       ├── secureToken.ts    # expo-secure-store get/set/clear
│       └── fileDownload.ts   # expo-file-system + media-library
└── app.config.ts             # extra.apiUrl, extra.wsUrl
```

**Gestión de estado:** Zustand (ligero, mismo patrón que el estado local actual de React) o TanStack Query para el cacheo de búsqueda/biblioteca. La cola se mantiene en un store que combina:
1. `GET /download/queue` inicial (al autenticar)
2. Eventos del WebSocket (upsert por `item.id`)
3. Persistencia local opcional (MMKV) para mostrar la última cola conocida offline

**Manejo de 401:** el wrapper de fetch limpia el token seguro y redirige a login (equivalente al evento `aura:auth-expired` del frontend web).

---

## 4. Pantallas (paridad con el frontend web)

| Pantalla | Consume | Componentes reutilizables conceptualmente |
|---|---|---|
| Login | `/auth/status`, `/auth/login` | `LoginScreen.jsx` |
| Buscar (tabs: canciones/álbumes) | `/search`, `/search/albums`, `/album/{id}/tracks`, `POST /download`, `POST /download/album` | `SearchPage.jsx`, `SongCard`, `AlbumCard`, `SearchBar` |
| Cola (modal o tab con badge) | WS + `/download/queue` + cancel/retry/remove | `DownloadQueue.jsx` |
| Biblioteca | `/library`, `GET /download/file/{id}` | `LibraryPage.jsx` |
| Favoritos | `/favorites`, toggle | `FavoritesPage.jsx` |
| Ajustes | `/settings` | `SettingsModal.jsx` |

---

## 5. Consideraciones móviles específicas

1. **Descargas al dispositivo:** el audio se genera en el servidor; el móvil lo baja vía `/download/file/{id}`. Decidir UX: auto-descargar al completar, o botón "Guardar en el teléfono" por track (recomendado: botón, para no gastar datos).
2. **Reproducción local:** una vez bajado, `expo-av` puede reproducirlo. La biblioteca muestra qué tracks ya están en el dispositivo vs solo en el servidor.
3. **Background:** iOS suspende WebSockets al ir a background. Aceptable: al volver a foreground, reconectar y hacer `GET /download/queue` para resincronizar (el backend mantiene la cola en memoria). Notificaciones locales programadas al iniciar una descarga como red de seguridad.
4. **HTTPS:** si el VPS no tiene certificado válido, Android bloquea cleartext por defecto. Opciones: (a) certificado con Caddy/Nginx + duckdns (ya hay referencias a duckdns en el repo), (b) `usesCleartextTraffic: true` solo en builds de desarrollo.
5. **CORS:** irrelevante para app nativa; solo afectaría si se hiciera una variante PWA/WebView. El backend ya acepta orígenes configurables vía `FRONTEND_URL`.

---

## 6. Checklist previo en el backend (una sola vez)

- [ ] `HOST=0.0.0.0` en `aura-backend/.env` del VPS (hoy es `127.0.0.1`, no acepta conexiones externas).
- [ ] `AURA_AUTH_TOKEN` configurado (obligatorio si la app se expone a internet).
- [ ] Puerto 9000 abierto en el firewall del VPS.
- [ ] (Recomendado) HTTPS con reverse proxy para no exponer el token en cleartext.
- [ ] (Opcional) Ping handler: el endpoint WS ya hace `receive_text()` en loop; un `"ping"` de texto es suficiente, no requiere cambio.

---

## 7. Roadmap por fases

| Fase | Alcance | Criterio de salida |
|---|---|---|
| **0 — Scaffold** | Expo + Router + cliente API + SecureStore + AuthGate | Login contra el VPS real funciona |
| **1 — Buscar y descargar** | Pantalla Search + `POST /download` + cola con polling REST (sin WS aún) | Descargar una canción end-to-end |
| **2 — Tiempo real** | WebSocket con backoff + store de cola mergeado + badge | Progreso en vivo sin refrescar |
| **3 — Biblioteca/Favoritos** | Tabs Library/Favorites + toggle + guardar archivo en dispositivo | Track bajado suena en `expo-av` |
| **4 — Pulido** | Álbumes, settings, notificaciones locales, manejo offline | Paridad funcional con el frontend web |
