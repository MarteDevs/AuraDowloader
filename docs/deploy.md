# Despliegue

## VPS (recomendado: Contabo / Hetzner / cualquier Ubuntu 22.04+)

### 1. Clonar

```bash
ssh root@<vps-ip>
git clone <repo> /var/www/AuraDowloader
cd /var/www/AuraDowloader
```

### 2. Configurar backend

```bash
cd aura-backend
python3 -m venv .venv
.venv/bin/pip install -r requirements-dev.txt

cp .env.example .env
nano .env   # configura DB_PASSWORD y AUTH_TOKEN
```

**Genera un token aleatorio seguro:**

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(48))"
```

Pégalo en `AUTH_TOKEN=` dentro de `.env`.

### 3. Crear DB

```bash
mysql -u root -p
```

```sql
CREATE USER 'aura_user'@'localhost' IDENTIFIED BY 'PASSWORD';
CREATE DATABASE aura_music_db CHARACTER SET utf8mb4;
GRANT ALL ON aura_music_db.* TO 'aura_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### 4. Cookies de YouTube

```bash
# En tu máquina local, exporta las cookies desde Chrome/Firefox a youtube_cookies.txt
# Luego cópialas al servidor:
scp youtube_cookies.txt root@<vps-ip>:/var/www/AuraDowloader/aura-backend/

# O usa el script rotate_cookies.py si lo prefieres automatizado.
```

### 5. Construir frontend

```bash
cd ../aura-frontend
npm ci
npm run build
# El bundle queda en aura-frontend/dist/
```

### 6. Caddy (reverse proxy con HTTPS)

Instala Caddy:

```bash
apt install -y caddy
```

Copia el Caddyfile incluido:

```bash
cp ../deploy/Caddyfile /etc/caddy/sites-enabled/aura
# O reemplaza /etc/caddy/Caddyfile directamente.
```

Activa HSTS en producción: en `aura-backend/.env`:

```
HSTS_ENABLED=1
```

Reinicia Caddy:

```bash
systemctl restart caddy
systemctl status caddy
```

Caddy obtiene el certificado TLS automáticamente vía Let's Encrypt.

### 7. PM2 (process manager)

```bash
npm install -g pm2
cd /var/www/AuraDowloader
# Edita ecosystem.config.js para apuntar a la ruta absoluta del venv.
pm2 start ecosystem.config.js --env production
pm2 save
pm2 startup
```

## Reverse proxy con Nginx (alternativa a Caddy)

Si prefieres Nginx, este bloque en `/etc/nginx/sites-enabled/aura`:

```nginx
server {
    listen 80;
    server_name aura-downloader.duckdns.org;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name aura-downloader.duckdns.org;

    ssl_certificate /etc/letsencrypt/live/aura-downloader.duckdns.org/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/aura-downloader.duckdns.org/privkey.pem;

    client_max_body_size 500M;  # descargas grandes

    location / {
        proxy_pass http://127.0.0.1:5173;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:9000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /ws/ {
        proxy_pass http://127.0.0.1:9000/ws/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

Obtén el certificado:

```bash
apt install certbot python3-certbot-nginx
certbot --nginx -d aura-downloader.duckdns.org
```

## Healthcheck y monitorización

```bash
# Estado
pm2 status
systemctl status caddy

# Logs
pm2 logs aura-backend --lines 200
tail -f /var/log/caddy/aura.log
```
