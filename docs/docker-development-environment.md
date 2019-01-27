# Docker Development Environment

First, install Docker CE. On macOS, the best way to this is to use [Docker for Mac](https://docs.docker.com/docker-for-mac/install/). For Linux and Windows, [take a look at Docker's documentation](https://docs.docker.com/engine/installation/). 

Make sure you have `docker-compose` installed. See eg: Digital Ocean's most likely up to date [instructions](https://www.digitalocean.com/community/tutorials/how-to-install-docker-compose-on-ubuntu-18-04) for installing from source or packages. 

Next, run:

    $ [sudo] docker-compose up --build

This will boot up everything that Modernomad needs to run, and stay running in the terminal.

In another console, run these commands to set up the database and set up a user:

    $ [sudo] docker-compose run web ./manage.py migrate
    $ [sudo] docker-compose run web ./manage.py createsuperuser

You only need to run these commands once. To spin up the development environment when you need to work on it again, just run `docker-compose up --build`. (Note: `--build` is optional, but means that the Python and Node dependencies will always remain up-to-date.)

To run the test suite:

    $ docker-compose run web ./manage.py test

## Configuration

You can configure the development environment using environment variables in a file called `.env`. It looks something like this:

```
STRIPE_SECRET_KEY=...
STRIPE_PUBLISHABLE_KEY=...
MAILGUN_API_KEY=...
```

To learn about what can be configured, see the [configuration documentation](configuration.md).
