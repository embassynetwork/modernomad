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

PIL is a requirement but in order for it to compile with JPG support, you must have a system-wide library called libjpeg62-dev. to install this:
- `sudo apt-get install libjpeg62-dev`

you may need to symlink these libraries for PIL to find them during the install:
`sudo ln -s /usr/lib/x86_64-linux-gnu/libfreetype.so /usr/lib/`
`sudo ln -s /usr/lib/x86_64-linux-gnu/libz.so /usr/lib/`
`sudo ln -s /usr/lib/x86_64-linux-gnu/libjpeg.so /usr/lib/`

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

## first time and on model updates
- make sure settings.py and, if applicable, local_settings.py exist and are correct. 
- `./manage.py syncdb` to create and sync the models of installed apps
- `./manage.py migrate` to set up the migrations

## mailman setup
- see http://mail.python.org/pipermail/mailman-users/2012-March/073089.html
- make sure you are in your virtualenv
- follow instructions [here](http://packages.python.org/mailman/src/mailman/docs/START.html)
- database used: url: sqlite:///$DATA_DIR/mailman.db (stores it in var/data within mailmain directory)
- mail server used: postfix (sudo apt-get install postfix)
- if installing on a local machine, you can set the FQDN to be the hostname
  (default) or anything else. 
- add appropriate config items to /etc/postfix/main.cf
- After modifying main.cf, be sure to run '/etc/init.d/postfix reload'.

- run the tests: bin/test -vv

build the docs (their docs are wrong about how to build the docs!):
- pip install sphinx
- python setup.py build_sphinx
this will put the docs in build/sphinx/html (obviously). the main index page is README.html


mailman frontend:
**** as released, does not work with django 1.4 (mention of a patch but version i pulled didn't work) *****
cd into a new directory to test the mailman setup (but remain in the virtualenv).
follow the 5 minute install for the posterious web UI:`http://wiki.list.org/display/DEV/A+5+minute+guide+to+get+the+Mailman+web+UI+running
(don't forget pip install django-social-auth).  

first test you can send a regular email locally

add a well-formed but not legit domain to /etc/hosts
create a new list and make sure you set an owner so when emails bounce you will receive the bounces

setting up local debugging - postfix aliases? 

testing a la http://www.mail-archive.com/mailman-developers%40python.org/msg12813.html:
- send a test mail using:
$ sendmail user@example.com
to: user@example.com
from: other@somedomain.com
subject: test
body of email
.
(empty line)
$




list integration
- new house -> internal and community lists (options)
- create new sub domain, auth for managing that subdomain

coliving.org
- storage, auth, styling


