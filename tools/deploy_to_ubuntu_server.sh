#!/bin/bash -ex

apt-get install python-software-properties -y
apt-get update -y
#apt-get upgrade -y 
apt-get install git vim python-dev libjpeg8 libjpeg8-dev rabbitmq-server curl vim screen -y

if [ -f /etc/init.d/nginx ]; then
  apt-get remove nginx
  killall nginx
fi

cd /tmp
curl -O https://raw.github.com/pypa/pip/master/contrib/get-pip.py
sudo python get-pip.py
pip --version
cd /vagrant/

yes | pip install -r requirements.txt
yes | pip install --index-url https://code.stripe.com --upgrade stripe

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

su vagrant -c "./manage.py syncdb --noinput"
su vagrant -c "./manage.py migrate --noinput"
su vagrant -c "screen -dmS django ./manage.py runserver 0.0.0.0:31337"
