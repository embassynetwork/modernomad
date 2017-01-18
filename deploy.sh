#!/bin/bash
# For this to work you must have your public key added to the embassynetwork
# user's authorized_keys on alfred
ssh embassynetwork@embassynetwork.com <<-'ENDSSH'
  echo "PULLING MASTER"
  cd ~/webapp/modernomad
  git pull origin master

  echo "UPDATING WEBPACK BUNDLE"
  cd client
  npm install
  node_modules/.bin/webpack --config webpack.prod.config.js
  cd ..

  echo "INSTALLING PYTHON PACKAGES"
  source ../bin/activate
  pip install -r requirements.txt
  ./manage.py migrate

  echo "COLLECTING STATIC ASSETS"
  ./manage.py collectstatic  -i node_modules --noinput
ENDSSH

# For this to work, you must have sudo access and your username on your
# localmachine must match your username on embassynetwork.com (alfred)
echo "RESTARTING SERVICES"
echo "(You will be asked for your password twice, that's normal)"
ssh -t embassynetwork.com "sudo supervisorctl restart gunicorn"
ssh -t embassynetwork.com "sudo supervisorctl restart celery"
