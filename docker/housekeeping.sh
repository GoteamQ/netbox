#!/bin/bash

cd /opt/netbox/netbox

while true; do
  echo "Running housekeeping tasks..."
  /opt/netbox/venv/bin/python manage.py housekeeping
  echo "Housekeeping complete. Sleeping for 24 hours..."
  sleep 86400
done
