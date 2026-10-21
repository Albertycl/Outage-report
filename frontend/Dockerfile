# Frontend: Quasar SPA built with node, served by nginx.

# ---------- build ----------
# package.json pins engines to node ^18 || ^16 || ^14.19; 18 is what the dev
# box builds with.
FROM node:18-alpine AS build

WORKDIR /app

# npm ci from the lockfile, before the source, so editing a .vue file does not
# reinstall 216MB of node_modules.
COPY package.json package-lock.json ./
RUN npm ci

COPY . .

# Built with a placeholder rather than a real URL: the backend address is a
# Vite build-time define, and baking it in here would mean one image per
# backend. docker/entrypoint.sh substitutes the real value at container start.
ENV API_BASE_URL=__API_BASE_URL__
RUN npx quasar build

# ---------- serve ----------
FROM nginx:alpine AS runtime

COPY --from=build /app/dist/spa /usr/share/nginx/html
COPY docker/nginx.conf /etc/nginx/conf.d/default.conf
COPY docker/entrypoint.sh /docker-entrypoint-api-url.sh

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD wget -qO- http://127.0.0.1/ >/dev/null || exit 1

ENTRYPOINT ["/docker-entrypoint-api-url.sh"]
CMD ["nginx", "-g", "daemon off;"]
