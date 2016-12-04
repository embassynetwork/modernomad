#!/bin/sh

until python manage.py syncdb --noinput; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done
python manage.py makemigrations --noinput && \
python manage.py migrate --noinput && \
celery beat -b mq -A modernomad --detach && \
python manage.py runserver 0.0.0.0:80 -v 3
