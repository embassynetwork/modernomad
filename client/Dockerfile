FROM node:8-alpine
RUN mkdir -p /app
WORKDIR /app
COPY package.json /app/
RUN npm install && npm cache clean --force
COPY . /app/
EXPOSE 3000
RUN ["node", "server.js"]
