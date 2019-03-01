# Deployment

This a description of how https://embassynetwork.com is set up, but you can also use it to set up your own instance of Modernomad.

## Creating app

Modernomad is designed to be deployed on Heroku inside Docker containers.

These commands, roughly, will get you set up with an app. Replace `embassynetwork-production` with a name for your app:

    $ heroku update beta
    $ heroku plugins:install @heroku-cli/plugin-manifest
    $ heroku apps:create --manifest --no-remote --stack=container embassynetwork-production
    $ heroku config:set -a embassynetwork-production SECRET_KEY=$(openssl rand -hex 64)

In the Heroku web UI, go to the app, then the "Deploy" tab, then connect it to a GitHub repo. Then, click "Deploy branch" at the bottom.

If you want to set up a Bucketeer bucket with a custom name:

    $ heroku addons:destroy -a embassynetwork-production BUCKETEER
    $ heroku addons:create -a embassynetwork-production bucketeer:micro --bucket-name media.embassynetwork.com

## Deployments

Trigger deployments through the Heroku web UI. It will automatically run `./manage.py migrate`.

## Scheduled tasks

In Heroku scheduler, add a daily task at 11:00 UTC: `./manage.py run_daily_tasks`

## Cloudflare

We are set up to use Cloudflare for DNS which also includes a CDN. 

## Static files

The Heroku app serves up static files (JS, CSS, etc.) directly, using [Whitenoise](http://whitenoise.evans.io/en/stable/).

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

## Media

We use the Heroku add-on "Bucketeer" to host media files on S3. Creates bucket
and puts creds inside Heroku environment variables, and does billing through
Heroku too. Inside the Django app we use django-storages which saves the files
to s3. Configuration is in the `settings.py`.

## Payments

Stripe is used for payment processing. 

## Email sending

Emails are sent using Mailgun. Using mailgun we configure routes to associate
with specific modernomad HTTP endpoints, which trigger function calls in the
code. 

Mailgun credentials are stored in Heroku environment variables. 


