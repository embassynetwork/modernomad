FROM python:3.6.8-slim

RUN apt-get update -qq && apt-get install -yq \
    build-essential \
    curl \
    netcat

RUN curl -sL https://deb.nodesource.com/setup_10.x | bash
RUN apt-get update -qq && apt-get install -yq nodejs npm

# https://bitbucket.org/site/master/issues/16334/pipelines-failing-with-could-not-get-uid
# https://github.com/npm/npm/issues/20861
RUN npm config set unsafe-perm true

RUN npm install -g less

# Only copy requirements so cache isn't busted by changes in the app
RUN mkdir -p /app
COPY requirements.txt /app/
WORKDIR /app
RUN pip install --no-cache-dir -r requirements.txt

# Same, but for client
RUN mkdir -p /app/client
COPY client/package.json client/package-lock.json /app/client/
RUN cd client && npm install && npm cache clean --force

# Build client before copying everything so changes in Django don't trigger a
# re-build
COPY client /app/client
RUN cd client && node_modules/.bin/webpack --config webpack.prod.config.js

ENV PYTHONUNBUFFERED 1
# Set configuration last so we can change this without rebuilding the whole
# image
ENV DJANGO_SETTINGS_MODULE modernomad.settings.production
# Number of gunicorn workers
ENV WEB_CONCURRENCY 3
ENV PORT 8000
EXPOSE 8000
CMD ["gunicorn", "modernomad.wsgi"]

# Copy all files last, because this is most likely to change
COPY . /app/

RUN SECRET_KEY=unset ./manage.py collectstatic --noinput
RUN SECRET_KEY=unset ./manage.py compress
