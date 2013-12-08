# -*- mode: ruby -*-
# vi: set ft=ruby :

# Vagrantfile API/syntax version. Don't touch unless you know what you're doing!
VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  # All Vagrant configuration is done here. The most common configuration
  # options are documented and commented below. For a complete reference,
  # please see the online documentation at vagrantup.com.

  # Every Vagrant virtual environment requires a box to build off of.
  config.vm.box = "modernomad"
  
  # custom baked ubuntu vm that hass updates applied and packages applied 
  config.vm.box_url = "https://dl.dropboxusercontent.com/s/obldjxggn8m3gzn/modernomad.box"
  
  # If you get download errors then the above image may have been deleted.
  # You can safely revert back to the cloud image
  # config.vm.box_url = "http://cloud-images.ubuntu.com/vagrant/precise/current/precise-server-cloudimg-i386-vagrant-disk1.box"

  # Another backup of the custom baked vm is available here
  # (this does not work in vagrant currently because it doesn't seem to handle 302 redirects)
  # https://drive.google.com/file/d/0B3OI3GryqC2ua0pVSlEtMmNtX1k/edit?usp=sharing

  # Create a forwarded port mapping which allows access to a specific port
  # within the machine from a port on the host machine. In the example below,
  # accessing "localhost:8080" will access port 80 on the guest machine.
  config.vm.network :forwarded_port, guest: 80, host: 31337

  # Create a private network, which allows host-only access to the machine
  # using a specific IP.
  config.vm.network :private_network, ip: "192.168.33.10"

  # Create a public network, which generally matched to bridged network.
  # Bridged networks make the machine appear as another physical device on
  # your network.
  # config.vm.network :public_network


  # If true, then any SSH connections made will enable agent forwarding.
  # Default value: false
  config.ssh.forward_agent = true

  # Share an additional folder to the guest VM. The first argument is
  # the path on the host to the actual folder. The second argument is
  # the path on the guest to mount the folder. And the optional third
  # argument is a set of non-required options.
  # config.vm.synced_folder "./", "/var/django_apps/modernomad/"
  
  config.vm.provision "shell",
    path: "tools/deploy_to_ubuntu_server.sh",
    args: `git config --get remote.origin.url`

end
