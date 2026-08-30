FROM node:22-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm install
COPY . .

# Стадия для локальной разработки: dev-сервер Vite с горячей перезагрузкой.
FROM deps AS dev
EXPOSE 5173
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

# Стадия для продакшна: собирает статику и кладёт её в том, откуда раздаёт Caddy.
FROM deps AS build
ARG VITE_API_BASE_URL
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
RUN npm run build
CMD ["sh", "-c", "rm -rf /srv/web/* && cp -r /app/dist/. /srv/web/"]
