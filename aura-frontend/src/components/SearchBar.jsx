import React, { useState } from 'react';
import { Search, Youtube, Sparkles, X, Loader2 } from 'lucide-react';

export function SearchBar({ onSearch, isLoading, activeEngine, setEngine, searchType, setSearchType }) {
  const [query, setQuery] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (query.trim()) {
      onSearch(query.trim());
    }
  };

  const handleClear = () => {
    setQuery('');
  };

  const quickSearches = ['Dua Lipa', 'The Weeknd', 'Coldplay', 'Daft Punk', 'Bad Bunny'];

  return (
    <div className="w-full max-w-4xl mx-auto space-y-4">
      <form onSubmit={handleSubmit} className="relative">
        <div className="relative flex items-center glass-input rounded-2xl p-2 shadow-2xl focus-within:ring-2 focus-within:ring-indigo-500/50 transition-all border border-slate-700/80">
          <Search className="w-6 h-6 text-slate-400 ml-3" />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder={searchType === 'albums' ? "Busca álbumes o discos de un artista..." : "Busca por canción, artista o pega una URL..."}
            className="w-full bg-transparent px-4 py-3 text-white placeholder-slate-400 focus:outline-none text-base font-medium"
          />

          {query && (
            <button
              type="button"
              onClick={handleClear}
              className="p-2 text-slate-400 hover:text-white transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          )}

          <button
            type="submit"
            disabled={isLoading || !query.trim()}
            className="flex items-center gap-2 px-6 py-3 rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white font-semibold text-sm shadow-lg shadow-indigo-500/25 disabled:opacity-50 disabled:cursor-not-allowed transition-all min-w-[120px] justify-center"
          >
            {isLoading ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <span>Buscar</span>
            )}
          </button>
        </div>
      </form>

      {/* Mode Selectors & Engine Switches */}
      <div className="flex flex-wrap items-center justify-between gap-3 text-sm">
        {/* Search Type Filter Pills */}
        <div className="flex items-center gap-1.5 bg-slate-900/80 p-1.5 rounded-xl border border-slate-800">
          <button
            type="button"
            onClick={() => setSearchType('tracks')}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              searchType === 'tracks'
                ? 'bg-indigo-600 text-white shadow-md'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            🎵 Canciones
          </button>
          <button
            type="button"
            onClick={() => setSearchType('albums')}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              searchType === 'albums'
                ? 'bg-indigo-600 text-white shadow-md'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            💿 Álbumes Completos
          </button>
        </div>

        {/* Engine Toggle Pills */}
        <div className="flex items-center gap-2 bg-slate-900/80 p-1.5 rounded-xl border border-slate-800">
          <button
            type="button"
            onClick={() => setEngine('youtube')}
            className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              activeEngine === 'youtube'
                ? 'bg-red-500/20 text-red-400 border border-red-500/30'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <Youtube className="w-4 h-4 text-red-500" />
            YouTube
          </button>

          <button
            type="button"
            onClick={() => setEngine('deezer')}
            className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              activeEngine === 'deezer'
                ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <Sparkles className="w-4 h-4 text-amber-400" />
            Deezer FLAC
          </button>
        </div>
      </div>

      {/* Quick Suggestions */}
      <div className="flex items-center gap-2 overflow-x-auto py-1">
        <span className="text-xs text-slate-500 font-medium hidden sm:inline">Tendencias:</span>
        {quickSearches.map((item) => (
          <button
            key={item}
            onClick={() => {
              setQuery(item);
              onSearch(item);
            }}
            className="px-2.5 py-1 rounded-lg bg-slate-800/60 hover:bg-slate-700/60 text-slate-300 text-xs transition-colors border border-slate-700/40"
          >
            {item}
          </button>
        ))}
      </div>
    </div>
  );
}
