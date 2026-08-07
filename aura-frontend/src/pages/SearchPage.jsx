import { useState } from 'react';
import { toast } from 'sonner';
import { Sparkles, Music, Disc, ShieldCheck, Download, Radio } from 'lucide-react';
import { SearchBar } from '../components/SearchBar';
import { SongCard } from '../components/SongCard';
import { AlbumCard } from '../components/AlbumCard';
import { SkeletonGrid } from '../components/SkeletonGrid';
import { api } from '../services/api';

export function SearchPage({ onDownloaded }) {
  const [searchResults, setSearchResults] = useState([]);
  const [isSearching, setIsSearching] = useState(false);
  const [activeEngine, setActiveEngine] = useState('youtube');
  const [searchType, setSearchType] = useState('tracks');
  const [hasSearched, setHasSearched] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  const handleSearch = async (query) => {
    setIsSearching(true);
    setHasSearched(true);
    setSearchQuery(query);
    setSearchResults([]);
    try {
      const data = searchType === 'albums'
        ? await api.searchAlbums(query, activeEngine)
        : await api.search(query, activeEngine);
      setSearchResults(Array.isArray(data?.results) ? data.results : []);
    } catch (err) {
      toast.error('Búsqueda fallida', { description: err.message });
      setSearchResults([]);
    } finally {
      setIsSearching(false);
    }
  };

  const handleDownload = async (track, quality) => {
    try {
      await api.startDownload(track, quality);
      toast.success(`Añadido: ${track.title}`, { description: `Calidad: ${quality.toUpperCase()}` });
      if (onDownloaded) onDownloaded();
    } catch (err) {
      toast.error('No se pudo iniciar la descarga', { description: err.message });
    }
  };

  const handleDownloadAlbum = async (albumData, quality) => {
    try {
      const result = await api.startAlbumDownload(albumData, quality);
      toast.success(`Álbum en cola: ${albumData.title}`, {
        description: `${result.total_tracks} pistas añadidas`,
      });
      if (onDownloaded) onDownloaded();
    } catch (err) {
      toast.error('No se pudo iniciar el álbum', { description: err.message });
    }
  };

  return (
    <>
      <section className="text-center space-y-6 pt-4" aria-labelledby="search-hero">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-xs font-semibold">
          <Sparkles className="w-3.5 h-3.5" aria-hidden="true" />
          Descargas de Alta Fidelidad en Formato Lossless (FLAC & 320k)
        </div>

        <h2 id="search-hero" className="text-4xl sm:text-5xl font-extrabold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-white via-slate-100 to-indigo-200">
          Encuentra y Descarga tu Música en <span className="text-indigo-400">Máxima Calidad</span>
        </h2>

        <SearchBar
          onSearch={handleSearch}
          isLoading={isSearching}
          activeEngine={activeEngine}
          setEngine={setActiveEngine}
          searchType={searchType}
          setSearchType={setSearchType}
        />
      </section>

      {hasSearched && (
        <section className="space-y-5 animate-fade-in pt-2" aria-label="Resultados de búsqueda">
          <div className="flex items-center justify-between border-b border-slate-800/80 pb-3">
            <h3 className="text-lg font-bold text-slate-100 flex items-center gap-2">
              {searchType === 'albums' ? (
                <Disc className="w-5 h-5 text-indigo-400" aria-hidden="true" />
              ) : (
                <Music className="w-5 h-5 text-indigo-400" aria-hidden="true" />
              )}
              Resultados para <span className="text-indigo-300">"{searchQuery}"</span>
            </h3>
            <span className="text-xs text-slate-400 font-medium">
              {searchResults.length} {searchType === 'albums' ? 'álbumes encontrados' : 'canciones encontradas'}
            </span>
          </div>

          {isSearching ? (
            <SkeletonGrid count={8} />
          ) : searchResults.length === 0 ? (
            <div className="glass-panel rounded-2xl p-12 text-center space-y-3">
              <Radio className="w-12 h-12 text-slate-600 mx-auto" aria-hidden="true" />
              <p className="text-base font-semibold text-slate-300">No se encontraron resultados para tu búsqueda.</p>
              <p className="text-xs text-slate-500">Prueba cambiando las palabras clave o alternando entre el motor YouTube y Deezer.</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 2xl:grid-cols-5 gap-5">
              {searchResults.map((item) =>
                searchType === 'albums' ? (
                  <AlbumCard
                    key={item.id}
                    album={item}
                    onDownloadAlbum={handleDownloadAlbum}
                    onDownloadSingleTrack={handleDownload}
                  />
                ) : (
                  <SongCard key={item.id} track={item} onDownload={handleDownload} />
                )
              )}
            </div>
          )}
        </section>
      )}

      {!hasSearched && (
        <section className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-6" aria-label="Características">
          <FeatureCard
            icon={<Sparkles className="w-5 h-5" />}
            color="amber"
            title="Calidad FLAC Lossless"
            description="Conecta tu Token ARL de Deezer para descargar archivos máster de estudio a 16-bit / 44.1kHz con compresión sin pérdida."
          />
          <FeatureCard
            icon={<ShieldCheck className="w-5 h-5" />}
            color="indigo"
            title="Etiquetado Automático ID3"
            description="Cada descarga incluye la carátula del álbum en alta definición, nombre del artista, título y metadatos limpios."
          />
          <FeatureCard
            icon={<Download className="w-5 h-5" />}
            color="purple"
            title="Descargas Simultáneas"
            description="Procesamiento asíncrono que permite añadir múltiples archivos en cola con avance en tiempo real y velocidad medida."
          />
        </section>
      )}
    </>
  );
}

function FeatureCard({ icon, color, title, description }) {
  const colorClasses = {
    amber: 'bg-amber-500/10 border-amber-500/20 text-amber-400',
    indigo: 'bg-indigo-500/10 border-indigo-500/20 text-indigo-400',
    purple: 'bg-purple-500/10 border-purple-500/20 text-purple-400',
  }[color];

  return (
    <div className="glass-panel p-6 rounded-2xl space-y-3 border border-slate-800/80">
      <div className={`w-10 h-10 rounded-xl border flex items-center justify-center ${colorClasses}`}>
        {icon}
      </div>
      <h3 className="font-bold text-slate-100 text-base">{title}</h3>
      <p className="text-xs text-slate-400 leading-relaxed">{description}</p>
    </div>
  );
}

