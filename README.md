# 🎵 Aura Music Downloader

Descargador de música audiófila cliente-servidor. Soporta calidad **FLAC Lossless** (vía Deezer ARL) y **MP3 320kbps** (vía YouTube). Incluye búsqueda de artistas, álbumes, etiquetado automático ID3, progreso en tiempo real vía **WebSockets** e historial persistente en **MySQL**.

---

## 🗺️ Estructura del Proyecto

```
AuraDowloader/
├── aura-backend/          # Backend FastAPI (Python)
│   ├── app/
│   │   ├── api/           # Endpoints REST y WebSocket
│   │   ├── core/          # Config, DB, FFmpeg
│   │   ├── models/        # Modelos SQLAlchemy
│   │   └── services/      # YouTube, Deezer, Download Manager
│   ├── .env               # Variables de entorno (NO en Git)
│   ├── .env.example       # Plantilla de configuración
│   └── requirements.txt
├── aura-frontend/         # Frontend React + Vite + Tailwind
│   ├── src/
│   ├── .env               # Variables de entorno (NO en Git)
│   ├── .env.example       # Plantilla de configuración
│   └── package.json
└── ecosystem.config.js    # PM2 — gestor de procesos producción
```

---

## 💻 Desarrollo Local (Windows)

### 1. Backend

```powershell
cd aura-backend

# Crear el entorno virtual
py -m venv .venv

# Activar el entorno virtual (Windows)
.venv\Scripts\activate

# Instalar dependencias dentro del .venv
pip install -r requirements.txt

# El .env ya está configurado con valores locales (root/marte)
# Asegúrate de que MySQL local esté corriendo en el puerto 3306

# Iniciar backend (crea la DB automáticamente al arrancar)
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

> 💡 La próxima vez solo activa el entorno y arranca:
> ```powershell
> .venv\Scripts\activate
> uvicorn app.main:app --reload
> ```

La API estará disponible en: `http://localhost:8000`  
Documentación Swagger: `http://localhost:8000/docs`

### 2. Frontend

```powershell
cd aura-frontend
npm install
npm run dev
```

La app estará disponible en: `http://localhost:5173`

---

## 🚀 Despliegue en VPS Contabo (Linux)

**Dominio:** `aura-downloader.duckdns.org` | **IP:** `5.189.171.171`

### 1. Clonar el repositorio en el VPS

```bash
ssh root@5.189.171.171
git clone <tu-repositorio> /var/www/AuraDowloader
cd /var/www/AuraDowloader
```

### 2. Crear carpetas necesarias

```bash
mkdir -p /var/www/AuraDowloader/downloads
mkdir -p /var/www/AuraDowloader/logs
```

### 3. Configurar el Backend (.env)

```bash
cp aura-backend/.env.example aura-backend/.env
nano aura-backend/.env
```

Contenido del `.env` en el VPS:
```env
HOST=0.0.0.0
PORT=8000
DB_HOST=localhost
DB_PORT=3306
DB_USER=aura_user
DB_PASSWORD=TU_PASSWORD_SEGURO
DB_NAME=aura_music_db
DOWNLOAD_DIR=/var/www/AuraDowloader/downloads
FRONTEND_URL=http://aura-downloader.duckdns.org:3000
```

### 4. Crear usuario y base de datos MySQL

```bash
mysql -u root -p
```
```sql
CREATE USER 'aura_user'@'localhost' IDENTIFIED BY 'TU_PASSWORD_SEGURO';
GRANT ALL PRIVILEGES ON aura_music_db.* TO 'aura_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

> El backend crea la base de datos `aura_music_db` automáticamente al arrancar.

### 5. Entorno virtual y dependencias del Backend (Linux)

```bash
cd /var/www/AuraDowloader/aura-backend

# Crear el entorno virtual
python3 -m venv .venv

# Activar el entorno virtual (Linux — usa / no \)
source .venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Desactivar cuando termines (opcional)
deactivate
```

> 💡 A diferencia de Windows, en Linux el comando es siempre:
> ```bash
> source .venv/bin/activate   # Activar
> deactivate                  # Desactivar
> ```

### 6. Actualizar el ecosystem.config.js para usar .venv en Linux

Edita el `interpreter` en `ecosystem.config.js` para apuntar al Python del `.venv`:

```bash
nano /var/www/AuraDowloader/ecosystem.config.js
```

Cambia la línea del backend:
```js
// Antes:
interpreter: 'python3',

// Después (usa el Python del .venv):
interpreter: '/var/www/AuraDowloader/aura-backend/.venv/bin/python3',
```

### 7. Instalar dependencias y Build del Frontend

```bash
cd /var/www/AuraDowloader/aura-frontend
npm install

# Build de producción con las URLs del VPS
VITE_API_BASE_URL=http://aura-downloader.duckdns.org:8000 \
VITE_WS_BASE_URL=ws://aura-downloader.duckdns.org:8000 \
npm run build

cd ..
```

### 8. Instalar PM2 y levantar la aplicación

```bash
# Instalar PM2 globalmente
npm install -g pm2

# Iniciar todos los servicios en modo producción
pm2 start ecosystem.config.js --env production

# Verificar que están corriendo
pm2 status

# Guardar para auto-arranque tras reinicio del servidor
pm2 save
pm2 startup
# Ejecuta el comando que pm2 te muestra en pantalla
```

### 9. Verificar el despliegue

```bash
# Verificar backend
curl http://localhost:8000/api/health

# Ver logs en tiempo real
pm2 logs aura-backend
pm2 logs aura-frontend
```

La aplicación estará disponible en:
- **Frontend:** `http://aura-downloader.duckdns.org:3000`
- **Backend API:** `http://aura-downloader.duckdns.org:8000`
- **API Docs:** `http://aura-downloader.duckdns.org:8000/docs`

---

## 🔧 Comandos PM2 Útiles

```bash
pm2 status                    # Ver estado de todos los procesos
pm2 logs                      # Ver todos los logs
pm2 logs aura-backend         # Logs solo del backend
pm2 logs aura-frontend        # Logs solo del frontend
pm2 restart aura-backend      # Reiniciar el backend
pm2 restart all               # Reiniciar todos los procesos
pm2 stop all                  # Detener todos los procesos
pm2 delete all                # Eliminar todos los procesos de PM2
pm2 monit                     # Monitor visual interactivo
```

---

## 🔑 Configuración ARL Token (Deezer FLAC)

Para descargas en calidad FLAC Lossless se requiere un token ARL de Deezer:

1. Abre la app en el navegador → ⚙️ (Configuración)
2. Pega tu token ARL de Deezer
3. Selecciona calidad **FLAC** al descargar

---

## 📡 Endpoints Principales

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/api/health` | Estado del servidor |
| `GET` | `/api/search?q=...&engine=youtube` | Buscar canciones |
| `GET` | `/api/search/albums?q=...` | Buscar álbumes |
| `POST` | `/api/download` | Descargar canción |
| `POST` | `/api/download/album` | Descargar álbum completo |
| `GET` | `/api/download/queue` | Cola de descargas |
| `GET` | `/api/library` | Historial de canciones descargadas |
| `GET` | `/api/favorites` | Canciones marcadas como favoritas |
| `WS` | `/ws/downloads` | WebSocket de progreso en tiempo real |
