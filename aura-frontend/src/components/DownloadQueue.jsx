import React from 'react';
import { X, Download, CheckCircle2, AlertCircle, Loader2, FileAudio, FolderDown } from 'lucide-react';
import { api } from '../services/api';

export function DownloadQueue({ isOpen, onClose, queue }) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex justify-end bg-slate-950/60 backdrop-blur-sm animate-fade-in">
      <div className="w-full max-w-md bg-slate-900 border-l border-slate-800 h-full flex flex-col shadow-2xl">
        {/* Queue Header */}
        <div className="p-5 border-b border-slate-800 flex items-center justify-between bg-slate-900/90">
          <div className="flex items-center gap-3">
            <FolderDown className="w-5 h-5 text-indigo-400" />
            <h2 className="font-bold text-slate-100 text-lg">Cola de Descargas</h2>
            <span className="px-2 py-0.5 rounded-full bg-slate-800 text-slate-300 text-xs font-semibold">
              {queue.length}
            </span>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Downloads List */}
        <div className="flex-1 overflow-y-auto p-4 space-y-3">
          {queue.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-center p-6 space-y-3 text-slate-500">
              <FileAudio className="w-12 h-12 stroke-[1.5]" />
              <p className="text-sm font-medium">No hay descargas en curso ni completadas.</p>
              <p className="text-xs text-slate-600">Busca canciones e inicia la descarga para ver el avance aquí.</p>
            </div>
          ) : (
            queue.map((item) => (
              <div
                key={item.id}
                className="p-3.5 rounded-xl bg-slate-850/80 border border-slate-800/80 space-y-2 relative overflow-hidden"
              >
                {/* Track Info Header */}
                <div className="flex items-center gap-3">
                  {item.thumbnail ? (
                    <img src={item.thumbnail} alt={item.title} className="w-11 h-11 rounded-lg object-cover bg-slate-800" />
                  ) : (
                    <div className="w-11 h-11 rounded-lg bg-slate-800 flex items-center justify-center text-slate-500">
                      <FileAudio className="w-5 h-5" />
                    </div>
                  )}

                  <div className="flex-1 min-w-0">
                    <h4 className="text-xs font-bold text-slate-100 truncate" title={item.title}>
                      {item.title}
                    </h4>
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

                {/* Progress Bar & Status */}
                <div className="space-y-1">
                  <div className="flex justify-between items-center text-[11px] font-semibold">
                    <span className="text-slate-400">
                      {item.status === 'queued' && 'En cola...'}
                      {item.status === 'downloading' && `Descargando (${item.progress}%)`}
                      {item.status === 'processing' && 'Etiquetando ID3 / FFmpeg...'}
                      {item.status === 'completed' && 'Completado'}
                      {item.status === 'error' && 'Error'}
                    </span>
                    {item.status === 'completed' && <CheckCircle2 className="w-4 h-4 text-emerald-400" />}
                    {item.status === 'error' && <AlertCircle className="w-4 h-4 text-rose-400" />}
                    {(item.status === 'downloading' || item.status === 'processing') && (
                      <Loader2 className="w-3.5 h-3.5 text-indigo-400 animate-spin" />
                    )}
                  </div>

                  <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">
                    <div
                      className={`h-full transition-all duration-300 ${
                        item.status === 'completed'
                          ? 'bg-emerald-500'
                          : item.status === 'error'
                          ? 'bg-rose-500'
                          : 'bg-gradient-to-r from-indigo-500 to-purple-500'
                      }`}
                      style={{ width: `${item.progress}%` }}
                    />
                  </div>
                </div>

                {/* Download File Action */}
                {item.status === 'completed' && (
                  <a
                    href={api.getDownloadFileUrl(item.id)}
                    download
                    className="flex items-center justify-center gap-1.5 w-full py-1.5 rounded-lg bg-emerald-600/20 hover:bg-emerald-600/30 text-emerald-400 border border-emerald-500/30 text-xs font-semibold transition-all mt-2"
                  >
                    <Download className="w-3.5 h-3.5" />
                    Guardar Archivo en Disco
                  </a>
                )}

                {item.error_message && (
                  <p className="text-[10px] text-rose-400 font-mono mt-1 break-words">{item.error_message}</p>
                )}
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
