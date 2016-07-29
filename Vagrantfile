# -*- mode: ruby -*-
# vi: set ft=ruby :

# Vagrantfile API/syntax version. Don't touch unless you know what you're doing!
VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  # All Vagrant configuration is done here. The most common configuration
  # options are documented and commented below. For a complete reference,
  # please see the online documentation at vagrantup.com.

  # From https://gist.github.com/millisami/3798773
  def local_cache(box_name)
    cache_dir = File.join(File.expand_path('~/.vagrant.d'), 'cache', 'apt', box_name)
    partial_dir = File.join(cache_dir, 'partial')
    FileUtils.mkdir_p(partial_dir) unless File.exists? partial_dir
    cache_dir
  end


  # Every Vagrant virtual environment requires a box to build off of.
  config.vm.box = "precise32"
  
  # custom baked ubuntu vm that hass updates applied and packages applied
  config.vm.box_url = "https://cloud-images.ubuntu.com/vagrant/precise/current/precise-server-cloudimg-i386-vagrant-disk1.box"

  cache_dir = local_cache(config.vm.box)
  
  config.vm.synced_folder cache_dir, "/var/cache/apt/archives/"

  # accessing "localhost:31337" will access port 3133 on the guest machine.
  config.vm.network :forwarded_port, guest: 8989, host: 8989

  # If true, then any SSH connections made will enable agent forwarding.
  # Default value: false
  config.ssh.forward_agent = true
  
$rootScript = <<SCRIPT
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
  service postgresql restart
  
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
SCRIPT

$userScript = <<SCRIPT

  git config --global url."https://".insteadOf git://
  
  echo export WORKON_HOME="/home/vagrant/envs" >> /home/vagrant/.bashrc
  export WORKON_HOME="/home/vagrant/envs"
  echo source /usr/local/bin/virtualenvwrapper.sh >> /home/vagrant/.bashrc
  source /usr/local/bin/virtualenvwrapper.sh
  cd /vagrant

  mkvirtualenv modernomad
  yes | pip install -r requirements.txt
  yes | pip install --index-url https://code.stripe.com --upgrade stripe

  if [ ! -f modernomad/local_settings.py ]; then
  	SECURE_RANDOM=$(dd if=/dev/urandom count=1 bs=28 2>/dev/null | od -t x1 -A n)
  	SECRET_KEY="${SECURE_RANDOM//[[:space:]]/}"
  	sed "s/^SECRET_KEY.*$/SECRET_KEY = '$SECRET_KEY'/" modernomad/local_settings.example.py > modernomad/local_settings.py
    sed -i.bak "s/\\/Users\\/jessykate\\/code\\/embassynetwork\\/logs\\/django.log/\\/vagrant\\/django.log/" modernomad/local_settings.py
    sed -i.bak "s/'postgres'/'modernomad'/" modernomad/local_settings.py
  fi
  
  echo workon modernomad >> /home/vagrant/.bashrc
  workon modernomad
  ./manage.py syncdb --noinput
  ./manage.py migrate core
  ./manage.py migrate
  screen -dms celery ./manage.py celeryd -v 2 -B -s celery -E -l INFO
  screen -dmS django ./manage.py runserver 0.0.0.0:8989
SCRIPT


  config.vm.provision "shell",
    privileged: true,
    inline: $rootScript

  config.vm.provision "shell",
    privileged: false,
    inline: $userScript
    
end
