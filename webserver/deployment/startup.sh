#!/usr/bin/env bash
set -x
cd /crypto-ticker/webserver/cryptoticker
git pull
# Install dependencies
pip install -r /crypto-ticker/webserver/requirements.txt

python manage.py makemigrations; python manage.py migrate
python manage.py createsuperuser --no-input --username $DJANGO_SUPERUSER_USERNAME --email $DJANGO_SUPERUSER_EMAIL

(cd /crypto-ticker/webserver/cryptoticker; gunicorn cryptoticker.wsgi:application --user www-data --bind 0.0.0.0:8010 --workers 3) &
nginx -g "daemon off;"