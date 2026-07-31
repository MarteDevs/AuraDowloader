# Aura Music Downloader 🎵

Aura es una aplicación cliente-servidor diseñada para buscar, resolver y descargar música con la máxima calidad posible, priorizando formatos Lossless (FLAC) con un sistema de respaldo automático a calidad estándar (MP3/M4A).

---

## 🎯 Visión General del Proyecto

La aplicación se divide en dos motores de procesamiento principales que se desarrollarán en fases:

*   **Fase 1 (Motor YouTube):** Búsqueda rápida, extracción de metadatos y descarga de audio de alta disponibilidad a 256kbps/160kbps. Servirá como motor principal de búsqueda y sistema de respaldo (Fallback).
*   **Fase 2 (Motor Deezer Lossless):** Integración de tokens ARL para descargas de grado audiófilo (FLAC 16-bit/44.1kHz) y extracción pura de los másters de estudio.

## 🛠�?Stack Tecnológico

**Backend (Motor de Descarga y Resolución)**
*   **Lenguaje:** Python 3.10+
*   **Framework API:** FastAPI (Asíncrono, rápido y autodocumentado)
*   **Extracción de Audio:** `yt-dlp` (YouTube) / Librerías de descifrado (Deezer)
*   **Procesamiento de Audio:** `FFmpeg` (Conversión y empaquetado)
*   **Metadatos (ID3 Tags):** `mutagen` (Inyección de portadas, artista, álbum)

**Frontend (Interfaz de Usuario)**
*   **Core:** React 18 + Vite
*   **Estilos:** Tailwind CSS (Diseño oscuro, minimalista tipo Spotify/Antra)
*   **Iconos:** Lucide React

---

## 🚀 Características y Funcionalidades Principales

### 1. Búsqueda Integrada
*   Barra de búsqueda global que consulta en tiempo real.
*   Visualización de resultados con metadatos ricos: Portada del álbum, Título, Artista, Duración y Tipo (Sencillo, Álbum, Playlist).

### 2. Gestor de Descargas (Download Queue)
*   Panel interactivo para ver el estado de las descargas.
*   Barra de progreso en tiempo real para cada pista.
*   Descargas concurrentes (múltiples archivos a la vez sin bloquear la interfaz).

### 3. Etiquetado Automático (ID3 Tagging)
*   Cada archivo descargado (MP3, M4A o FLAC) incluirá automáticamente:
    *   Carátula del álbum incrustada en el archivo.
    *   Nombre de la pista, Artista, Álbum y Año.

### 4. Selector de Calidad Dinámico
*   **Insignias Visuales (Badges):** La interfaz mostrará si la canción que se está descargando es `Lossless (FLAC)`, `HQ (320kbps)` o `Standard (128/160kbps)`.
*   **Sistema Fallback:** Si un usuario solicita calidad FLAC pero no está disponible, el sistema avisará y descargará automáticamente la mejor versión disponible en YouTube.

### 5. Configuración de Usuario (Settings)
*   Panel para configurar la carpeta de destino de las descargas.
*   Campo seguro para inyectar y guardar el **Token ARL** (necesario para habilitar las descargas Lossless de la Fase 2).

---

## 📂 Arquitectura de Carpetas

El proyecto funciona como un monorepositorio con la siguiente estructura:

```text
aura-music-app/
├── backend/                  # Motor Python / FastAPI
�?  ├── app/
�?  �?  ├── api/              # Controladores (Search, Download)
�?  �?  ├── core/             # Config. de FFmpeg y variables
�?  �?  ├── services/         # Lógica pura (youtube_service.py)
�?  �?  └── main.py           # Entrada del servidor
�?  ├── downloads/            # Destino final de archivos
�?  ├── temp/                 # Caché y procesamiento
�?  └── requirements.txt      
�?└── frontend/                 # Interfaz React / Vite
    ├── src/
    �?  ├── components/       # UI (SearchBar, DownloadQueue, SongCard)
    �?  ├── hooks/            # Estados de React
    �?  ├── services/         # Llamadas API al backend
    �?  └── App.jsx
    └── package.json
	
	
	??? Hoja de Ruta (Roadmap)
Fase 1: MVP - Motor YouTube
[ ] Configurar entorno base (Carpetas, Git, Entornos virtuales).

[ ] Backend: Crear endpoint /api/search usando yt-dlp.

[ ] Frontend: Construir la UI principal (Buscador y Tarjetas de resultados).

[ ] Backend: Integrar FFmpeg y mutagen para el procesado final.

[ ] Backend: Crear endpoint /api/download.

[ ] Frontend: Crear el panel de Cola de Descargas (Progress bar).

Fase 2: Motor Lossless y Refinamiento
[ ] Backend: Crear el m��dulo deezer_service.py.

[ ] Backend: Implementar l��gica para aceptar tokens ARL.

[ ] Frontend: A?adir secci��n de "Configuraci��n" para que el usuario pegue su token.

[ ] Backend: Crear el sistema de "Fallback" (Si falla Deezer -> Usar YouTube).

[ ] Frontend: A?adir insignias de calidad (FLAC, AAC, MP3).