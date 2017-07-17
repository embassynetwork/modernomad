FROM python:2-alpine

# So Pillow can find zlib
ENV LIBRARY_PATH /lib:/usr/lib

RUN apk add --no-cache \
  build-base \
  jpeg \
  jpeg-dev \
  libxslt \
  libxslt-dev \
  libxml2 \
  libxml2-dev \
  nodejs \
  postgresql-dev \
  postgresql-libs \
  zlib \
  zlib-dev

RUN npm install -g less

# Only copy requirements so cache isn't busted by changes in the app
RUN mkdir -p /app
COPY requirements.txt requirements.test.txt /app/
WORKDIR /app
RUN pip install --no-cache-dir -r requirements.txt -r requirements.test.txt

ENV DJANGO_SETTINGS_MODULE modernomad.settings_docker
EXPOSE 8000

COPY . /app/

CMD ["./manage.py", "runserver", "0.0.0.0:8000"]
