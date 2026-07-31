import React from 'react';
import { Disc3, Settings, DownloadCloud, Activity } from 'lucide-react';

export function Header({ isOnline, queueCount, onOpenSettings, onToggleQueue }) {
  return (
    <header className="sticky top-0 z-40 w-full glass-panel border-b border-slate-800/80 px-6 py-4">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        {/* Brand */}
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 via-purple-600 to-pink-500 flex items-center justify-center shadow-lg shadow-indigo-500/20">
            <Disc3 className="w-6 h-6 text-white animate-spin-slow" />
          </div>
          <div>
            <h1 className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white via-slate-100 to-slate-400">
              Aura <span className="text-indigo-400 font-normal">Music</span>
            </h1>
            <p className="text-xs text-slate-400 font-medium">Audiophile & Lossless Downloader</p>
          </div>
        </div>

        {/* Server Status & Controls */}
        <div className="flex items-center gap-3">
          {/* Status badge */}
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-900/60 border border-slate-800 text-xs">
            <span className={`w-2 h-2 rounded-full ${isOnline ? 'bg-emerald-500 animate-pulse' : 'bg-rose-500'}`} />
            <span className="text-slate-300 font-medium hidden sm:inline">
              {isOnline ? 'Motor Conectado' : 'Sin Conexión'}
            </span>
          </div>

          {/* Queue Button */}
          <button
            onClick={onToggleQueue}
            className="relative flex items-center gap-2 px-4 py-2 rounded-xl bg-slate-800/80 hover:bg-slate-700/80 border border-slate-700/60 text-slate-200 text-sm font-medium transition-all"
          >
            <DownloadCloud className="w-4 h-4 text-indigo-400" />
            <span className="hidden sm:inline">Descargas</span>
            {queueCount > 0 && (
              <span className="ml-1 px-2 py-0.5 rounded-full bg-indigo-600 text-white text-xs font-bold shadow-sm">
                {queueCount}
              </span>
            )}
          </button>

          {/* Settings Button */}
          <button
            onClick={onOpenSettings}
            className="p-2 rounded-xl bg-slate-800/80 hover:bg-slate-700/80 border border-slate-700/60 text-slate-300 hover:text-white transition-all"
            title="Configuración y Token ARL"
          >
            <Settings className="w-5 h-5" />
          </button>
        </div>
      </div>
    </header>
  );
}
