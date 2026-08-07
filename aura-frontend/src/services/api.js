import axios from 'axios';

// In dev: Vite proxies /api -> localhost:8000, so we use relative /api
// In production (VPS): VITE_API_BASE_URL=http://your-vps-ip:8000, so we use absolute URL
const API_BASE = import.meta.env.VITE_API_BASE_URL
  ? `${import.meta.env.VITE_API_BASE_URL}/api`
  : '/api';

const TOKEN_KEY = 'aura.authToken.v1';

export const tokenStore = {
  get: () => (typeof localStorage !== 'undefined' ? localStorage.getItem(TOKEN_KEY) || '' : ''),
  set: (t) => localStorage.setItem(TOKEN_KEY, t),
  clear: () => localStorage.removeItem(TOKEN_KEY),
};

const client = axios.create({ baseURL: API_BASE });

client.interceptors.request.use((config) => {
  const token = tokenStore.get();
  if (token) {
    config.headers = config.headers || {};
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

client.interceptors.response.use(
  (r) => r,
  (err) => {
    if (err.response?.status === 401) {
      // Token invalid or expired — drop it so the Login screen re-mounts.
      tokenStore.clear();
      if (typeof window !== 'undefined') {
        window.dispatchEvent(new CustomEvent('aura:auth-expired'));
      }
    }
    return Promise.reject(err);
  }
);

export const api = {
  async authStatus() {
    const res = await client.get('/auth/status');
    return res.data;
  },

  async login(token) {
    await client.post('/auth/login', { token });
    tokenStore.set(token);
  },

  logout() {
    tokenStore.clear();
  },

  async search(query, engine = 'youtube') {
    const res = await client.get('/search', { params: { q: query, engine } });
    return res.data;
  },

  async searchAlbums(query, engine = 'youtube') {
    const res = await client.get('/search/albums', { params: { q: query, engine } });
    return res.data;
  },

  async getAlbumTracks(albumId, engine = 'youtube') {
    const res = await client.get(`/album/${albumId}/tracks`, { params: { engine } });
    return res.data;
  },

  async startDownload(track, quality = '320k') {
    const res = await client.post('/download', {
      id: track.id,
      title: track.title,
      artist: track.artist,
      thumbnail: track.thumbnail,
      url: track.url || '',
      engine: track.engine || 'youtube',
      quality,
    });
    return res.data;
  },

  async startAlbumDownload(albumData, quality = '320k') {
    const res = await client.post('/download/album', {
      album_id: albumData.id,
      album_title: albumData.title,
      artist: albumData.artist,
      engine: albumData.engine || 'youtube',
      quality,
      tracks: albumData.tracks,
    });
    return res.data;
  },

  async getQueue() {
    const res = await client.get('/download/queue');
    return res.data;
  },

  async cancelDownload(downloadId) {
    const res = await client.post(`/download/cancel/${downloadId}`);
    return res.data;
  },

  async retryDownload(downloadId) {
    const res = await client.post(`/download/retry/${downloadId}`);
    return res.data;
  },

  async removeDownload(downloadId) {
    const res = await client.delete(`/download/${downloadId}`);
    return res.data;
  },

  async getLibrary() {
    const res = await client.get('/library');
    return res.data;
  },

  async getFavorites() {
    const res = await client.get('/favorites');
    return res.data;
  },

  async toggleFavorite(trackId) {
    const res = await client.post(`/favorites/${trackId}/toggle`);
    return res.data;
  },

  async getSettings() {
    const res = await client.get('/settings');
    return res.data;
  },

  async saveSettings(settingsData) {
    const res = await client.post('/settings', settingsData);
    return res.data;
  },

  async checkHealth() {
    try {
      const res = await client.get('/health', { timeout: 3000 });
      return res.data?.status === 'online';
    } catch {
      return false;
    }
  },

  /**
   * Build a URL to download a file. The backend serves the file via
   * /api/download/file/{id} but the axios client uses the same Authorization
   * header. Since <a download> can't send headers, we use a small route that
   * accepts the token in the query string for this one endpoint.
   */
  getDownloadFileUrl(downloadId) {
    const token = tokenStore.get();
    return token
      ? `${API_BASE}/download/file/${downloadId}?token=${encodeURIComponent(token)}`
      : `${API_BASE}/download/file/${downloadId}`;
  },
};
