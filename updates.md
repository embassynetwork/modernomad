## Model Updates

if you update a model, create a migration and run south (this assumes
`./manage.py schemamigration --initial` was run when you set up your project
initially).

create the migration
`$ ./manage.py schemamigration core --auto`

to rename a field...?

if you have a fixtures file, add/change field(s) to correspond to any model
changes you made. 

then, as instructed, run
`$ ./manage.py migrate <appname>`


