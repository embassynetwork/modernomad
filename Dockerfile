FROM alpine
RUN apk upgrade --update && \
    apk add build-base py-pip python-dev postgresql-dev libxml2-dev libxslt-dev jpeg-dev zlib-dev && \
    pip install --upgrade pip

COPY . /app
WORKDIR /app

ENV LIBRARY_PATH /lib:/usr/lib

RUN pip install -r requirements.txt && \
    pip install --index-url https://code.stripe.com --upgrade stripe && \
    npm install -g less && \
    cd client && npm install && \
    node_modules/.bin/webpack --config webpack.prod.config.js

EXPOSE 80

