# Heroku/Dokku/similar PaaS deployment configuration
# Release phase runs collectstatic and migrations before deployment
release: python manage.py collectstatic --noinput && python manage.py migrate --noinput
web: gunicorn config.wsgi --log-file -
