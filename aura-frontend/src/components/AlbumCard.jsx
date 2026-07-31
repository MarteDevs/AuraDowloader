import React, { useState } from 'react';
import { Disc, Download, ListMusic, Loader2, X, Music } from 'lucide-react';
import { api } from '../services/api';

export function AlbumCard({ album, onDownloadAlbum, onDownloadSingleTrack }) {
  const [isDownloading, setIsDownloading] = useState(false);
  const [selectedQuality, setSelectedQuality] = useState(
    album.engine === 'deezer' ? 'flac' : '320k'
  );
  const [showTracklist, setShowTracklist] = useState(false);
  const [tracks, setTracks] = useState([]);
  const [isLoadingTracks, setIsLoadingTracks] = useState(false);

  const handleDownloadFullAlbum = async () => {
    setIsDownloading(true);
    try {
      let albumTracks = tracks;
      if (albumTracks.length === 0) {
        const data = await api.getAlbumTracks(album.id, album.engine);
        albumTracks = data.tracks || [];
        setTracks(albumTracks);
      }

      if (albumTracks.length === 0) {
        alert('No se pudieron obtener las canciones de este álbum.');
        return;
      }

      await onDownloadAlbum({
        ...album,
        tracks: albumTracks
      }, selectedQuality);

    } catch (err) {
      alert('Error descargando el álbum: ' + err.message);
    } finally {
      setIsDownloading(false);
    }
  };

  const handleOpenTracklist = async () => {
    setShowTracklist(true);
    if (tracks.length === 0) {
      setIsLoadingTracks(true);
      try {
        const data = await api.getAlbumTracks(album.id, album.engine);
        setTracks(data.tracks || []);
      } catch (err) {
        console.error('Error fetching album tracks', err);
      } finally {
        setIsLoadingTracks(false);
      }
    }
  };

  return (
    <>
      <div className="group relative glass-panel rounded-2xl p-4 hover:border-indigo-500/40 hover:bg-slate-800/40 transition-all duration-300 flex flex-col justify-between shadow-lg">
        <div>
          {/* Cover & Track Count Badge */}
          <div className="relative aspect-square w-full rounded-xl overflow-hidden bg-slate-900 mb-3 group-hover:shadow-indigo-500/10 transition-shadow">
            {album.thumbnail ? (
              <img
                src={album.thumbnail}
                alt={album.title}
                className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                loading="lazy"
              />
            ) : (
              <div className="w-full h-full flex items-center justify-center bg-slate-800">
                <Disc className="w-12 h-12 text-slate-600" />
              </div>
            )}

            {/* Album Badge */}
            <div className="absolute top-2 left-2 flex items-center gap-1 px-2.5 py-1 rounded-md bg-slate-950/85 backdrop-blur-md text-indigo-300 text-[11px] font-semibold border border-indigo-500/30 shadow-md">
              <Disc className="w-3 h-3 text-indigo-400" />
              Álbum / Disco
            </div>

            {/* Tracks Count Badge */}
            {album.nb_tracks > 0 && (
              <div className="absolute bottom-2 right-2 flex items-center gap-1 px-2 py-0.5 rounded-md bg-slate-950/85 backdrop-blur-md text-[11px] font-medium text-slate-300">
                <ListMusic className="w-3 h-3 text-slate-400" />
                {album.nb_tracks} Pistas
              </div>
            )}
          </div>

          {/* Title & Artist */}
          <div className="space-y-1 mb-3">
            <h3 className="font-bold text-slate-100 text-sm line-clamp-1 group-hover:text-indigo-300 transition-colors" title={album.title}>
              {album.title}
            </h3>
            <p className="text-xs text-slate-400 line-clamp-1 font-medium" title={album.artist}>
              {album.artist}
            </p>
          </div>
        </div>

        {/* Action Footer */}
        <div className="pt-3 mt-2 border-t border-slate-800/80 space-y-2">
          <select
            value={selectedQuality}
            onChange={(e) => setSelectedQuality(e.target.value)}
            className="w-full bg-slate-900/90 text-slate-300 text-xs font-semibold px-2.5 py-1.5 rounded-lg border border-slate-700/80 focus:outline-none focus:border-indigo-500 cursor-pointer"
          >
            {album.engine === 'deezer' && <option value="flac">FLAC Lossless</option>}
            <option value="320k">MP3 320kbps (HQ)</option>
            <option value="standard">MP3 160kbps</option>
          </select>

          <div className="grid grid-cols-2 gap-2">
            <button
              onClick={handleOpenTracklist}
              className="flex items-center justify-center gap-1.5 px-2.5 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold border border-slate-700/80 transition-all"
            >
              <ListMusic className="w-3.5 h-3.5 text-indigo-400" />
              <span>Ver Pistas</span>
            </button>

            <button
              onClick={handleDownloadFullAlbum}
              disabled={isDownloading}
              className="flex items-center justify-center gap-1.5 px-2.5 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold shadow-md shadow-indigo-600/20 active:scale-95 transition-all disabled:opacity-50"
            >
              {isDownloading ? (
                <Loader2 className="w-3.5 h-3.5 animate-spin" />
              ) : (
                <>
                  <Download className="w-3.5 h-3.5" />
                  <span>Álbum</span>
                </>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Tracklist Modal */}
      {showTracklist && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/75 backdrop-blur-md animate-fade-in">
          <div className="w-full max-w-xl glass-panel rounded-2xl border border-slate-800 shadow-2xl overflow-hidden flex flex-col max-h-[85vh]">
            {/* Header */}
            <div className="p-5 border-b border-slate-800 flex items-center justify-between bg-slate-900/90">
              <div className="flex items-center gap-3">
                <Disc className="w-6 h-6 text-indigo-400" />
                <div>
                  <h3 className="font-bold text-slate-100 text-base">{album.title}</h3>
                  <p className="text-xs text-slate-400">{album.artist} • {tracks.length} canciones</p>
                </div>
              </div>
              <button
                onClick={() => setShowTracklist(false)}
                className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Tracklist Content */}
            <div className="flex-1 overflow-y-auto p-4 space-y-2">
              {isLoadingTracks ? (
                <div className="py-12 text-center space-y-2">
                  <Loader2 className="w-8 h-8 text-indigo-400 animate-spin mx-auto" />
                  <p className="text-xs text-slate-400 font-medium">Obteniendo lista de canciones del álbum...</p>
                </div>
              ) : tracks.length === 0 ? (
                <p className="py-8 text-center text-xs text-slate-400">No se encontraron pistas detalladas.</p>
              ) : (
                tracks.map((track, idx) => (
                  <div
                    key={track.id || idx}
                    className="flex items-center justify-between p-3 rounded-xl bg-slate-900/60 border border-slate-800/60 hover:bg-slate-800/40 transition-colors"
                  >
                    <div className="flex items-center gap-3 min-w-0">
                      <span className="text-xs font-mono font-bold text-slate-500 w-5 text-right">
                        {track.track_number || idx + 1}
                      </span>
                      <div className="min-w-0">
                        <h4 className="text-xs font-bold text-slate-100 truncate">{track.title}</h4>
                        <p className="text-[11px] text-slate-400 truncate">{track.artist}</p>
                      </div>
                    </div>

                    <button
                      onClick={() => onDownloadSingleTrack(track, selectedQuality)}
                      className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-indigo-600/20 hover:bg-indigo-600 text-indigo-300 hover:text-white border border-indigo-500/30 text-xs font-semibold transition-all"
                    >
                      <Download className="w-3.5 h-3.5" />
                      <span>Descargar</span>
                    </button>
                  </div>
                ))
              )}
            </div>

            {/* Modal Footer */}
            <div className="p-4 border-t border-slate-800 bg-slate-900/90 flex justify-between items-center">
              <span className="text-xs text-slate-400">Calidad: <strong className="text-indigo-400 uppercase">{selectedQuality}</strong></span>
              <button
                onClick={handleDownloadFullAlbum}
                disabled={isDownloading}
                className="flex items-center gap-2 px-5 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold shadow-lg shadow-indigo-600/25 transition-all"
              >
                <Download className="w-4 h-4" />
                Descargar Álbum Completo ({tracks.length} Pistas)
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
