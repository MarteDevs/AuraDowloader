import { NavLink } from 'react-router-dom';
import { Settings, DownloadCloud, Search, Library, Heart } from 'lucide-react';

export function Header({ isOnline, queueCount, onOpenSettings, onToggleQueue }) {
  return (
    <header className="sticky top-0 z-40 w-full glass-panel border-b border-slate-800/80 px-6 py-4">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        {/* Brand */}
        <div className="flex items-center gap-3">
          <div className="relative w-11 h-11 rounded-xl bg-slate-900/80 border border-indigo-500/30 p-1 flex items-center justify-center shadow-lg shadow-indigo-500/20 group">
            <img
              src="/aura-logo.png"
              alt="Aura Logo"
              className="w-full h-full object-contain rounded-lg drop-shadow-md group-hover:scale-105 transition-transform"
            />
          </div>
          <div>
            <h1 className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white via-slate-100 to-slate-400">
              Aura <span className="text-indigo-400 font-normal">Music</span>
            </h1>
            <p className="text-xs text-slate-400 font-medium">Audiophile & Lossless Downloader</p>
          </div>
        </div>

        {/* Nav links (desktop) */}
        <nav aria-label="Navegación principal" className="hidden md:flex items-center gap-1 bg-slate-900/60 p-1.5 rounded-xl border border-slate-800">
          <NavLink
            to="/"
            end
            className={({ isActive }) =>
              `flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                isActive
                  ? 'bg-indigo-600 text-white shadow-md'
                  : 'text-slate-400 hover:text-slate-200'
              }`
            }
          >
            <Search className="w-3.5 h-3.5" aria-hidden="true" />
            Buscar
          </NavLink>
          <NavLink
            to="/library"
            className={({ isActive }) =>
              `flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                isActive
                  ? 'bg-indigo-600 text-white shadow-md'
                  : 'text-slate-400 hover:text-slate-200'
              }`
            }
          >
            <Library className="w-3.5 h-3.5" aria-hidden="true" />
            Biblioteca
          </NavLink>
          <NavLink
            to="/favorites"
            className={({ isActive }) =>
              `flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                isActive
                  ? 'bg-rose-500 text-white shadow-md'
                  : 'text-slate-400 hover:text-slate-200'
              }`
            }
          >
            <Heart className="w-3.5 h-3.5" aria-hidden="true" />
            Favoritos
          </NavLink>
        </nav>

        {/* Server Status & Controls */}
        <div className="flex items-center gap-3">
          <div
            className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-900/60 border border-slate-800 text-xs"
            role="status"
            aria-live="polite"
          >
            <span
              className={`w-2 h-2 rounded-full ${isOnline ? 'bg-emerald-500 animate-pulse' : 'bg-rose-500'}`}
              aria-hidden="true"
            />
            <span className="text-slate-300 font-medium hidden sm:inline">
              {isOnline ? 'Motor Conectado' : 'Sin Conexión'}
            </span>
            <span className="sr-only">{isOnline ? 'Servidor conectado' : 'Servidor desconectado'}</span>
          </div>

          <button
            onClick={onToggleQueue}
            className="relative flex items-center gap-2 px-4 py-2 rounded-xl bg-slate-800/80 hover:bg-slate-700/80 border border-slate-700/60 text-slate-200 text-sm font-medium transition-all"
            aria-label={`Abrir cola de descargas (${queueCount} activas)`}
          >
            <DownloadCloud className="w-4 h-4 text-indigo-400" aria-hidden="true" />
            <span className="hidden sm:inline">Descargas</span>
            {queueCount > 0 && (
              <span
                className="ml-1 px-2 py-0.5 rounded-full bg-indigo-600 text-white text-xs font-bold shadow-sm"
                aria-hidden="true"
              >
                {queueCount}
              </span>
            )}
          </button>

          <button
            onClick={onOpenSettings}
            className="p-2 rounded-xl bg-slate-800/80 hover:bg-slate-700/80 border border-slate-700/60 text-slate-300 hover:text-white transition-all"
            title="Configuración y Token ARL"
            aria-label="Abrir configuración"
          >
            <Settings className="w-5 h-5" aria-hidden="true" />
          </button>
        </div>
      </div>
    </header>
  );
}

