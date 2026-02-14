# Deploying Django Mombasa on a Linode VPS with Docker

This is an informational guide — no code changes required.

---

## Step 1: Create a Linode Instance

1. Log in to [cloud.linode.com](https://cloud.linode.com)
2. Click **Create Linode**
3. Choose:
   - **Image**: Ubuntu 24.04 LTS
   - **Region**: Closest to your audience (e.g. `eu-west` for East Africa)
   - **Plan**: Shared CPU — **Nanode 1GB** ($5/mo) is fine to start, **Linode 2GB** ($12/mo) recommended
   - **Label**: `djangomombasa`
   - **Root Password**: Set a strong password
   - **SSH Key**: Add your public key (recommended)
4. Click **Create Linode** and wait for it to boot
5. Note the **IP address** shown on the dashboard

---

## Step 2: Connect and Secure the Server

```bash
# SSH into the server
ssh root@YOUR_SERVER_IP

# Update packages
apt update && apt upgrade -y

# Set up firewall
ufw allow OpenSSH
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable
```

---

## Step 3: Install Docker

```bash
# Install Docker
curl -fsSL https://get.docker.com | sh

# Verify Docker is running
docker --version
docker compose version
```

---

## Step 4: Clone the Project

```bash
# Install git
apt install git -y

# Clone your repo into /srv
git clone https://github.com/YOUR_USERNAME/djangomombasa.git /srv/djangomombasa
cd /srv/djangomombasa
```

---

## Step 5: Configure Environment Variables

```bash
# Copy the example env file
cp .env.example .env

# Edit with your production values
nano .env
```

Set these values in `.env`:
```env
DJANGO_SETTINGS_MODULE=config.settings.prod
SECRET_KEY=<generate-a-real-key>
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,YOUR_SERVER_IP
CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
EMAIL_HOST_PASSWORD=<your-gmail-app-password>
DB_NAME=djangomombasa
DB_USER=postgres
DB_PASSWORD=<strong-random-password>
DB_HOST=db
DB_PORT=5432
```

Generate a secret key locally or on the server:
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(50))"
```

---

## Step 6: Build and Start the Containers

```bash
# Build and start in detached mode
docker compose up --build -d

# Verify both containers are running
docker compose ps

# You should see:
#   djangomombasa-db-1   ... healthy
#   djangomombasa-web-1  ... running

# Check logs if needed
docker compose logs -f web
```

At this point, your app is running on **port 8000**. You can test with:
```bash
curl http://localhost:8000
```

---

## Step 7: Create a Superuser

```bash
docker compose exec web python manage.py createsuperuser
# Enter your email and password (no username — we use email-based auth)
```

---

## Step 8: Set Up Nginx as a Reverse Proxy

Nginx sits in front of Gunicorn to handle SSL, static file caching, and proxying.

```bash
apt install nginx -y
```

Create the Nginx config:
```bash
nano /etc/nginx/sites-available/djangomombasa
```

Paste this config:
```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable and restart:
```bash
ln -s /etc/nginx/sites-available/djangomombasa /etc/nginx/sites-enabled/
rm /etc/nginx/sites-enabled/default
nginx -t
systemctl restart nginx
```

Your site is now accessible at `http://yourdomain.com` (or `http://YOUR_SERVER_IP`).

---

## Step 9: Point Your Domain to Linode

1. In your domain registrar (Namecheap, Cloudflare, etc.), set the **A record**:
   - `@` → `YOUR_SERVER_IP`
   - `www` → `YOUR_SERVER_IP`
2. Wait for DNS propagation (a few minutes to 48 hours)

---

## Step 10: Set Up SSL with Let's Encrypt

```bash
# Install Certbot
apt install certbot python3-certbot-nginx -y

# Get and install the certificate
certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Follow the prompts — choose to redirect HTTP to HTTPS

# Auto-renewal is set up automatically. Test it:
certbot renew --dry-run
```

---

## Step 11: Updating the App (Future Deployments)

When you push new code:

```bash
cd /srv/djangomombasa
git pull origin main
docker compose up --build -d
```

If no code changes (just restarting):
```bash
docker compose up -d
```

---

## Quick Reference

| Task | Command |
|------|---------|
| Start containers | `docker compose up -d` |
| Rebuild after code changes | `docker compose up --build -d` |
| View logs | `docker compose logs -f web` |
| Create superuser | `docker compose exec web python manage.py createsuperuser` |
| Django shell | `docker compose exec web python manage.py shell` |
| Stop containers | `docker compose down` |
| Stop + wipe database | `docker compose down -v` |
| Check SSL renewal | `certbot renew --dry-run` |
| Restart Nginx | `systemctl restart nginx` |
