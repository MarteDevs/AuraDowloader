const TOKEN_KEY = 'aura.authToken.v1';

function getToken() {
  try {
    return localStorage.getItem(TOKEN_KEY) || '';
  } catch {
    return '';
  }
}

export class DownloadWebSocket {
  constructor(onMessageCallback) {
    this.onMessage = onMessageCallback;
    this.ws = null;
    this.reconnectTimer = null;
    this.isClosedManually = false;
    this.reconnectDelay = 1000; // start at 1s, back off up to 30s
  }

  connect() {
    this.isClosedManually = false;

    let base;
    if (import.meta.env.VITE_WS_BASE_URL) {
      base = `${import.meta.env.VITE_WS_BASE_URL}/ws/downloads`;
    } else {
      // Auto-detect protocol and host from current browser location
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const host = window.location.host;
      base = `${protocol}//${host}/ws/downloads`;
    }

    const token = getToken();
    const wsUrl = token ? `${base}?token=${encodeURIComponent(token)}` : base;

    try {
      this.ws = new WebSocket(wsUrl);

      this.ws.onopen = () => {
        console.log('[WebSocket] Connected to Aura Download Feed');
        this.reconnectDelay = 1000; // reset backoff on successful connection
        if (this.reconnectTimer) {
          clearTimeout(this.reconnectTimer);
          this.reconnectTimer = null;
        }
      };

      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (this.onMessage) {
            this.onMessage(data);
          }
        } catch (err) {
          console.error('[WebSocket] Error parsing message', err);
        }
      };

      this.ws.onclose = (e) => {
        console.log('[WebSocket] Connection closed', e.code);
        if (e.code === 1008) {
          // Policy violation — token rejected. Stop reconnecting.
          return;
        }
        if (!this.isClosedManually) {
          this.scheduleReconnect();
        }
      };

      this.ws.onerror = (err) => {
        console.error('[WebSocket] Error', err);
        this.ws?.close();
      };
    } catch (e) {
      console.error('[WebSocket] Exception during connect', e);
      this.scheduleReconnect();
    }
  }

  scheduleReconnect() {
    if (this.reconnectTimer || this.isClosedManually) return;
    const delay = Math.min(this.reconnectDelay, 30000);
    console.log(`[WebSocket] Reconnecting in ${delay}ms...`);
    this.reconnectTimer = setTimeout(() => {
      this.reconnectTimer = null;
      this.reconnectDelay = Math.min(this.reconnectDelay * 2, 30000);
      this.connect();
    }, delay);
  }

  close() {
    this.isClosedManually = true;
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
    if (this.ws) {
      this.ws.close();
    }
  }
}

