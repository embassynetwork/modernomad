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

## Staging environment and Heroku Pipelines

On embassynetwork.com, we have a separate staging environment, https://staging.embassynetwork.com/, that is deployed on every commit to master. It has a complete copy of production data so we can check things work on real data.

Both the staging environment and production environment are part of a "[Pipeline](https://devcenter.heroku.com/articles/pipelines)" on Heroku. This allows us to see a high-level view of what state the app is in. It also allows you to create "[Review Apps](https://devcenter.heroku.com/articles/github-integration-review-apps)" of pull requests, which are like mini throwaway staging environments.

Deploys can be done either through the Heroku web interface (under the "Deploy" tab in the app) or on Slack, in the #modernomad_heroku channel. The advantage of doing it on Slack is that it will refuse to deploy if the build is broken, stopping you from deploying a broken version to production.

Heroku Pipelines has a "promotion" feature which is designed to deploy a build from staging directly to production. This means the exact same deployment from staging gets deployed to production, instead of it getting rebuilt from source code, which minimises the chances of breakage. Unfortunately this doesn't support Docker containers yet. Once it does, this could be used to deploy the app.

## Deployments

Trigger deployments through the Heroku web UI. It will automatically run `./manage.py migrate`.

## Scheduled tasks

In Heroku scheduler, add a daily task at 11:00 UTC: `./manage.py run_daily_tasks`

## Cloudflare

We are set up to use Cloudflare for DNS which also includes a CDN. All requests to the app go through Cloudflare, and it caches what it can. This is just static files and media currently -- both documented in more detail below.

## Static files

The Heroku app serves up static files (JS, CSS, etc.) directly, using [Whitenoise](http://whitenoise.evans.io/en/stable/).

Cloudflare sits in front of the Heroku app and caches the static files so each request doesn't hit the Heroku app.

### Caching

The main caveat you have to be aware of is that all static files have very long cache timeouts so they can be cached for a long time in Cloudflare and users' browsers. This means that if you change a static file, it has to be given a different filename for it to be updated.

This is done automatically by django_compressor for most CSS and JS in the app. For images, you will have to either rename the file or assume that some users will be seeing the old version.

In Django, there are various ways of adding the hash of the content of a static file to the filename, but this hasn't been implemented yet.

### Thumbnails

Thumbnails are generated with django-imagekit when a model is saved. If you change the thumbnail specification in the model, or need to regenerate the thumbnails for whatever reason, run `./manage.py generateimages`.

### Testing production static files locally

The Docker Compose file `docker-compose.production.yml` approximates a production setup so you can check the compilation of static files. Run it with:

    $ docker-compose -f docker-compose.production.yml up --build

It won't auto-reload, so you'll need to Ctrl-C and start it again if you change any code.

This Compose file is also used on CI for the browser tests so they are as close as possible to a production set up. This will catch problems like the static files not compiling properly.

## Media

Media files are hosted on S3. Setting up S3 buckets and IAM credentials is a PITA so we use the Heroku add-on "Bucketeer" to do that for us. It creates a bucket on S3 and adds the credentials to the Heroku config.

Inside the Django app, we use django-storages to save the files to S3. Configuration is in `settings/common.py`.

Cloudflare sits in front of the S3 bucket to handle caching and distribution. The trick to make this work is to give the bucket a custom name that is a full domain name, as shown in the "Creating app" section above. You can then use Cloudflare to proxy requests to it.

For example, for embassynetwork.com our S3 bucket is called `media.embassynetwork.com`, then we have a CNAME in Cloudflare called `media` which points at `media.embassynetwork.com.s3.amazonaws.com`.

## Payments

Stripe is used for payment processing. 

## Email sending

Emails are sent using Mailgun. Using mailgun we configure routes to associate
with specific modernomad HTTP endpoints, which trigger function calls in the
code. 

Mailgun credentials are stored in Heroku environment variables. 

## Backups

Backups are done with [heroku-tarsnap-backups](https://github.com/bfirsh/heroku-tarsnap-backups). It runs as a sidecar container alongside the main app and backs up both Heroku's Postgres database and the Bucketeer S3 bucket onto Tarsnap.
