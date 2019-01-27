# Docker Development Environment

First, install Docker CE. On macOS, the best way to this is to use [Docker for Mac](https://docs.docker.com/docker-for-mac/install/). For Linux and Windows, [take a look at Docker's documentation](https://docs.docker.com/engine/installation/). 

Make sure you have `docker-compose` installed. See eg: Digital Ocean's most likely up to date [instructions](https://www.digitalocean.com/community/tutorials/how-to-install-docker-compose-on-ubuntu-18-04) for installing from source or packages. 

Next, run:

    $ [sudo] docker-compose up --build

This will boot up everything that Modernomad needs to run, and stay running in the terminal.

In another console, run these commands to set up the database and set up a user:

    $ [sudo] docker-compose run web ./manage.py migrate

Your docker image is now running with your local development code. Browse to `http://localhost:8000/` to access your running image. You can run any of the other `manage.py` commands in the same way. E.g., to run the test suite:

    $ docker-compose run web ./manage.py test

The first time you get this going, you will want to generate some test data:

    $ docker-compose run web ./manage.py generate_test_data

This will wipe out your superuser, so after generating test data, create a new superuser that you know the credentials to:

    $ [sudo] docker-compose run web ./manage.py createsuperuser

You only need to run these commands once. Wen you want to work on the development environment in the future, just run `docker-compose up --build`. (Note: `--build` is optional, but means that the Python and Node dependencies will always remain up-to-date.)

## Configuration

You can configure the development environment using environment variables in a file called `.env`. It looks something like this:

```
STRIPE_SECRET_KEY=...
STRIPE_PUBLISHABLE_KEY=...
MAILGUN_API_KEY=...
```

To learn about what can be configured, see the [configuration documentation](configuration.md).
