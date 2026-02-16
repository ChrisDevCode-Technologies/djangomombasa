# VPS Deployment Guide (Ubuntu)

Deploy Django Mombasa on a bare Ubuntu VPS with Nginx, Gunicorn, and PostgreSQL.

## Prerequisites

- Ubuntu 22.04+ VPS with root/sudo access
- Domain name pointed to the VPS IP (A record)
- SSH access configured

## Quick Start

```bash
# 1. SSH into your server
ssh root@your-server-ip

# 2. Clone the repository
git clone https://github.com/your-username/djangomombasa.git /opt/djangomombasa

# 3. Edit the configuration variables at the top of the setup script
nano /opt/djangomombasa/deploy/setup.sh
# Set REPO_URL and DOMAIN

# 4. Run the setup script
sudo bash /opt/djangomombasa/deploy/setup.sh

# 5. Edit the environment file with your email password
sudo nano /etc/djangomombasa/.env

# 6. Set up SSL with Let's Encrypt
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# 7. Create an admin user
sudo -u djangomombasa bash -c '
    set -a && source /etc/djangomombasa/.env && set +a
    /opt/djangomombasa/.venv/bin/python /opt/djangomombasa/manage.py createsuperuser
'
```

## Maintenance Commands

```bash
# Check service status
sudo systemctl status djangomombasa
sudo systemctl status nginx

# View application logs
sudo tail -f /var/log/djangomombasa/error.log
sudo tail -f /var/log/djangomombasa/access.log

# Restart after code or config changes
sudo systemctl restart djangomombasa

# Pull latest code and redeploy
cd /opt/djangomombasa
sudo -u djangomombasa git pull
sudo -u djangomombasa bash -c '
    set -a && source /etc/djangomombasa/.env && set +a
    /opt/djangomombasa/.venv/bin/pip install -r requirements.txt
    /opt/djangomombasa/.venv/bin/python manage.py collectstatic --noinput
    /opt/djangomombasa/.venv/bin/python manage.py migrate --noinput
'
sudo systemctl restart djangomombasa

# Django management commands
sudo -u djangomombasa bash -c '
    set -a && source /etc/djangomombasa/.env && set +a
    /opt/djangomombasa/.venv/bin/python /opt/djangomombasa/manage.py shell
'
```

## File Locations

| What | Where |
|------|-------|
| Application code | `/opt/djangomombasa/` |
| Virtual environment | `/opt/djangomombasa/.venv/` |
| Environment variables | `/etc/djangomombasa/.env` |
| Systemd service | `/etc/systemd/system/djangomombasa.service` |
| Nginx config | `/etc/nginx/sites-available/djangomombasa` |
| Gunicorn socket | `/run/gunicorn/djangomombasa.sock` |
| Application logs | `/var/log/djangomombasa/` |
| Media uploads | `/opt/djangomombasa/media/` |
| Static files | `/opt/djangomombasa/staticfiles/` |

## SSL Certificate Renewal

Certbot sets up automatic renewal. To test:

```bash
sudo certbot renew --dry-run
```

## Troubleshooting

```bash
# Gunicorn won't start — check logs
sudo journalctl -u djangomombasa -n 50

# Nginx errors — test config
sudo nginx -t

# Permission issues — verify ownership
ls -la /opt/djangomombasa/
ls -la /run/gunicorn/

# Database connection issues — check PostgreSQL
sudo systemctl status postgresql
sudo -u postgres psql -c "\l"
```
