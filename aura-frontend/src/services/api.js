import axios from 'axios';

const API_BASE = '/api';

export const api = {
  async search(query, engine = 'youtube') {
    const res = await axios.get(`${API_BASE}/search`, {
      params: { q: query, engine }
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
