FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    ca-certificates \
    curl \
    git \
    libffi-dev \
    libpq-dev \
    libssl-dev \
    libxml2-dev \
    libxslt1-dev \
    libldap2-dev \
    libsasl2-dev \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/netbox

COPY requirements.txt /opt/netbox/
RUN python -m venv /opt/netbox/venv \
    && /opt/netbox/venv/bin/pip install --upgrade pip wheel \
    && /opt/netbox/venv/bin/pip install -r requirements.txt \
    && /opt/netbox/venv/bin/pip install gunicorn \
    && /opt/netbox/venv/bin/pip install \
        google-cloud-compute \
        google-cloud-storage \
        google-cloud-container \
        google-cloud-resource-manager \
        google-api-python-client

COPY netbox /opt/netbox/netbox

COPY docker/configuration.py /opt/netbox/netbox/netbox/configuration.py
COPY docker/entrypoint.sh /opt/netbox/entrypoint.sh
COPY docker/housekeeping.sh /opt/netbox/housekeeping.sh

RUN chmod +x /opt/netbox/entrypoint.sh /opt/netbox/housekeeping.sh

RUN mkdir -p /opt/netbox/netbox/static \
    && mkdir -p /opt/netbox/netbox/media \
    && mkdir -p /opt/netbox/netbox/reports \
    && mkdir -p /opt/netbox/netbox/scripts

WORKDIR /opt/netbox/netbox

EXPOSE 8080

ENTRYPOINT ["/opt/netbox/entrypoint.sh"]
CMD ["/opt/netbox/venv/bin/gunicorn", "--bind", "0.0.0.0:8080", "--workers", "3", "netbox.wsgi:application"]
