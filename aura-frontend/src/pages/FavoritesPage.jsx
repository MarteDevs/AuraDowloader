import { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { Heart, Disc, Library as LibraryIcon } from 'lucide-react';
import { api } from '../services/api';
import { SkeletonGrid } from '../components/SkeletonGrid';

export function FavoritesPage() {
  const [tracks, setTracks] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  const load = useCallback(async () => {
    setIsLoading(true);
    try {
      const data = await api.getFavorites();
      setTracks(data?.tracks || []);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => { load(); }, [load]);

  const handleToggleFav = async (id) => {
    try {
      await api.toggleFavorite(id);
      setTracks((prev) => prev.filter((t) => t.id !== id));
    } catch {
      // ignore
    }
  };

  return (
    <section className="space-y-5 animate-fade-in" aria-labelledby="favorites-title">
      <div className="flex items-center justify-between border-b border-slate-800/80 pb-3">
        <h2 id="favorites-title" className="text-2xl font-bold text-slate-100 flex items-center gap-2">
          <Heart className="w-6 h-6 text-rose-400 fill-rose-400" aria-hidden="true" />
          Favoritos
        </h2>
        <Link
          to="/library"
          className="text-xs font-semibold text-indigo-300 hover:text-indigo-200 flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-indigo-500/10 border border-indigo-500/20 transition-colors"
        >
          <LibraryIcon className="w-3.5 h-3.5" aria-hidden="true" />
          Ver biblioteca
        </Link>
      </div>

      {isLoading ? (
        <SkeletonGrid count={6} />
      ) : tracks.length === 0 ? (
        <div className="glass-panel rounded-2xl p-12 text-center space-y-3">
          <Heart className="w-12 h-12 text-slate-600 mx-auto" aria-hidden="true" />
          <p className="text-base font-semibold text-slate-300">Aún no tienes favoritos.</p>
          <p className="text-xs text-slate-500">Pulsa el corazón en cualquier canción de tu biblioteca para guardarla aquí.</p>
        </div>
      ) : (
        <ul className="space-y-2">
          {tracks.map((t) => (
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

              <button
                onClick={() => handleToggleFav(t.id)}
                className="p-1.5 rounded-lg hover:bg-slate-700 transition-colors"
                aria-label="Quitar de favoritos"
              >
                <Heart className="w-4 h-4 fill-rose-400 text-rose-400" aria-hidden="true" />
              </button>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}

