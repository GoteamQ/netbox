#!/bin/bash
set -e

# Run database migrations
if [ "$1" = "web" ]; then
    echo "Running database migrations..."
    python manage.py migrate --no-input

    echo "Starting NetBox web server..."
    exec gunicorn netbox.wsgi \
        --bind 0.0.0.0:8000 \
        --workers "${GUNICORN_WORKERS:-3}" \
        --threads "${GUNICORN_THREADS:-3}" \
        --timeout "${GUNICORN_TIMEOUT:-120}" \
        --max-requests "${GUNICORN_MAX_REQUESTS:-5000}" \
        --max-requests-jitter "${GUNICORN_MAX_REQUESTS_JITTER:-500}" \
        --access-logfile - \
        --error-logfile -

elif [ "$1" = "worker" ]; then
    echo "Starting NetBox RQ worker..."
    exec python manage.py rqworker high default low

else
    exec "$@"
fi
