## if you update a model, need to create a migration and run south. 
$ ./manage.py schemamigration core --auto

if you have a fixtures file, you might need to add/change a field name to
correspond to any model changes you made. 

then, as instructed, run
$ ./manage.py migrate <appname>


