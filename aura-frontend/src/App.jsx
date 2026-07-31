import React, { useState, useEffect } from 'react';
import { Header } from './components/Header';
import { SearchBar } from './components/SearchBar';
import { SongCard } from './components/SongCard';
import { DownloadQueue } from './components/DownloadQueue';
import { SettingsModal } from './components/SettingsModal';
import { api } from './services/api';
import { Sparkles, Music, Disc, ShieldCheck, Download, Radio } from 'lucide-react';

export default function App() {
  const [isOnline, setIsOnline] = useState(false);
  const [searchResults, setSearchResults] = useState([]);
  const [isSearching, setIsSearching] = useState(false);
  const [activeEngine, setActiveEngine] = useState('youtube');
  const [hasSearched, setHasSearched] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  
  const [queue, setQueue] = useState([]);
  const [isQueueOpen, setIsQueueOpen] = useState(false);
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);

  // Health check (check once on mount, then every 30s)
  useEffect(() => {
    const check = async () => {
      const online = await api.checkHealth();
      setIsOnline(online);
    };
    check();
    const interval = setInterval(check, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchQueue = async () => {
    try {
      const data = await api.getQueue();
      if (data && data.items) {
        setQueue(data.items);
      }
    } catch {}
  };

  // Smart Queue polling: only poll while there are active/pending downloads
  const hasActiveDownloads = queue.some(
    (item) => item.status === 'queued' || item.status === 'downloading' || item.status === 'processing'
  );

  useEffect(() => {
    fetchQueue();
  }, []);

  useEffect(() => {
    if (!hasActiveDownloads) return;

    const interval = setInterval(() => {
      fetchQueue();
    }, 2500);

    return () => clearInterval(interval);
  }, [hasActiveDownloads]);

  const handleSearch = async (query) => {
    setIsSearching(true);
    setHasSearched(true);
    setSearchQuery(query);
    try {
      const data = await api.search(query, activeEngine);
      setSearchResults(data.results || []);
    } catch (err) {
      console.error('Search failed', err);
      setSearchResults([]);
    } finally {
      setIsSearching(false);
    }
  };

  const handleDownload = async (track, quality) => {
    try {
      await api.startDownload(track, quality);
      fetchQueue();
      setIsQueueOpen(true);
    } catch (err) {
      alert('Error iniciando descarga: ' + err.message);
    }
  };

  return (
    <div className="min-h-screen bg-[#0b0f19] text-slate-100 flex flex-col selection:bg-indigo-500 selection:text-white">
      {/* Top Header */}
      <Header
        isOnline={isOnline}
        queueCount={queue.filter((i) => i.status !== 'completed' && i.status !== 'error').length}
        onOpenSettings={() => setIsSettingsOpen(true)}
        onToggleQueue={() => setIsQueueOpen(!isQueueOpen)}
      />

      {/* Main Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-6 py-8 space-y-10">
        {/* Search Hero Section */}
        <section className="text-center space-y-6 pt-4">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-xs font-semibold">
            <Sparkles className="w-3.5 h-3.5" />
            Descargas de Alta Fidelidad en Formato Lossless (FLAC & 320k)
          </div>

          <h2 className="text-4xl sm:text-5xl font-extrabold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-white via-slate-100 to-indigo-200">
            Encuentra y Descarga tu Música en <span className="text-indigo-400">Máxima Calidad</span>
          </h2>

          {/* Search Bar */}
          <SearchBar
            onSearch={handleSearch}
            isLoading={isSearching}
            activeEngine={activeEngine}
            setEngine={setActiveEngine}
          />
        </section>

        {/* Results Section */}
        {hasSearched && (
          <section className="space-y-5 animate-fade-in pt-2">
            <div className="flex items-center justify-between border-b border-slate-800/80 pb-3">
              <h3 className="text-lg font-bold text-slate-100 flex items-center gap-2">
                <Music className="w-5 h-5 text-indigo-400" />
                Resultados para <span className="text-indigo-300">"{searchQuery}"</span>
              </h3>
              <span className="text-xs text-slate-400 font-medium">{searchResults.length} canciones encontradas</span>
            </div>

            {searchResults.length === 0 && !isSearching ? (
              <div className="glass-panel rounded-2xl p-12 text-center space-y-3">
                <Radio className="w-12 h-12 text-slate-600 mx-auto" />
                <p className="text-base font-semibold text-slate-300">No se encontraron resultados para tu búsqueda.</p>
                <p className="text-xs text-slate-500">Prueba cambiando las palabras clave o alternando entre el motor YouTube y Deezer.</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 2xl:grid-cols-5 gap-5">
                {searchResults.map((track) => (
                  <SongCard
                    key={track.id}
                    track={track}
                    onDownload={handleDownload}
                  />
                ))}
              </div>
            )}
          </section>
        )}

        {/* Landing Feature Cards if not searched yet */}
        {!hasSearched && (
          <section className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-6">
            <div className="glass-panel p-6 rounded-2xl space-y-3 border border-slate-800/80">
              <div className="w-10 h-10 rounded-xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-amber-400">
                <Sparkles className="w-5 h-5" />
              </div>
              <h3 className="font-bold text-slate-100 text-base">Calidad FLAC Lossless</h3>
              <p className="text-xs text-slate-400 leading-relaxed">
                Conecta tu Token ARL de Deezer para descargar archivos máster de estudio a 16-bit / 44.1kHz con compresión sin pérdida.
              </p>
            </div>

            <div className="glass-panel p-6 rounded-2xl space-y-3 border border-slate-800/80">
              <div className="w-10 h-10 rounded-xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400">
                <ShieldCheck className="w-5 h-5" />
              </div>
              <h3 className="font-bold text-slate-100 text-base">Etiquetado Automático ID3</h3>
              <p className="text-xs text-slate-400 leading-relaxed">
                Cada descarga incluye la carátula del álbum en alta definición, nombre del artista, título y metadatos limpios.
              </p>
            </div>

            <div className="glass-panel p-6 rounded-2xl space-y-3 border border-slate-800/80">
              <div className="w-10 h-10 rounded-xl bg-purple-500/10 border border-purple-500/20 flex items-center justify-center text-purple-400">
                <Download className="w-5 h-5" />
              </div>
              <h3 className="font-bold text-slate-100 text-base">Descargas Simultáneas</h3>
              <p className="text-xs text-slate-400 leading-relaxed">
                Procesamiento asíncrono que permite añadir múltiples archivos en cola con avance en tiempo real y velocidad medida.
              </p>
            </div>
          </section>
        )}
      </main>

      {/* Drawers & Modals */}
      <DownloadQueue
        isOpen={isQueueOpen}
        onClose={() => setIsQueueOpen(false)}
        queue={queue}
      />

      <SettingsModal
        isOpen={isSettingsOpen}
        onClose={() => setIsSettingsOpen(false)}
      />
    </div>
  );
}
