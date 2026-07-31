// =====================================================
// Aura Music Downloader — PM2 Ecosystem Config
// VPS: aura-downloader.duckdns.org (5.189.171.171)
//
// Uso:
//   pm2 start ecosystem.config.js --env production
// =====================================================

module.exports = {
  apps: [
    {
      // ─── Backend FastAPI ──────────────────────────
      name: 'aura-backend',
      cwd: './aura-backend',

      // Apunta directamente al uvicorn del .venv (sin usar -m)
      script: '.venv/bin/uvicorn',
      args: 'app.main:app --host 0.0.0.0 --port 9000 --workers 2',
      interpreter: 'none',

      // PRODUCCIÓN — VPS Contabo / DuckDNS
      env_production: {
        NODE_ENV: 'production',
        HOST: '0.0.0.0',
        PORT: '9000',
        DB_HOST: 'localhost',
        DB_PORT: '3306',
        DB_USER: 'aura_user',
        DB_PASSWORD: 'CAMBIA_ESTE_PASSWORD_SEGURO',
        DB_NAME: 'aura_music_db',
        DOWNLOAD_DIR: '/var/www/AuraDowloader/downloads',
        FRONTEND_URL: 'http://aura-downloader.duckdns.org:3000',
      },

      // DESARROLLO — Windows local (usar .venv\Scripts\uvicorn.exe manualmente)
      env_development: {
        NODE_ENV: 'development',
        HOST: '127.0.0.1',
        PORT: '9000',
        DB_HOST: 'localhost',
        DB_PORT: '3306',
        DB_USER: 'root',
        DB_PASSWORD: 'marte',
        DB_NAME: 'aura_music_db',
        DOWNLOAD_DIR: '',
        FRONTEND_URL: 'http://localhost:5173',
      },

      instances: 1,
      exec_mode: 'fork',
      autorestart: true,
      watch: false,
      max_memory_restart: '500M',

      out_file: './logs/backend-out.log',
      error_file: './logs/backend-error.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss',
      merge_logs: true,
    },

    {
      // ─── Frontend estático con serve ──────────────
      name: 'aura-frontend',
      cwd: './aura-frontend',

      // serve@14: la bandera correcta es -l <puerto>
      script: 'npx',
      args: 'serve dist -l 3000 --single',

      env_production: {
        NODE_ENV: 'production',
      },
      env_development: {
        NODE_ENV: 'development',
      },

      instances: 1,
      exec_mode: 'fork',
      autorestart: true,
      watch: false,

      out_file: './logs/frontend-out.log',
      error_file: './logs/frontend-error.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss',
    },
  ],
};
