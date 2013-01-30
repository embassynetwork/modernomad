## Model Updates

if you update a model, create a migration and run south (this assumes
`./manage.py schemamigration --initial` was run when you set up your project
initially).

create the migration
`$ ./manage.py schemamigration core --auto`

if you have a fixtures file, add/change field(s) to correspond to any model
changes you made, if necessary. 

then, as instructed, run
`$ ./manage.py migrate <appname>`

if you want to sanity check things first, you can start by running the command
with the db-dry-run flag. don't forget to run it for reals after:
`$ ./manage.py migrate <appname> --db-dry-run`

if you need to reset all migrations, do:
`$ rm -r [appname]/migrations/`
`$ ./manage.py reset south`
`$ ./manage.py convert_to_south appname`

warning: resetting south will delete all migrations for ALL APPS!

when you pull changes that include new migrations on a remote copy of the repo, run the migrate command again:
`$ ./manage.py migrate <appname>`



