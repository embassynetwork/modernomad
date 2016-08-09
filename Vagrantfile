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

      config.vm.provider "virtualbox" do |v|
        v.memory = 1024
      end
      
      # custom baked ubuntu vm that hass updates applied and packages applied
      config.vm.box_url = "https://cloud-images.ubuntu.com/vagrant/precise/current/precise-server-cloudimg-i386-vagrant-disk1.box"

      cache_dir = local_cache(config.vm.box)
      
      config.vm.synced_folder cache_dir, "/var/cache/apt/archives/"

      # accessing "localhost:31337" will access port 3133 on the guest machine.
      config.vm.network :forwarded_port, guest: 8989, host: 8989

      # If true, then any SSH connections made will enable agent forwarding.
      # Default value: false
      config.ssh.forward_agent = true

config.vm.provision :shell, :path => "bootstrap_vagrant.sh"
   
end
