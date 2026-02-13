"""
Docker-oriented NetBox configuration.
All settings are read from environment variables with sensible defaults
so that the image can be configured entirely at runtime.
"""
import os


def get_env(name, default=None):
    return os.getenv(name, default)


def get_env_bool(name, default=False):
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def get_env_int(name, default=None):
    value = os.getenv(name)
    if value is None or value == "":
        return default
    return int(value)


def get_env_list(name, default=None):
    value = os.getenv(name)
    if value is None:
        return default or []
    return [item.strip() for item in value.split(",") if item.strip()]


ALLOWED_HOSTS = get_env_list("ALLOWED_HOSTS", ["*"])

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": get_env("DB_NAME", "netbox"),
        "USER": get_env("DB_USER", "netbox"),
        "PASSWORD": get_env("DB_PASSWORD", "netbox"),
        "HOST": get_env("DB_HOST", "localhost"),
        "PORT": get_env("DB_PORT", "5432"),
        "CONN_MAX_AGE": 300,
    }
}

REDIS = {
    "tasks": {
        "HOST": get_env("REDIS_HOST", "localhost"),
        "PORT": get_env_int("REDIS_PORT", 6379),
        "USERNAME": get_env("REDIS_USERNAME", ""),
        "PASSWORD": get_env("REDIS_PASSWORD", ""),
        "DATABASE": get_env_int("REDIS_TASKS_DB", 0),
        "SSL": get_env_bool("REDIS_SSL", False),
    },
    "caching": {
        "HOST": get_env("REDIS_HOST", "localhost"),
        "PORT": get_env_int("REDIS_PORT", 6379),
        "USERNAME": get_env("REDIS_USERNAME", ""),
        "PASSWORD": get_env("REDIS_PASSWORD", ""),
        "DATABASE": get_env_int("REDIS_CACHE_DB", 1),
        "SSL": get_env_bool("REDIS_SSL", False),
    },
}

SECRET_KEY = get_env("SECRET_KEY", "change-me-please")

API_TOKEN_PEPPERS = {}
DEBUG = get_env_bool("DEBUG", False)
DEVELOPER = get_env_bool("DEVELOPER", False)

# Log everything to console at DEBUG level
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
        }
    },
    "root": {
        "handlers": ["console"],
        "level": "DEBUG",
    },
}
