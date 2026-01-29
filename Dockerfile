FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/opt/netbox/netbox

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        libldap2-dev \
        libsasl2-dev \
        libssl-dev \
        libffi-dev \
        curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/netbox

COPY requirements.txt /opt/netbox/requirements.txt
RUN pip install --no-cache-dir -r /opt/netbox/requirements.txt

COPY . /opt/netbox

EXPOSE 8000

CMD ["/bin/sh", "-c", "python netbox/manage.py migrate && python netbox/manage.py collectstatic --no-input && gunicorn netbox.wsgi:application --bind 0.0.0.0:8000"]
