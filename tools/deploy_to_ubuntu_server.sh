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
pip install virtualenv
pip install virtualenvwrapper

#
#
#  Everything after this section is executed as the user "vagrant"
#
#
exec sudo -u vagrant /bin/bash - << eof

if [ ! -f modernomad/local_settings.py ]; then
	SECURE_RANDOM=$(dd if=/dev/urandom count=1 bs=28 2>/dev/null | od -t x1 -A n)
	SECRET_KEY="${SECURE_RANDOM//[[:space:]]/}"
	sed "s/^SECRET_KEY.*$/SECRET_KEY = '$SECRET_KEY'/" modernomad/local_settings.example.py > modernomad/local_settings.py
fi

echo export WORKON_HOME="/home/vagrant/envs" >> /home/vagrant/.bashrc
export WORKON_HOME="/home/vagrant/envs"
echo source /usr/local/bin/virtualenvwrapper.sh >> /home/vagrant/.bashrc
source /usr/local/bin/virtualenvwrapper.sh
cd /vagrant

mkvirtualenv modernomad
yes | pip install -r requirements.txt
yes | pip install --index-url https://code.stripe.com --upgrade stripe

./manage.py syncdb --noinput
./manage.py migrate --noinput
echo "from django.contrib.auth.models import User; user = User.objects.all()[0]; user.set_password('password'); user.save()" | ./manage.py shell

screen -dms celery ./manage.py celeryd -v 2 -B -s celery -E -l INFO
screen -dmS django ./manage.py runserver 0.0.0.0:31337

eof
