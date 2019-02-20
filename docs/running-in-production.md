# Running in production

Modernomad is designed to be deployed on Heroku inside Docker containers.

In the root of the repository is a manifest that lets you deploy it on Heroku. In short, you can these commands and it should get most things up and running:

    $ heroku create --manifest
    $ heroku run ./manage.py migrate

## Static files

The Heroku app serves up static files directly, using [Whitenoise](http://whitenoise.evans.io/en/stable/).

Cloudflare sits in front of the Heroku app and caches the static files so each request doesn't hit the Heroku app.

### Caching

The main caveat you have to be aware of is that all static files have very long cache timeouts so they can be cached for a long time in Cloudflare and users' browsers. This means that if you change a static file, it has to be given a different filename for it to be updated.

This is done automatically by django_compressor for most CSS and JS in the app. For images, you will have to either rename the file or assume that some users will be seeing the old version.

In Django, there are various ways of adding the hash of the content of a static file to the filename, but this hasn't been implemented yet.

### Testing production static files locally

The Docker Compose file `docker-compose.production.yml` approximates a production setup so you can check the compilation of static files. Run it with:

    $ docker-compose -f docker-compose.production.yml up --build

It won't auto-reload, so you'll need to Ctrl-C and start it again if you change any code.

This Compose file is also used on CI for the browser tests so they are as close as possible to a production set up. This will catch problems like the static files not compiling properly.
