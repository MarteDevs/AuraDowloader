import { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { Library as LibraryIcon, Disc, Clock, Heart, Search } from 'lucide-react';
import { api } from '../services/api';
import { SkeletonGrid } from '../components/SkeletonGrid';

export function LibraryPage() {
  const [tracks, setTracks] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [filter, setFilter] = useState('');

  const load = useCallback(async () => {
    setIsLoading(true);
    try {
      const data = await api.getLibrary();
      setTracks(data?.tracks || []);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => { load(); }, [load]);

  const filtered = filter
    ? tracks.filter((t) =>
        (t.title + ' ' + t.artist + ' ' + (t.album || ''))
          .toLowerCase()
          .includes(filter.toLowerCase())
      )
    : tracks;

  const handleToggleFav = async (id) => {
    try {
      await api.toggleFavorite(id);
      setTracks((prev) => prev.map((t) => (t.id === id ? { ...t, is_favorite: !t.is_favorite } : t)));
    } catch {
      // toast handled globally if added
    }
  };

  return (
    <section className="space-y-5 animate-fade-in" aria-labelledby="library-title">
      <div className="flex items-center justify-between border-b border-slate-800/80 pb-3">
        <h2 id="library-title" className="text-2xl font-bold text-slate-100 flex items-center gap-2">
          <LibraryIcon className="w-6 h-6 text-indigo-400" aria-hidden="true" />
          Mi Biblioteca
        </h2>
        <Link
          to="/favorites"
          className="text-xs font-semibold text-rose-300 hover:text-rose-200 flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-rose-500/10 border border-rose-500/20 transition-colors"
        >
          <Heart className="w-3.5 h-3.5" aria-hidden="true" />
          Ver favoritos
        </Link>
      </div>

      {tracks.length > 0 && (
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" aria-hidden="true" />
          <input
            type="search"
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            placeholder="Filtrar por título, artista o álbum..."
            aria-label="Filtrar biblioteca"
            className="w-full glass-input rounded-xl pl-10 pr-4 py-2.5 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/50"
          />
        </div>
      )}

      {isLoading ? (
        <SkeletonGrid count={6} />
      ) : tracks.length === 0 ? (
        <div className="glass-panel rounded-2xl p-12 text-center space-y-3">
          <Disc className="w-12 h-12 text-slate-600 mx-auto" aria-hidden="true" />
          <p className="text-base font-semibold text-slate-300">Tu biblioteca está vacía.</p>
          <p className="text-xs text-slate-500">Las canciones que descargues aparecerán aquí automáticamente.</p>
        </div>
      ) : (
        <ul className="space-y-2">
          {filtered.map((t) => (
            <li
              key={t.id}
              className="flex items-center gap-3 p-3 rounded-xl bg-slate-900/60 border border-slate-800/60 hover:bg-slate-800/40 transition-colors"
            >
              {t.thumbnail ? (
                <img src={t.thumbnail} alt="" className="w-11 h-11 rounded-lg object-cover bg-slate-800" />
              ) : (
                <div className="w-11 h-11 rounded-lg bg-slate-800 flex items-center justify-center text-slate-500">
                  <Disc className="w-5 h-5" aria-hidden="true" />
                </div>
              )}

              <div className="flex-1 min-w-0">
                <p className="text-sm font-bold text-slate-100 truncate">{t.title}</p>
                <p className="text-[11px] text-slate-400 truncate">
                  {t.artist} {t.album ? `• ${t.album}` : ''}
                </p>
              </div>

              <div className="flex items-center gap-3 text-[11px] text-slate-400">
                <span className="hidden sm:flex items-center gap-1">
                  <Clock className="w-3 h-3" aria-hidden="true" />
                  {t.duration || '00:00'}
                </span>
                <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-300 font-mono uppercase">
                  {t.quality}
                </span>
                <button
                  onClick={() => handleToggleFav(t.id)}
                  className="p-1.5 rounded-lg hover:bg-slate-700 transition-colors"
                  aria-label={t.is_favorite ? 'Quitar de favoritos' : 'Añadir a favoritos'}
                  aria-pressed={t.is_favorite}
                >
                  <Heart
                    className={`w-4 h-4 ${t.is_favorite ? 'fill-rose-400 text-rose-400' : 'text-slate-500'}`}
                    aria-hidden="true"
                  />
                </button>
                {t.file_name && (
                  <a
                    href={api.getDownloadFileUrl(t.id)}
                    download
                    className="px-2 py-1 rounded-lg bg-indigo-600/20 hover:bg-indigo-600/30 text-indigo-300 border border-indigo-500/30 transition-colors"
                    aria-label={`Descargar ${t.title}`}
                  >
                    Descargar
                  </a>
                )}
              </div>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}

