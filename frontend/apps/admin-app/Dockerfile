FROM node:21-slim as builder

WORKDIR /usr/src/app

COPY ./frontend/package*.json ./

RUN npm install

COPY ./frontend .

RUN npm run admin:build

FROM nginx:alpine

WORKDIR /app

COPY --from=builder /usr/src/app/dist/apps/admin-app /app/frontend
COPY --from=builder /usr/src/app/dist/libs /app/frontend/libs

COPY ./frontend/default.nginx.conf /etc/nginx/conf.d/default.conf


COPY ./frontend/env.sh /app/env.sh

EXPOSE 8080

CMD ["nginx", "-g", "daemon off;"]
