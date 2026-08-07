import { useEffect, useRef, useCallback } from 'react';
import { X, Download, CheckCircle2, AlertCircle, Loader2, FileAudio, FolderDown, RotateCcw, XCircle, Trash2 } from 'lucide-react';
import { api } from '../services/api';

export function DownloadQueue({ isOpen, onClose, queue, onChanged }) {
  const panelRef = useRef(null);
  const closeBtnRef = useRef(null);

  // Focus trap + Esc to close.
  useEffect(() => {
    if (!isOpen) return;
    const previouslyFocused = document.activeElement;
    closeBtnRef.current?.focus();

    const onKey = (e) => {
      if (e.key === 'Escape') {
        e.preventDefault();
        onClose();
        return;
      }
      if (e.key === 'Tab' && panelRef.current) {
        const focusable = panelRef.current.querySelectorAll(
          'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );
        if (focusable.length === 0) return;
        const first = focusable[0];
        const last = focusable[focusable.length - 1];
        if (e.shiftKey && document.activeElement === first) {
          e.preventDefault();
          last.focus();
        } else if (!e.shiftKey && document.activeElement === last) {
          e.preventDefault();
          first.focus();
        }
      }
    };
    document.addEventListener('keydown', onKey);
    return () => {
      document.removeEventListener('keydown', onKey);
      if (previouslyFocused && typeof previouslyFocused.focus === 'function') {
        previouslyFocused.focus();
      }
    };
  }, [isOpen, onClose]);

  const handleCancel = useCallback(async (id) => {
    try {
      await api.cancelDownload(id);
      if (onChanged) await onChanged();
    } catch {}
  }, [onChanged]);

  const handleRetry = useCallback(async (id) => {
    try {
      await api.retryDownload(id);
      if (onChanged) await onChanged();
    } catch {}
  }, [onChanged]);

  const handleRemove = useCallback(async (id) => {
    try {
      await api.removeDownload(id);
      if (onChanged) await onChanged();
    } catch {}
  }, [onChanged]);

  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex justify-end bg-slate-950/60 backdrop-blur-sm animate-fade-in"
      role="presentation"
      onClick={onClose}
    >
      <div
        ref={panelRef}
        className="w-full max-w-md bg-slate-900 border-l border-slate-800 h-full flex flex-col shadow-2xl"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="p-5 border-b border-slate-800 flex items-center justify-between bg-slate-900/90">
          <div className="flex items-center gap-3">
            <FolderDown className="w-5 h-5 text-indigo-400" aria-hidden="true" />
            <h2 id="queue-title" className="font-bold text-slate-100 text-lg">Cola de Descargas</h2>
            <span className="px-2 py-0.5 rounded-full bg-slate-800 text-slate-300 text-xs font-semibold" aria-label={`${queue.length} elementos`}>
              {queue.length}
            </span>
          </div>
          <button
            ref={closeBtnRef}
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
            aria-label="Cerrar cola de descargas"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-4 space-y-3">
          {queue.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-center p-6 space-y-3 text-slate-500">
              <FileAudio className="w-12 h-12 stroke-[1.5]" aria-hidden="true" />
              <p className="text-sm font-medium">No hay descargas en curso ni completadas.</p>
              <p className="text-xs text-slate-600">Busca canciones e inicia la descarga para ver el avance aquí.</p>
            </div>
          ) : (
            queue.map((item) => (
              <article
                key={item.id}
                className="p-3.5 rounded-xl bg-slate-850/80 border border-slate-800/80 space-y-2 relative overflow-hidden"
                aria-label={`${item.title} por ${item.artist}, estado: ${item.status}`}
              >
                <div className="flex items-center gap-3">
                  {item.thumbnail ? (
                    <img src={item.thumbnail} alt="" className="w-11 h-11 rounded-lg object-cover bg-slate-800" />
                  ) : (
                    <div className="w-11 h-11 rounded-lg bg-slate-800 flex items-center justify-center text-slate-500">
                      <FileAudio className="w-5 h-5" aria-hidden="true" />
                    </div>
                  )}

                  <div className="flex-1 min-w-0">
                    <h4 className="text-xs font-bold text-slate-100 truncate" title={item.title}>{item.title}</h4>
                    <p className="text-[11px] text-slate-400 truncate">{item.artist}</p>
                    <div className="flex items-center gap-2 mt-1">
                      <span className="text-[10px] uppercase font-bold text-indigo-400 bg-indigo-500/10 px-1.5 py-0.5 rounded border border-indigo-500/20">
                        {item.quality}
                      </span>
                      {item.status === 'downloading' && (
                        <span className="text-[10px] text-slate-400 font-mono">
                          {item.speed} • ETA: {item.eta}
                        </span>
                      )}
                    </div>
                  </div>
                </div>

                <div className="space-y-1">
                  <div className="flex justify-between items-center text-[11px] font-semibold">
                    <span className="text-slate-400">
                      {item.status === 'queued' && 'En cola...'}
                      {item.status === 'downloading' && `Descargando (${item.progress}%)`}
                      {item.status === 'processing' && 'Etiquetando ID3 / FFmpeg...'}
                      {item.status === 'completed' && 'Completado'}
                      {item.status === 'error' && 'Error'}
                      {item.status === 'cancelled' && 'Cancelado'}
                    </span>
                    {item.status === 'completed' && <CheckCircle2 className="w-4 h-4 text-emerald-400" aria-label="Completado" />}
                    {item.status === 'error' && <AlertCircle className="w-4 h-4 text-rose-400" aria-label="Error" />}
                    {item.status === 'cancelled' && <XCircle className="w-4 h-4 text-slate-400" aria-label="Cancelado" />}
                    {(item.status === 'downloading' || item.status === 'processing') && (
                      <Loader2 className="w-3.5 h-3.5 text-indigo-400 animate-spin" aria-label="En progreso" />
                    )}
                  </div>

                  <div
                    className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden"
                    role="progressbar"
                    aria-valuenow={Math.round(item.progress)}
                    aria-valuemin={0}
                    aria-valuemax={100}
                    aria-label={`Progreso de ${item.title}`}
                  >
                    <div
                      className={`h-full transition-all duration-300 ${
                        item.status === 'completed'
                          ? 'bg-emerald-500'
                          : item.status === 'error'
                          ? 'bg-rose-500'
                          : item.status === 'cancelled'
                          ? 'bg-slate-600'
                          : 'bg-gradient-to-r from-indigo-500 to-purple-500'
                      }`}
                      style={{ width: `${item.progress}%` }}
                    />
                  </div>
                </div>

                {/* Actions */}
                <div className="flex flex-wrap gap-2 pt-1">
                  {item.status === 'completed' && (
                    <a
                      href={api.getDownloadFileUrl(item.id)}
                      download
                      className="flex items-center justify-center gap-1.5 flex-1 py-1.5 rounded-lg bg-emerald-600/20 hover:bg-emerald-600/30 text-emerald-400 border border-emerald-500/30 text-xs font-semibold transition-all"
                    >
                      <Download className="w-3.5 h-3.5" aria-hidden="true" />
                      Guardar Archivo
                    </a>
                  )}
                  {(item.status === 'error' || item.status === 'cancelled') && (
                    <button
                      onClick={() => handleRetry(item.id)}
                      className="flex items-center justify-center gap-1.5 flex-1 py-1.5 rounded-lg bg-amber-500/15 hover:bg-amber-500/25 text-amber-300 border border-amber-500/30 text-xs font-semibold transition-all"
                    >
                      <RotateCcw className="w-3.5 h-3.5" aria-hidden="true" />
                      Reintentar
                    </button>
                  )}
                  {(item.status === 'queued' || item.status === 'downloading' || item.status === 'processing') && (
                    <button
                      onClick={() => handleCancel(item.id)}
                      className="flex items-center justify-center gap-1.5 flex-1 py-1.5 rounded-lg bg-rose-500/15 hover:bg-rose-500/25 text-rose-300 border border-rose-500/30 text-xs font-semibold transition-all"
                    >
                      <XCircle className="w-3.5 h-3.5" aria-hidden="true" />
                      Cancelar
                    </button>
                  )}
                  <button
                    onClick={() => handleRemove(item.id)}
                    className="flex items-center justify-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-slate-200 border border-slate-700/60 text-xs font-semibold transition-all"
                    aria-label={`Eliminar ${item.title} de la cola`}
                  >
                    <Trash2 className="w-3.5 h-3.5" aria-hidden="true" />
                  </button>
                </div>

                {item.error_message && (
                  <p className="text-[10px] text-rose-400 font-mono mt-1 break-words">{item.error_message}</p>
                )}
              </article>
            ))
          )}
        </div>
      </div>
    </div>
  );
}

