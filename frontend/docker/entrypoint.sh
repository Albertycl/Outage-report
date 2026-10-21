#!/bin/sh
# Rewrites the backend base URL into the built bundle at container start.
#
# The URL is a Vite build-time define (quasar.config.js -> build.env ->
# src/config/api.js), so it is normally frozen into the JS at `quasar build`.
# The image is built with the literal placeholder below instead, and this
# swaps in the real value here -- so one image runs against any backend and
# you do not rebuild to repoint it.
set -e

PLACEHOLDER='__API_BASE_URL__'
ROOT=/usr/share/nginx/html

if [ -z "$API_BASE_URL" ]; then
    echo "ERROR: API_BASE_URL is not set. Set it to the address the browser" >&2
    echo "       uses to reach the backend, e.g. /backend" >&2
    echo "       (this is resolved in the user's browser, not in the container," >&2
    echo "       so 'localhost' and the compose service name will not work)." >&2
    exit 1
fi

echo "pointing the frontend at $API_BASE_URL"

# Only the JS carries the define; scanning the images is wasted work.
find "$ROOT" -type f -name '*.js' -exec \
    sed -i "s|$PLACEHOLDER|$API_BASE_URL|g" {} +

if grep -rq "$PLACEHOLDER" "$ROOT" 2>/dev/null; then
    echo "WARNING: $PLACEHOLDER still present after substitution" >&2
fi

# nginx needs an explicit resolver for the per-request upstream lookup: use the
# container's own nameserver (Docker or cluster DNS) and a configurable upstream.
DNS_RESOLVER="$(awk '/^nameserver/ {print $2; exit}' /etc/resolv.conf)"
BACKEND_UPSTREAM="${BACKEND_UPSTREAM:-backend:5410}"
sed -i "s|__DNS_RESOLVER__|$DNS_RESOLVER|; s|__BACKEND_UPSTREAM__|$BACKEND_UPSTREAM|" /etc/nginx/conf.d/default.conf

exec "$@"
