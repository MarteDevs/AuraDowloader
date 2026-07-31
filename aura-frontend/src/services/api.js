import axios from 'axios';

// In dev: Vite proxies /api -> localhost:8000, so we use relative /api
// In production (VPS): VITE_API_BASE_URL=http://your-vps-ip:8000, so we use absolute URL
const API_BASE = import.meta.env.VITE_API_BASE_URL
  ? `${import.meta.env.VITE_API_BASE_URL}/api`
  : '/api';

export const api = {
  async search(query, engine = 'youtube') {
    const res = await axios.get(`${API_BASE}/search`, {
      params: { q: query, engine }
    });
    return res.data;
  },

  async searchAlbums(query, engine = 'youtube') {
    const res = await axios.get(`${API_BASE}/search/albums`, {
      params: { q: query, engine }
    });
    return res.data;
  },

  async getAlbumTracks(albumId, engine = 'youtube') {
    const res = await axios.get(`${API_BASE}/album/${albumId}/tracks`, {
      params: { engine }
    });
    return res.data;
  },

  async startDownload(track, quality = '320k') {
    const res = await axios.post(`${API_BASE}/download`, {
      id: track.id,
      title: track.title,
      artist: track.artist,
      thumbnail: track.thumbnail,
      url: track.url || '',
      engine: track.engine || 'youtube',
      quality: quality
    });
    return res.data;
  },

  async startAlbumDownload(albumData, quality = '320k') {
    const res = await axios.post(`${API_BASE}/download/album`, {
      album_id: albumData.id,
      album_title: albumData.title,
      artist: albumData.artist,
      engine: albumData.engine || 'youtube',
      quality: quality,
      tracks: albumData.tracks
    });
    return res.data;
  },

  async getQueue() {
    const res = await axios.get(`${API_BASE}/download/queue`);
    return res.data;
  },

  async getSettings() {
    const res = await axios.get(`${API_BASE}/settings`);
    return res.data;
  },

  async saveSettings(settingsData) {
    const res = await axios.post(`${API_BASE}/settings`, settingsData);
    return res.data;
  },

  async checkHealth() {
    try {
      const res = await axios.get(`${API_BASE}/health`, { timeout: 3000 });
      return res.data.status === 'online';
    } catch {
      return false;
    }
  },

  getDownloadFileUrl(downloadId) {
    return `${API_BASE}/download/file/${downloadId}`;
  }
};
