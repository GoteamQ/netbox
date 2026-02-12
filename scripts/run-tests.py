#!/usr/bin/env python3
"""Patch configuration_testing.py for Docker network and run tests."""
import os
import subprocess
import sys

config_path = '/opt/netbox/netbox/netbox/configuration_testing.py'

with open(config_path, 'r') as f:
    content = f.read()

# Split at REDIS to handle DB and Redis sections separately
parts = content.split('REDIS = ')
# DB section: localhost -> db
parts[0] = parts[0].replace("'HOST': 'localhost'", "'HOST': 'db'")
parts[0] = parts[0].replace("'PORT': ''", "'PORT': '5432'")
# Redis section: localhost -> redis
if len(parts) > 1:
    parts[1] = parts[1].replace("'HOST': 'localhost'", "'HOST': 'redis'")
content = 'REDIS = '.join(parts)

with open(config_path, 'w') as f:
    f.write(content)

print("Patched configuration_testing.py for Docker network")

# Run tests
os.environ['NETBOX_CONFIGURATION'] = 'netbox.configuration_testing'
os.chdir('/opt/netbox/netbox')
sys.exit(subprocess.call(
    [sys.executable, 'manage.py', 'test', '--no-input', '-v', '2'] + sys.argv[1:]
))
