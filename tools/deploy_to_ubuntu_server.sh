#!/bin/bash
sudo apt-get update -y
sudo apt-get install git python-dev libjpeg8 libjpeg8-dev rabbitmq-server wget python-pip -y

sudo mkdir -p /var/django_apps/
sudo chown vagrant:vagrant /var/django_apps/
cd /var/django_apps/
git clone "$1"

cd modernomad
sudo pip install -r requirements.txt
sudo pip install --index-url https://code.stripe.com --upgrade stripe

if [ ! -f modernomad/local_settings.py ]; then
    SECURE_RANDOM=$(dd if=/dev/urandom count=1 bs=28 2>/dev/null | od -t x1 -A n)
    SECRET_KEY="${SECURE_RANDOM//[[:space:]]/}"
    sed "s/^SECRET_KEY.*$/SECRET_KEY = '$SECRET_KEY'/" modernomad/local_settings.example.py > modernomad/local_settings.py
fi

sudo adduser --system --no-create-home --disabled-login --disabled-password --group celery
sudo mkdir -p /var/run/celery/
sudo mkdir -p /var/log/celery/
sudo cp tools/init.d/celeryd /etc/init.d/celeryd
sudo cp tools/default/celeryd /etc/init.d/celeryd
sudo chmod +x /etc/init.d/celeryd
sudo update-rc.d celeryd defaults
sudo /etc/init.d/celeryd start

./manage.py syncdb --noinput 
./manage.py migrate --noinput 
./manage.py runserver
