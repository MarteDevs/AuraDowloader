import { useState, useEffect, useCallback } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { toast } from 'sonner';
import { Header } from './components/Header';
import { DownloadQueue } from './components/DownloadQueue';
import { SettingsModal } from './components/SettingsModal';
import { LoginScreen } from './components/LoginScreen';
import { SearchPage } from './pages/SearchPage';
import { LibraryPage } from './pages/LibraryPage';
import { FavoritesPage } from './pages/FavoritesPage';
import { api } from './services/api';
import { DownloadWebSocket } from './services/websocket';

const QUEUE_STORAGE_KEY = 'aura.downloadQueue.v1';

function loadQueueFromStorage() {
  try {
    const raw = localStorage.getItem(QUEUE_STORAGE_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

export default function App() {
  const [authRequired, setAuthRequired] = useState(null); // null=loading
  const [isAuthenticated, setIsAuthenticated] = useState(() => Boolean(api.tokenStore.get()));
  const [isOnline, setIsOnline] = useState(false);
  const [queue, setQueue] = useState(() => loadQueueFromStorage());
  const [isQueueOpen, setIsQueueOpen] = useState(false);
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);

  // Persist queue across refreshes (only if authenticated, otherwise the
  // data isn't even relevant to the user).
  useEffect(() => {
    if (!isAuthenticated) return;
    try {
      localStorage.setItem(QUEUE_STORAGE_KEY, JSON.stringify(queue));
    } catch {
      // ignore quota errors
    }
  }, [queue, isAuthenticated]);

  // Detect if the server requires auth.
  useEffect(() => {
    let cancelled = false;
    api.authStatus()
      .then((s) => {
        if (cancelled) return;
        setAuthRequired(Boolean(s.auth_required));
        if (!s.auth_required) setIsAuthenticated(true);
      })
      .catch(() => {
        if (cancelled) return;
        setAuthRequired(false);
        setIsAuthenticated(true);
      });
    return () => { cancelled = true; };
  }, []);

  // Listen for 401 events from the axios client.
  useEffect(() => {
    const onExpired = () => {
      api.logout();
      setIsAuthenticated(false);
      toast.error('Tu sesión ha expirado. Vuelve a iniciar sesión.');
    };
    window.addEventListener('aura:auth-expired', onExpired);
    return () => window.removeEventListener('aura:auth-expired', onExpired);
  }, []);

  // Health check every 30s.
  useEffect(() => {
    if (!isAuthenticated) return;
    const check = async () => {
      const online = await api.checkHealth();
      setIsOnline((prev) => {
        if (!prev && online) toast.success('Conectado al motor de Aura');
        if (prev && !online) toast.error('Se perdió la conexión con el backend');
        return online;
      });
    };
    check();
    const interval = setInterval(check, 30000);
    return () => clearInterval(interval);
  }, [isAuthenticated]);

  const fetchQueue = useCallback(async () => {
    try {
      const data = await api.getQueue();
      if (data && Array.isArray(data.items)) {
        setQueue((prev) => {
          const byId = new Map(data.items.map((i) => [i.id, i]));
          for (const local of prev) {
            if (!byId.has(local.id)) byId.set(local.id, local);
          }
          return Array.from(byId.values()).sort((a, b) => (b.created_at ?? 0) - (a.created_at ?? 0));
        });
      }
    } catch {
      // Network error — keep showing the cached queue.
    }
  }, []);

  // Real-time WebSocket connection for download events.
  useEffect(() => {
    if (!isAuthenticated) return undefined;
    fetchQueue();

    const wsClient = new DownloadWebSocket((event) => {
      if (!event || !event.item) return;
      setQueue((prevQueue) => {
        const index = prevQueue.findIndex((i) => i.id === event.item.id);
        if (index !== -1) {
          const updated = [...prevQueue];
          updated[index] = event.item;
          return updated;
        }
        return [event.item, ...prevQueue];
      });

      if (event.type === 'download_completed') {
        toast.success(`✓ ${event.item.title}`, { description: 'Descarga completada' });
      } else if (event.type === 'download_error') {
        toast.error(`✗ ${event.item.title}`, {
          description: event.item.error_message || 'Error en la descarga',
        });
      } else if (event.type === 'download_cancelled') {
        toast.message(`Descarga cancelada: ${event.item.title}`);
      }
    });

    wsClient.connect();
    return () => wsClient.close();
  }, [fetchQueue, isAuthenticated]);

  if (authRequired === null) {
    return (
      <div className="min-h-screen bg-[#0b0f19] flex items-center justify-center text-slate-400 text-sm">
        Conectando...
      </div>
    );
  }

  if (authRequired && !isAuthenticated) {
    return <LoginScreen onAuthenticated={() => setIsAuthenticated(true)} />;
  }

  return (
    <div className="min-h-screen bg-[#0b0f19] text-slate-100 flex flex-col selection:bg-indigo-500 selection:text-white">
      <Header
        isOnline={isOnline}
        queueCount={queue.filter((i) => i.status !== 'completed' && i.status !== 'error' && i.status !== 'cancelled').length}
        onOpenSettings={() => setIsSettingsOpen(true)}
        onToggleQueue={() => setIsQueueOpen(!isQueueOpen)}
      />

      <main className="flex-1 max-w-7xl w-full mx-auto px-6 py-8 space-y-10">
        <Routes>
          <Route path="/" element={<SearchPage onDownloaded={() => setIsQueueOpen(true)} />} />
          <Route path="/library" element={<LibraryPage />} />
          <Route path="/favorites" element={<FavoritesPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>

      <DownloadQueue
        isOpen={isQueueOpen}
        onClose={() => setIsQueueOpen(false)}
        queue={queue}
        onChanged={fetchQueue}
      />

      <SettingsModal
        isOpen={isSettingsOpen}
        onClose={() => setIsSettingsOpen(false)}
      />
    </div>
  );
}

