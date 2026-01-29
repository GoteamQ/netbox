#!/bin/bash
set -e

echo "Waiting for PostgreSQL..."
until PGPASSWORD=$DB_PASSWORD psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -c '\q' 2>/dev/null; do
  echo "PostgreSQL is unavailable - sleeping"
  sleep 2
done
echo "PostgreSQL is up!"

cd /opt/netbox/netbox

echo "Running database migrations..."
/opt/netbox/venv/bin/python manage.py migrate --no-input

echo "Collecting static files..."
/opt/netbox/venv/bin/python manage.py collectstatic --no-input

if [ "$SKIP_SUPERUSER" != "true" ]; then
  echo "Creating superuser..."
  /opt/netbox/venv/bin/python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
import os
username = os.environ.get('SUPERUSER_NAME', 'admin')
email = os.environ.get('SUPERUSER_EMAIL', 'admin@example.com')
password = os.environ.get('SUPERUSER_PASSWORD', 'admin')
if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email=email, password=password)
    print(f'Superuser {username} created.')
else:
    print(f'Superuser {username} already exists.')
EOF
fi

echo "Starting NetBox..."
exec "$@"
