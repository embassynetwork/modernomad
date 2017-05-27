## How to Run the First Time

Assuming you have all the prerequisites and dependencies outlined in [environment-setup](environment-setup.md), we can proceed with making the virtual environemnt, populating it with required libraries, getting your local configuration working and starting up the app.

## virtualenv
create a new virtual environment for this project:
- `mkvirtualenv modernomad`

this will usually cause you to "enter" the virtualenv automatically, as will be
reflected by the prompt now prefixed with (modernomad). use the following
commands to work with virtualenvwrapper: `workon` to work on a specific virtual
env, `pip install blah` to install packages, `lssitepackages` to see packaged
installed in the virtual env. 

## clone the repository

- make sure you have git installed
- cd into the directory you want to clone the repository into
- git clone 

## dependencies:
within the virtualenv, install the requirements. this is done with the following command, which should iterate through the items in the text file and install them one by one:
- `pip install -r requirements.txt` 

note that the stripe library requires custom arguments which the
requirements.txt file parsing [apparently doesn't
support](https://github.com/pypa/pip/pull/515) (as of november 2012), so
install it manually on the command line using:
`pip install --index-url https://code.stripe.com --upgrade stripe`


## first time
create your own local_settings.py file from local_settings.example.py. inside the modernomad/modernomad directory, do the following:
- `cp local_settings.example.py local_settings.py`

the local_settings.py file contains configuration information for stripe
(payment handling), and email. if you want to run the software on a production
server, there are production-specific settings for email which you must setup
if you want email to work. by default, the software is in "development" mode,
and emails are sent using django's built-in console backend, meaning they
get printed to the console. 

- browse through settings.py. make note of the location of the media directory and media_url, and any other settings of interest.

go back into the top level repository directory and do the following:

- run `./manage.py syncdb` to create and sync the models of installed apps (and create an admin user)
- run `./manage.py migrate` to run the existing migrations (this will run migrations for all apps)

now you should be able to run the software:
- `./manage.py runserver [port]`

the first time you run the software, you will want to configure two things in
the admin interface. the software is designed to send various emails to users
who are part of the group 'house_admins' so, before it will send any emails,
you need to add at least one user to this group. login to the admin interface
at `localhost:port/admin` (with the admin user credentials you supplied when
you ran syncdb). click on 'users' and then any user (you probably only have one
user right now). on the user page under 'groups' highlight the option
'house_admin', and then hit 'save.'

in the admin interface you should also define some rooms, since the booking
form presents a choice to users based on the rooms and rates defined here. 

finally, set the value of the site variable so that full urls will have the
correct domain. Go back to the home page of the admin interface, then click
on 'sites' and then the first/only site that exists. edit the domain name
to match the host and port you are running the software on. 

Now you can go ahead and start creating content. 

## each time

- make sure rabbitmq is running, or start it: `rabbitmq-server`
- start celery beat (the scheduler for periodic tasks): `celery beat` (or some
  more sophisticated version of the same command, depending on your local or
  production setup), such as `./manage.py celeryd -v 2 -B -s celery -E -l INFO -n some_unique_name`
- start django `./manage.py runserver domain port`



## model updates
see the instructions in [updates](updates.md) for how to create and run database migrations if you add or remove fields from models. 




