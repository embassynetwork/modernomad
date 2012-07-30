## if you update a model, create a migration and run south. 

create the migration
$ ./manage.py schemamigration core --auto

if you have a fixtures file, add/change field(s) to correspond to any model
changes you made. 

then, as instructed, run
$ ./manage.py migrate <appname>


