manage networks of houses with members and resources. 
 
## prerequisites: pip and virtualenv. 

each virtualenv contains its own install of pip, but you need pip to be installed globally in order to install virtualenv and virtualenvwrapper (or, at least, this is the easiest way to get those dependencies). 

optionally remove old/crusty versions:
- `sudo apt-get purge python-pip`
then get current version (url from http://www.pip-installer.org/en/latest/installing.html)
- `cd /tmp`
- `wget https://raw.github.com/pypa/pip/master/contrib/get-pip.py`
- `sudo python get-pip.py`
optionally verify your install
- `pip --version`

install virtualenv and (if you want to stay sane) virtualenvwrapper:
- `sudo pip install virtualenv` (harmless if virtualenv is already installed)
- `sudo pip install virtualenvwrapper`
add to your ~/.bashrc:
- `export WORKON_HOME="~/envs"` (or whatever you want to name the directory)
- `source /usr/local/bin/virtualenvwrapper.sh` (the path should match the path printed by the pip installer for virtualenvwrapper). 
don't forget to source the bashrc file now:
- `source ~/.bashrc`

## modernomad virtualenv
- `mkvirtualenv modernomad`
this will automatically cause you to "enter" the virtualenv, as will be
reflected by the prompt now prefixed with (modernomad). use the following
commands to work with virtualenvwrapper: `workon` to work on a specific virtual
env, `pip install blah` to install packages, `lssitepackages` to see packaged
installed in the virtual env. 

## dependencies:
within the virtualenv
- `pip install -r requirements.txt.` 

## to run:

## to migrate:

