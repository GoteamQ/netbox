FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libxml2-dev \
    libxslt1-dev \
    libffi-dev \
    libssl-dev \
    zlib1g-dev \
    libjpeg62-turbo-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/netbox

# Install Python dependencies
COPY base_requirements.txt requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Install GCP discovery dependencies
RUN pip install --no-cache-dir \
    google-api-python-client \
    google-auth \
    google-auth-httplib2 \
    httplib2

# Collect static files
WORKDIR /opt/netbox/netbox
RUN mkdir -p /opt/netbox/netbox/static && \
    NETBOX_CONFIGURATION=netbox.configuration_example python manage.py collectstatic --no-input 2>/dev/null || true

# Entrypoint
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["web"]
