# 🎵 Aura Music Downloader

Aura es una aplicación cliente-servidor diseñada para buscar, resolver y descargar música en la máxima calidad posible, priorizando formatos **Lossless (FLAC 16-bit/44.1kHz)** con etiquetado automático **ID3** (carátulas HD, artista, álbum, año) y un sistema de **fallback automático** a MP3 320kbps/160kbps a través del motor de YouTube.

---

## 🚀 Requisitos Previos

Antes de iniciar la aplicación, asegúrate de contar con:

- **Python 3.10+** (probado y verificado en Windows usando el lanzador `py` o `python`).
- **Node.js 18+** y **npm** (para la interfaz en React/Vite).

---

## 🛠️ Cómo Levantar la Aplicación

La aplicación consta de dos partes: el **Backend (FastAPI)** y el **Frontend (React + Vite)**. Sigue los siguientes pasos para iniciar ambos componentes:

---

### 1. Iniciar el Backend (Python / FastAPI)

Abre una terminal en la raíz del proyecto y ejecuta:

```powershell
# 1. Navega a la carpeta del backend
cd aura-backend

# 2. Instala las dependencias (solo la primera vez)
py -m pip install -r requirements.txt

# 3. Inicia el servidor del backend
py -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

- **URL de la API**: `http://localhost:8000`
- **Documentación Interactiva (Swagger UI)**: `http://localhost:8000/docs`

> **Nota sobre FFmpeg**: El backend incluye el paquete `static-ffmpeg`, el cual descarga y configura automáticamente los binarios de `ffmpeg` sin requerir instalación manual previa en tu sistema.

---

### 2. Iniciar el Frontend (React + Vite + Tailwind CSS)

En **otra ventana de la terminal**, ejecuta:

```powershell
# 1. Navega a la carpeta del frontend
cd aura-frontend

# 2. Instala las dependencias (solo la primera vez)
npm install

# 3. Inicia el servidor de desarrollo
npm run dev
```

- **URL de la Aplicación Web**: `http://localhost:5173`

Abre tu navegador en `http://localhost:5173` para comenzar a utilizar Aura.

---

## ⚙️ Configuración y Descargas Lossless (FLAC)

### Habilitar Motor Deezer (FLAC 16-bit)
1. Abre la aplicación en el navegador (`http://localhost:5173`).
2. Haz clic en el icono de **Configuración ⚙️** ubicado en la esquina superior derecha del encabezado.
3. En el campo **Token ARL de Deezer**, pega tu token ARL de tu cuenta de Deezer.
4. Presiona **Guardar Ajustes**.
5. ¡Listo! Ahora podrás realizar búsquedas en el motor Deezer y descargar canciones en calidad **FLAC Lossless**.

> **Sistema Fallback**: Si no cuentas con Token ARL o la canción no está disponible en FLAC, Aura cambiará automáticamente al motor de YouTube para entregarte la versión en MP3 a 320kbps con etiquetado ID3.

---

## 📁 Estructura del Proyecto

```text
AuroDowloader/
├── aura-backend/            # Servidor FastAPI (Python)
│   ├── app/
│   │   ├── api/            # Endpoints (/search, /download, /settings)
│   │   ├── core/           # Configuración y utilidades de FFmpeg
│   │   ├── services/       # Motores YouTube, Deezer y cola asíncrona
│   │   └── main.py         # Entrypoint del servidor
│   ├── downloads/          # Carpeta de almacenamiento de audio
│   └── requirements.txt    # Dependencias de Python
│
├── aura-frontend/           # Interfaz de Usuario (React + Vite)
│   ├── src/
│   │   ├── components/     # Header, SearchBar, SongCard, DownloadQueue, Settings
│   │   ├── services/       # Cliente API Axios
│   │   └── App.jsx         # Componente principal
│   └── package.json
│
├── .gitignore               # Exclusión de node_modules, audios y temporales
├── plan-aura.md             # Especificación técnica inicial
└── README.md                # Guía de uso e instalación
```

---

## 🧪 Comandos Útiles

- **Compilar el Frontend para Producción**:
  ```bash
  cd aura-frontend
  npm run build
  ```
- **Verificar Sintaxis del Backend**:
  ```bash
  cd aura-backend
  py -m py_compile app/main.py
  ```
