#!/bin/bash -x

apt-get install python-software-properties -y
apt-get update -y
apt-get upgrade -y 
apt-get install git vim python-dev libjpeg8 libjpeg8-dev rabbitmq-server wget python-pip nginx -y
apt-add-repository ppa:gunicorn/ppa -y
apt-get install gunicorn -y

cd /vagrant/

pip install pip --upgrade
pip install -r requirements.txt
pip install --index-url https://code.stripe.com --upgrade stripe

if [ ! -f modernomad/local_settings.py ]; then
    SECURE_RANDOM=$(dd if=/dev/urandom count=1 bs=28 2>/dev/null | od -t x1 -A n)
    SECRET_KEY="${SECURE_RANDOM//[[:space:]]/}"
    sed "s/^SECRET_KEY.*$/SECRET_KEY = '$SECRET_KEY'/" modernomad/local_settings.example.py > modernomad/local_settings.py
fi

adduser --system --no-create-home --disabled-login --disabled-password --group celery
mkdir -p /var/run/celery/
mkdir -p /var/log/celery/
rsync -avr tools/etc/ /etc/
chmod +x /etc/init.d/celeryd
update-rc.d celeryd defaults
/etc/init.d/celeryd start

./manage.py syncdb --noinput 
./manage.py migrate --noinput 
./manage.py runserver 80
