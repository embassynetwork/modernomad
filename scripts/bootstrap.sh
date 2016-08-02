sudo service postgresql restart
dropdb modernomadb -U modernomad
createdb -U modernomad modernomadb
python manage.py syncdb --noinput
python manage.py migrate
python manage.py migrate core
python manage.py loaddata modernomad/fixtures/initial_modernomad_data.json

