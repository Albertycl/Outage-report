#!/bin/sh
# Concept demo: no migrations and no pollers. On start-up the schema and the
# made-up demo rows are loaded into DATABASE_URL, then gunicorn serves them.
set -e

: "${DATABASE_URL:?set DATABASE_URL}"
: "${GUNICORN_WORKERS:=2}"
: "${GUNICORN_THREADS:=4}"
: "${BIND:=0.0.0.0:5410}"
export APP_CONFIG="${APP_CONFIG:-production}"

python load_sql.py

exec gunicorn \
    --bind "$BIND" \
    --workers "$GUNICORN_WORKERS" \
    --threads "$GUNICORN_THREADS" \
    --access-logfile - \
    --error-logfile - \
    main_outage:app
