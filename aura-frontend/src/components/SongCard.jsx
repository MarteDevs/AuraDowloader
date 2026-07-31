import React, { useState } from 'react';
import { Download, Clock, Music2, Check, Loader2 } from 'lucide-react';
import { QualityBadge } from './QualityBadge';

export function SongCard({ track, onDownload, defaultQuality }) {
  const [isDownloading, setIsDownloading] = useState(false);
  const [selectedQuality, setSelectedQuality] = useState(
    track.engine === 'deezer' && track.has_flac ? 'flac' : '320k'
  );

  const handleDownload = async () => {
    setIsDownloading(true);
    try {
      await onDownload(track, selectedQuality);
    } finally {
      setTimeout(() => setIsDownloading(false), 1200);
    }
  };

  return (
    <div className="group relative glass-panel rounded-2xl p-4 hover:border-indigo-500/40 hover:bg-slate-800/40 transition-all duration-300 flex flex-col justify-between shadow-lg">
      <div>
        {/* Thumbnail & Badges */}
        <div className="relative aspect-square w-full rounded-xl overflow-hidden bg-slate-900 mb-3 group-hover:shadow-indigo-500/10 transition-shadow">
          {track.thumbnail ? (
            <img
              src={track.thumbnail}
              alt={track.title}
              className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
              loading="lazy"
            />
          ) : (
            <div className="w-full h-full flex items-center justify-center bg-slate-800">
              <Music2 className="w-12 h-12 text-slate-600" />
            </div>
          )}

          {/* Overlay Quality Badge */}
          <div className="absolute top-2 left-2">
            <QualityBadge badge={track.quality_badge} engine={track.engine} hasFlac={track.has_flac} />
          </div>

          {/* Duration Badge */}
          <div className="absolute bottom-2 right-2 flex items-center gap-1 px-2 py-0.5 rounded-md bg-slate-950/80 backdrop-blur-md text-[11px] font-medium text-slate-300">
            <Clock className="w-3 h-3 text-slate-400" />
            {track.duration}
          </div>
        </div>

        {/* Track Title & Artist */}
        <div className="space-y-1 mb-3">
          <h3 className="font-bold text-slate-100 text-sm line-clamp-1 group-hover:text-indigo-300 transition-colors" title={track.title}>
            {track.title}
          </h3>
          <p className="text-xs text-slate-400 line-clamp-1 font-medium" title={track.artist}>
            {track.artist}
          </p>
        </div>
      </div>

      {/* Action Footer */}
      <div className="pt-2 border-t border-slate-800/80 flex items-center justify-between gap-2">
        {/* Quality Selector dropdown */}
        <select
          value={selectedQuality}
          onChange={(e) => setSelectedQuality(e.target.value)}
          className="bg-slate-900/90 text-slate-300 text-xs font-semibold px-2 py-1.5 rounded-lg border border-slate-700 focus:outline-none focus:border-indigo-500 cursor-pointer"
        >
          {track.engine === 'deezer' && track.has_flac && (
            <option value="flac">FLAC (Lossless)</option>
          )}
          <option value="320k">MP3 320kbps (HQ)</option>
          <option value="standard">MP3 160kbps</option>
        </select>

        {/* Download Button */}
        <button
          onClick={handleDownload}
          disabled={isDownloading}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-md shadow-indigo-600/20 active:scale-95 transition-all disabled:opacity-50"
        >
          {isDownloading ? (
            <>
              <Loader2 className="w-3.5 h-3.5 animate-spin" />
              <span>Añadiendo</span>
            </>
          ) : (
            <>
              <Download className="w-3.5 h-3.5" />
              <span>Descargar</span>
            </>
          )}
        </button>
      </div>
    </div>
  );
}
