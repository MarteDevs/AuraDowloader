import { useState, useEffect, useRef } from 'react';
import { X, Key, Folder, Sparkles, Save, CheckCircle } from 'lucide-react';
import { api } from '../services/api';

export function SettingsModal({ isOpen, onClose }) {
  const [arlToken, setArlToken] = useState('');
  const [defaultQuality, setDefaultQuality] = useState('flac');
  const [downloadDir, setDownloadDir] = useState('');
  const [hasArl, setHasArl] = useState(false);
  const [isSaved, setIsSaved] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const closeBtnRef = useRef(null);

  useEffect(() => {
    if (isOpen) {
      api.getSettings().then((data) => {
        if (data) {
          setHasArl(Boolean(data.has_arl));
          setDefaultQuality(data.default_quality || 'flac');
          setDownloadDir(data.download_dir || '');
        }
      });
      setTimeout(() => closeBtnRef.current?.focus(), 50);
    }
  }, [isOpen]);

  useEffect(() => {
    if (!isOpen) return;
    const onKey = (e) => {
      if (e.key === 'Escape') onClose();
    };
    document.addEventListener('keydown', onKey);
    return () => document.removeEventListener('keydown', onKey);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const handleSave = async (e) => {
    e.preventDefault();
    setIsSaving(true);
    try {
      await api.saveSettings({
        arl_token: arlToken.trim(),
        default_quality: defaultQuality,
        download_dir: downloadDir.trim()
      });
      setIsSaved(true);
      setTimeout(() => setIsSaved(false), 2000);
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/70 backdrop-blur-md animate-fade-in"
      role="presentation"
      onClick={onClose}
    >
      <div
        className="w-full max-w-lg glass-panel rounded-2xl border border-slate-800 shadow-2xl overflow-hidden"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="p-5 border-b border-slate-800 flex items-center justify-between bg-slate-900/90">
          <div className="flex items-center gap-2.5">
            <Sparkles className="w-5 h-5 text-indigo-400" aria-hidden="true" />
            <h2 id="settings-title" className="font-bold text-slate-100 text-lg">Configuración de Aura</h2>
          </div>
          <button
            ref={closeBtnRef}
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
            aria-label="Cerrar configuración"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Form Body */}
        <form onSubmit={handleSave} className="p-6 space-y-5">
          {/* Deezer ARL Token */}
          <div className="space-y-2">
            <label className="flex items-center gap-2 text-xs font-bold text-slate-300 uppercase tracking-wider" htmlFor="arl-token">
              <Key className="w-4 h-4 text-amber-400" aria-hidden="true" />
              Token ARL de Deezer (Habilita descargas FLAC Lossless)
              {hasArl && (
                <span className="ml-auto inline-flex items-center gap-1 px-1.5 py-0.5 rounded bg-emerald-500/15 text-emerald-300 border border-emerald-500/30 normal-case">
                  Configurado
                </span>
              )}
            </label>
            <input
              id="arl-token"
              type="password"
              value={arlToken}
              onChange={(e) => setArlToken(e.target.value)}
              placeholder={hasArl ? '•••••••••••• (dejar vacío para mantener)' : 'Ingresa tu token ARL de Deezer...'}
              className="w-full glass-input rounded-xl px-4 py-2.5 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-amber-500/50"
              autoComplete="off"
            />
            <p className="text-[11px] text-slate-400">
              El token ARL permite acceder al catálogo de alta fidelidad FLAC (16-bit/44.1kHz). Si no se proporciona, el sistema usará automáticamente el motor de YouTube a 320kbps.
            </p>
          </div>

          {/* Calidad por Defecto */}
          <div className="space-y-2">
            <label htmlFor="quality-select" className="text-xs font-bold text-slate-300 uppercase tracking-wider block">
              Calidad de Audio Preferida
            </label>
            <select
              id="quality-select"
              value={defaultQuality}
              onChange={(e) => setDefaultQuality(e.target.value)}
              className="w-full glass-input rounded-xl px-4 py-2.5 text-sm text-slate-100 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 cursor-pointer"
            >
              <option value="flac">FLAC Lossless (Audiófilo 16-bit)</option>
              <option value="320k">MP3 High Quality (320 kbps)</option>
              <option value="standard">MP3 Standard (160 kbps)</option>
            </select>
          </div>

          {/* Carpeta de Descargas */}
          <div className="space-y-2">
            <label htmlFor="download-dir" className="flex items-center gap-2 text-xs font-bold text-slate-300 uppercase tracking-wider">
              <Folder className="w-4 h-4 text-indigo-400" />
              Directorio de Descargas en Servidor
            </label>
            <input
              id="download-dir"
              type="text"
              value={downloadDir}
              onChange={(e) => setDownloadDir(e.target.value)}
              placeholder="Ruta del sistema (ej. aura-backend/downloads)"
              className="w-full glass-input rounded-xl px-4 py-2.5 text-sm text-slate-100 font-mono text-xs focus:outline-none focus:ring-2 focus:ring-indigo-500/50"
            />
          </div>

          {/* Actions */}
          <div className="pt-3 border-t border-slate-800 flex items-center justify-between">
            {isSaved ? (
              <span className="flex items-center gap-1.5 text-xs text-emerald-400 font-semibold">
                <CheckCircle className="w-4 h-4" />
                Ajustes guardados correctamente
              </span>
            ) : (
              <span />
            )}

            <button
              type="submit"
              disabled={isSaving}
              className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-semibold shadow-lg shadow-indigo-600/25 active:scale-95 transition-all"
            >
              <Save className="w-4 h-4" />
              {isSaving ? 'Guardando...' : 'Guardar Ajustes'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

