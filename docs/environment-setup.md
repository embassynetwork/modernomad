
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

add these to your ~/.bashrc (~/.bash_profile if one OS X) (create this file if it doesn't exist):
- `export WORKON_HOME="~/envs"` (or whatever you want to name the directory)
- `source /usr/local/bin/virtualenvwrapper.sh` (the path should match the path printed by the pip installer for virtualenvwrapper). 

don't forget to source the bashrc file now:
- `source ~/.bashrc`

## dependencies

PIL is a requirement, but in order for it to compile with JPG support, you must have a system-wide library called libjpeg62-dev. 

on OS X, download and install the tarball linked to on [this](http://apple.stackexchange.com/questions/59718/python-imaging-library-pil-decoder-jpeg-not-available-how-to-fix) stackexchange question. you will need x code installed with the extra "command line tools" component. 

to install on linux:
- `sudo apt-get install libjpeg62-dev`

you also need the python dev package:
- `sudo apt-get install python-dev`

on linux, you may need to symlink these libraries for PIL to find them during the install:
`sudo ln -s /usr/lib/x86_64-linux-gnu/libfreetype.so /usr/lib/`
`sudo ln -s /usr/lib/x86_64-linux-gnu/libz.so /usr/lib/`
`sudo ln -s /usr/lib/x86_64-linux-gnu/libjpeg.so /usr/lib/`


then either install PIL using `brew`, or from the dmg's available on the PIL website. for example, see the process outlined [here](http://stackoverflow.com/questions/9070074/how-to-install-pil-on-mac-os-x-10-7-2-lion)

## Hooray!

Now you can follow the directions in [how-to-run](how-to-run.md)
