#!/usr/bin/env bash
# ────────────────────────────────────────────────────────────────
# KekiCakes – Ubuntu VPS Deployment Script
# Run once as root (or sudo) on a fresh Ubuntu 22.04+ server
# ────────────────────────────────────────────────────────────────
set -e

DOMAIN="kekicakes.co.ke"
APP_USER="kekicakes"
APP_DIR="/home/${APP_USER}/KekiCakes"
REPO_URL="https://github.com/reaganodhiambo/KekiCakes.git"  # Update this

echo "── Installing system packages ──────────────────────────────"
apt-get update -qq
apt-get install -y -qq python3 python3-venv python3-pip nginx mysql-server certbot python3-certbot-nginx git

echo "── Creating application user ───────────────────────────────"
useradd -m -s /bin/bash $APP_USER 2>/dev/null || echo "User already exists"

echo "── Cloning repository ──────────────────────────────────────"
sudo -u $APP_USER git clone "${REPO_URL}" "${APP_DIR}" 2>/dev/null || (cd "${APP_DIR}" && sudo -u $APP_USER git pull)

echo "── Setting up Python virtualenv ────────────────────────────"
sudo -u $APP_USER python3 -m venv "${APP_DIR}/venv"
sudo -u $APP_USER "${APP_DIR}/venv/bin/pip" install -r "${APP_DIR}/requirements.txt" -q

echo "── Configuring .env ────────────────────────────────────────"
if [ ! -f "${APP_DIR}/.env" ]; then
    cp "${APP_DIR}/.env.example" "${APP_DIR}/.env"
    echo "⚠️  IMPORTANT: Edit ${APP_DIR}/.env with your production credentials."
fi

echo "── Running Django migrations ───────────────────────────────"
sudo -u $APP_USER bash -c "cd ${APP_DIR} && DJANGO_SETTINGS_MODULE=kekicakes.settings.production venv/bin/python manage.py migrate"
sudo -u $APP_USER bash -c "cd ${APP_DIR} && DJANGO_SETTINGS_MODULE=kekicakes.settings.production venv/bin/python manage.py collectstatic --noinput"

echo "── Installing Gunicorn systemd service ─────────────────────"
cp "${APP_DIR}/nginx/kekicakes.service" /etc/systemd/system/kekicakes.service
systemctl daemon-reload
systemctl enable kekicakes
systemctl start kekicakes

echo "── Configuring Nginx ───────────────────────────────────────"
cp "${APP_DIR}/nginx/kekicakes.conf" /etc/nginx/sites-available/kekicakes
ln -sf /etc/nginx/sites-available/kekicakes /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx

echo "── Getting SSL certificate ─────────────────────────────────"
certbot --nginx -d "${DOMAIN}" -d "www.${DOMAIN}" --non-interactive --agree-tos --email admin@${DOMAIN} || echo "SSL: Run certbot manually after DNS propagates."

echo ""
echo "✅ KekiCakes deployment complete!"
echo "   Visit: https://${DOMAIN}"
echo "   Admin: https://${DOMAIN}/admin/"
echo "   Remember to create a superuser: cd ${APP_DIR} && venv/bin/python manage.py createsuperuser"
