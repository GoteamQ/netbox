import os

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '*').split(',')

DATABASE = {
    'NAME': os.environ.get('DB_NAME', 'netbox'),
    'USER': os.environ.get('DB_USER', 'netbox'),
    'PASSWORD': os.environ.get('DB_PASSWORD', 'netbox'),
    'HOST': os.environ.get('DB_HOST', 'localhost'),
    'PORT': os.environ.get('DB_PORT', '5432'),
    'CONN_MAX_AGE': 300,
}

REDIS = {
    'tasks': {
        'HOST': os.environ.get('REDIS_HOST', 'localhost'),
        'PORT': int(os.environ.get('REDIS_PORT', 6379)),
        'DATABASE': 0,
        'SSL': False,
    },
    'caching': {
        'HOST': os.environ.get('REDIS_CACHE_HOST', os.environ.get('REDIS_HOST', 'localhost')),
        'PORT': int(os.environ.get('REDIS_CACHE_PORT', os.environ.get('REDIS_PORT', 6379))),
        'DATABASE': 1,
        'SSL': False,
    }
}

SECRET_KEY = os.environ.get('SECRET_KEY', 'r(m)9nLGnz$(_q3N4z1k(EFsMCjjjzx08x9VhNVcfd%6RF#r!6DE@+V5Zk2X')

DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

CSRF_TRUSTED_ORIGINS = [
    'http://localhost:8000',
    'http://127.0.0.1:8000',
    'https://localhost:8000',
    'https://127.0.0.1:8000',
]

LOGIN_REQUIRED = False

PLUGINS = []

PLUGINS_CONFIG = {}
