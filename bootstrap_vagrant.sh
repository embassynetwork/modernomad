#
# Pretty CLI
#
echo "export CLICOLOR=1" >> /home/vagrant/.bashrc
echo "export LSCOLORS=GxFxCxDxBxegedabagaced" >> /home/vagrant/.bashrc
echo 'export PS1="[\u@\[\e[32;1m\]\H \[\e[0m\]\w]\$ "' >> /home/vagrant/.bashrc

# Always start us in /vagrant
echo "cd /vagrant/" >> /home/vagrant/.bashrc

# Add some helpful aliases
echo "alias runserver='cd /vagrant && python manage.py runserver [::]:8989'" >> /home/vagrant/.bashrc

source /home/vagrant/.bashrc

set -x
apt-get update -y 
# apt-get upgrade -y 
apt-get install python-software-properties libxml2-dev libxslt1-dev -y
apt-get install git vim python-dev libjpeg8 libjpeg8-dev rabbitmq-server curl vim screen -y
apt-get install python-psycopg2 libpq-dev postgresql -y

apt-get purge python-pip -y

sudo -u postgres createuser --createdb --no-superuser --no-createrole modernomad
sudo -u postgres createdb --owner=modernomad modernomadb
sudo -u postgres psql -d postgres -c "ALTER USER modernomad WITH PASSWORD 'somepassword'" 
sed -i.bak 's/peer$/trust/' /etc/postgresql/9.1/main/pg_hba.conf 

if [ -f /etc/init.d/nginx ]; then
    apt-get remove nginx
    killall nginx
fi

cd /tmp
curl -LO https://bootstrap.pypa.io/get-pip.py
sudo python get-pip.py
sudo pip --version
sudo pip install virtualenv
sudo pip install virtualenvwrapper 

git config --global url."https://".insteadOf git://

# echo export WORKON_HOME="/home/vagrant/envs" >> /home/vagrant/.bashrc
# export WORKON_HOME="/home/vagrant/envs"
# echo source /usr/local/bin/virtualenvwrapper.sh >> /home/vagrant/.bashrc
# source /usr/local/bin/virtualenvwrapper.sh
cd /vagrant

# mkvirtualenv modernomad
yes | sudo pip install -r requirements.txt
yes | sudo pip install --index-url https://code.stripe.com --upgrade stripe

if [ ! -f modernomad/local_settings.py ]; then
    SECURE_RANDOM=$(dd if=/dev/urandom count=1 bs=28 2>/dev/null | od -t x1 -A n)
    SECRET_KEY="${SECURE_RANDOM//[[:space:]]/}"
    sed "s/^SECRET_KEY.*$/SECRET_KEY = '$SECRET_KEY'/" modernomad/local_settings.example.py > modernomad/local_settings.py
    sed -i.bak "s/\\/Users\\/jessykate\\/code\\/embassynetwork\\/logs\\/django.log/\\/vagrant\\/django.log/" modernomad/local_settings.py
    sed -i.bak "s/'postgres'/'modernomad'/" modernomad/local_settings.py
fi

# echo workon modernomad >> /home/vagrant/.bashrc
# workon modernomad

./scripts/bootstrap.sh

screen -dms celery ./manage.py celeryd -v 2 -B -s celery -E -l INFO
