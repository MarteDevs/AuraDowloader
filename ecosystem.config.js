// =====================================================
// Aura Music Downloader — PM2 Ecosystem Config
// VPS: aura-downloader.duckdns.org (5.189.171.171)
//
// Uso:
//   pm2 start ecosystem.config.js --env production
//   pm2 start ecosystem.config.js --env development
// =====================================================

module.exports = {
  apps: [
    {
      // ─── Backend FastAPI ──────────────────────────
      name: 'aura-backend',
      cwd: './aura-backend',
      interpreter: 'python3',
      script: '-m',
      args: 'uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2',

      // PRODUCCIÓN — VPS Contabo / DuckDNS
      env_production: {
        NODE_ENV: 'production',
        HOST: '0.0.0.0',
        PORT: '8000',
        DB_HOST: 'localhost',
        DB_PORT: '3306',
        DB_USER: 'aura_user',
        DB_PASSWORD: 'CAMBIA_ESTE_PASSWORD_SEGURO',
        DB_NAME: 'aura_music_db',
        DOWNLOAD_DIR: '/var/www/aura-music/downloads',
        FRONTEND_URL: 'http://aura-downloader.duckdns.org:3000',
      },

      // DESARROLLO — Windows local
      env_development: {
        NODE_ENV: 'development',
        HOST: '127.0.0.1',
        PORT: '8000',
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
      // ─── Frontend (Build estático servido con serve) ──
      name: 'aura-frontend',
      cwd: './aura-frontend',
      script: 'npx',
      args: 'serve dist --listen tcp://0.0.0.0:3000 --single',

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
