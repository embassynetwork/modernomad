## How to Run the First Time

Assuming you have all the prerequisites and dependencies outlined in [environment-setup](environment-setup.md), we can proceed with making the virtual environemnt, populating it with required libraries, getting your local configuration working and starting up the app.

## virtualenv
create a new virtual environment for this project:
- `mkvirtualenv modernomad`

this will usually cause you to "enter" the virtualenv automatically, as will be reflected by the prompt now prefixed with (modernomad). use the following commands to work with virtualenvwrapper: `workon` to work on a specific virtual env, `pip install blah` to install packages, `lssitepackages` to see packaged installed in the virtual env.

## clone the repository

- make sure you have git installed
- cd into the directory you want to clone the repository into
- git clone

## dependencies:
within the virtualenv, install the requirements. this is done with the following command, which should iterate through the items in the text file and install them one by one:
- `pip install -r requirements.txt`
- `pip install -r requirements.test.txt`

install all node packages
- `cd modernomad/client`
- `npm install`
- `npm install -g less`

initialize webpack here???
- `node_modules/.bin/webpack --config webpack.prod.config.js`

To get webpack to work locally you should be able to do
- `node_modules/.bin/webpack`

Then to run the webpack dev server. Run the following command.
It'll now serve the javascript from localhost:3000 which is what django is
configured for.
- `node_modules/.bin/webpack-dev-server --port 3000 -w`

@todo This is a fix to make webpack work. Configuration needs tidying up by whoever knows how webpack works.
- `cp webpack-stats-prod.json webpack-stats.json`
- Edit server.js and replace `localhost` if necessary with the public IP address or hostname you are serving from. E.g. `public: 'myhousingnetwork.com'`
- Edit webpack.config.js and in the output.publicPath setting, replace `localhost` if necessary with your public IP or hostname. E.g. ` publicPath: 'http://myhousingnetwork:3000/build/'`


## Configuration settings
If there is any local settings that you'd like to overwrite while developing you can always overwrite those in `settings/local.py`. Otherwise the project is set up to the biggest possible extent to use environment variables.

### settings you must configure, and dependant services:

* `DATABASES`  : Setup Postgres:
  * `sudo su - postgres`
  * `psql`
  * `CREATE USER modernomad WITH PASSWORD '$POSTGRESPASSWORD';`
  * `CREATE DATABASE modernomad;`
  * `GRANT ALL PRIVILEGES ON DATABASE modernomad TO modernomad ;`
  * (Enter USER, NAME, and PASSWORD in config)
* `LOGGING` : If some debug modes are enabled you need to set a valid log file path in the setting LOGGING.handlers.file.filename

### optional stuff required for payment, email, etc.

* STRIPE
* EMAIL: if you want to run the software on a production server, there are production-specific settings for email which you must setup if you want email to work. by default, the software is in "development" mode, and emails are sent using django's built-in console backend, meaning they get printed to the console.

- browse through settings.py. make note of the location of the media directory and media_url, and any other settings of interest.

## Initialisation

go back into the top level repository directory and do the following:

- `./manage.py migrate` will initialise the database on first run. In the next step you want to get some initial data into the database.
- `./manage.py generate_test_data`. This will populate the database with some randomized initial data.

## Run!

Now you should be able to run the software. Both django and node are required to be running!

Run django:

- `cd $WORKON_HOME/modernomadenv/modernomad`
- `./manage.py runserver [port]`

Run node:

- `cd $WORKON_HOME/modernomadenv/modernomad/client`
- `node server`


The first time you run the software, you will want to configure two things in the admin interface. the software is designed to send various emails to users who are part of the group 'house_admins' so, before it will send any emails, you need to add at least one user to this group. login to the admin interface at `localhost:port/admin` (with the admin user credentials you supplied when you ran migrate). click on 'users' and then any user (you probably only have one user right now). on the user page under 'groups' highlight the option 'house_admin', and then hit 'save.'

in the admin interface you should also define some rooms, since the booking form presents a choice to users based on the rooms and rates defined here.

finally, set the value of the site variable so that full urls will have the correct domain. Go back to the home page of the admin interface, then click on 'sites' and then the first/only site that exists. edit the domain name to match the host and port you are running the software on.

Now you can go ahead and start creating content.

## Running in Production

(Update docs here for Debian service creation)

Ensure required services running:

- postgres

Start django and node services

(Docs here for adding proper production configuration for django and node)

## model updates
see the instructions in [updates](updates.md) for how to create and run database migrations if you add or remove fields from models.




