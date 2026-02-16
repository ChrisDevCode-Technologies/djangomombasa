#!/usr/bin/env bash
# Django Mombasa — Ubuntu VPS Setup Script
# Run as root: sudo bash deploy/setup.sh
#
# Assumes the repo is already cloned, virtualenv created, and pip install done.
#
# This script:
#   1. Installs remaining system packages (Nginx, Certbot)
#   2. Configures firewall
#   3. Creates a dedicated system user
#   4. Writes the environment file
#   5. Runs collectstatic and migrate
#   6. Installs the systemd service and Nginx config
#   7. Starts everything up

set -euo pipefail

# ──────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────
DOMAIN="djangomombasa.org"
APP_DIR="/var/www/djangomombasa"
APP_USER="djangomombasa"
DB_NAME="djangomombasa"
DB_USER="linodeuser"
DB_PASSWORD="linodepassword"

# ──────────────────────────────────────────────
# Sanity checks
# ──────────────────────────────────────────────
if [[ $EUID -ne 0 ]]; then
    echo "Error: This script must be run as root (use sudo)."
    exit 1
fi

if [[ ! -d "${APP_DIR}/bin" ]]; then
    echo "Error: Virtualenv not found at ${APP_DIR}/bin"
    echo "Create it first: python3 -m venv ${APP_DIR}/bin && ${APP_DIR}/bin/pip install -r ${APP_DIR}/requirements.txt"
    exit 1
fi

# ──────────────────────────────────────────────
# 1. Install system packages (nginx, certbot)
# ──────────────────────────────────────────────
echo "==> Installing system packages..."
apt update
apt install -y nginx certbot python3-certbot-nginx ufw

# ──────────────────────────────────────────────
# 2. Configure firewall
# ──────────────────────────────────────────────
echo "==> Configuring firewall..."
ufw allow OpenSSH
ufw allow 'Nginx Full'
ufw --force enable

# ──────────────────────────────────────────────
# 3. Create system user
# ──────────────────────────────────────────────
echo "==> Creating system user '${APP_USER}'..."
if ! id "${APP_USER}" &>/dev/null; then
    useradd --system --shell /usr/sbin/nologin --home "${APP_DIR}" "${APP_USER}"
fi
usermod -aG www-data "${APP_USER}"

# ──────────────────────────────────────────────
# 4. Create environment file
# ──────────────────────────────────────────────
echo "==> Writing environment file..."
mkdir -p /etc/djangomombasa

SECRET_KEY=$("${APP_DIR}/bin/python" -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")

cat > /etc/djangomombasa/.env <<ENV
DJANGO_SETTINGS_MODULE=config.settings.prod
SECRET_KEY=${SECRET_KEY}
ALLOWED_HOSTS=${DOMAIN},www.${DOMAIN}
CSRF_TRUSTED_ORIGINS=https://${DOMAIN},https://www.${DOMAIN}
ENABLE_HTTPS=true

# Database
DB_NAME=${DB_NAME}
DB_USER=${DB_USER}
DB_PASSWORD=${DB_PASSWORD}
DB_HOST=localhost
DB_PORT=5432

# Email (Gmail SMTP) — add your app password
EMAIL_HOST_PASSWORD=
ENV

chmod 640 /etc/djangomombasa/.env
chown root:${APP_USER} /etc/djangomombasa/.env
echo "    Environment file written to /etc/djangomombasa/.env"

# ──────────────────────────────────────────────
# 5. Set up directories and permissions
# ──────────────────────────────────────────────
echo "==> Setting permissions..."
mkdir -p "${APP_DIR}/media"
mkdir -p /var/log/djangomombasa

chown -R "${APP_USER}:www-data" "${APP_DIR}"
chown -R "${APP_USER}:www-data" /var/log/djangomombasa
chmod -R 755 "${APP_DIR}"

# ──────────────────────────────────────────────
# 6. Run Django setup
# ──────────────────────────────────────────────
echo "==> Running collectstatic and migrate..."
cd "${APP_DIR}"

sudo -u "${APP_USER}" bash -c "
    set -a
    source /etc/djangomombasa/.env
    set +a
    ${APP_DIR}/bin/python manage.py collectstatic --noinput
    ${APP_DIR}/bin/python manage.py migrate --noinput
"

# ──────────────────────────────────────────────
# 7. Install systemd service
# ──────────────────────────────────────────────
echo "==> Installing systemd service..."
cp "${APP_DIR}/deploy/gunicorn.service" /etc/systemd/system/djangomombasa.service
systemctl daemon-reload
systemctl enable djangomombasa
systemctl start djangomombasa

# ──────────────────────────────────────────────
# 8. Install Nginx config
# ──────────────────────────────────────────────
echo "==> Configuring Nginx..."
cp "${APP_DIR}/deploy/nginx.conf" /etc/nginx/sites-available/djangomombasa

# Update server_name with the configured domain
sed -i "s/your-domain.com/${DOMAIN}/g" /etc/nginx/sites-available/djangomombasa

ln -sf /etc/nginx/sites-available/djangomombasa /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

nginx -t && systemctl reload nginx

# ──────────────────────────────────────────────
# Done
# ──────────────────────────────────────────────
echo ""
echo "============================================"
echo "  Deployment complete!"
echo "============================================"
echo ""
echo "  App directory:  ${APP_DIR}"
echo "  Config file:    /etc/djangomombasa/.env"
echo "  Gunicorn:       systemctl status djangomombasa"
echo "  Nginx:          systemctl status nginx"
echo "  Logs:           /var/log/djangomombasa/"
echo ""
echo "  Next steps:"
echo "    1. Edit /etc/djangomombasa/.env (add EMAIL_HOST_PASSWORD, verify domain)"
echo "    2. Set up SSL:  sudo certbot --nginx -d ${DOMAIN} -d www.${DOMAIN}"
echo "    3. Create admin: sudo -u ${APP_USER} bash -c 'source /etc/djangomombasa/.env && ${APP_DIR}/bin/python ${APP_DIR}/manage.py createsuperuser'"
echo ""
