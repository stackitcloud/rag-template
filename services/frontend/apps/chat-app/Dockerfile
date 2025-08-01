FROM --platform=linux/amd64 node:21-slim as builder

WORKDIR /usr/src/app

COPY ./services/frontend/package*.json ./

RUN npm install

COPY ./services/frontend .

RUN npm run chat:build

FROM --platform=linux/amd64 nginx:alpine

WORKDIR /app

COPY --from=builder /usr/src/app/dist/apps/chat-app /app/frontend
COPY --from=builder /usr/src/app/dist/libs /app/frontend/libs

COPY ./services/frontend/default.nginx.conf /etc/nginx/conf.d/default.conf
COPY ./services/frontend/env.sh /app/env.sh

EXPOSE 8080

RUN chown -R nginx:nginx /var/cache/nginx
RUN touch /var/run/nginx.pid && chown nginx:nginx /var/run/nginx.pid

RUN apk del apk-tools && rm -rf /var/cache/apk/;

USER nginx

CMD ["nginx", "-g", "daemon off;"]
