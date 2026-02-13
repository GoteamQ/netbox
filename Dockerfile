################################################################################
# Stage 1: Build — install compilers, build wheels, collect static
################################################################################
FROM python:3.12-slim AS builder

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
    binutils \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/netbox

# Install Python dependencies
COPY base_requirements.txt requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt \
    google-api-python-client \
    google-auth \
    google-auth-httplib2 \
    httplib2 \
    gunicorn \
    whitenoise

# Copy application
COPY . .

# Collect static files
WORKDIR /opt/netbox/netbox
RUN NETBOX_CONFIGURATION=netbox.configuration_docker \
    SECRET_KEY=build-only-key-that-is-at-least-fifty-characters-long-for-validation \
    ALLOWED_HOSTS=localhost \
    DB_HOST=localhost \
    REDIS_HOST=localhost \
    python manage.py collectstatic --no-input --verbosity 2

################################################################################
# Stage 2: Strip — compile .pyc, remove bloat, collect shared libs
################################################################################
FROM builder AS stripped

# Copy strip scripts
COPY scripts/strip-python.sh scripts/strip-app.sh scripts/copy-runtime-libs.sh /tmp/

RUN chmod +x /tmp/strip-python.sh /tmp/strip-app.sh /tmp/copy-runtime-libs.sh

# Strip Python site-packages (removes ~350MB of bloat)
RUN /tmp/strip-python.sh

# Strip application directory
WORKDIR /opt/netbox
RUN /tmp/strip-app.sh /opt/netbox

# Collect only the shared libraries needed at runtime
RUN /tmp/copy-runtime-libs.sh /runtime-libs

# Ensure libpython has proper soname + just one real copy
# Also clean /usr/local/lib of everything except python3.12 dir and libpython
RUN cd /usr/local/lib && \
    real=$(readlink -f libpython3.12.so.1.0) && \
    rm -f libpython3.12.so libpython3.12.so.1.0 && \
    cp "$real" libpython3.12.so.1.0 && \
    ln libpython3.12.so.1.0 libpython3.12.so && \
    find /usr/local/lib -maxdepth 1 -type f ! -name "libpython3.12*" -delete 2>/dev/null || true && \
    find /usr/local/lib -maxdepth 1 -type d ! -name "lib" ! -name "python3.12" -exec rm -rf {} + 2>/dev/null || true && \
    find /usr/local/lib -maxdepth 1 -type l ! -name "libpython3.12*" -delete 2>/dev/null || true

# Ensure python binary symlinks are proper
RUN cd /usr/local/bin && \
    rm -f python python3 && \
    ln -s python3.12 python3 && \
    ln -s python3.12 python

################################################################################
# Stage 3: Test — stripped site-packages + full app source (for testing)
################################################################################
FROM builder AS test

# Copy only the stripped site-packages (what production uses)
COPY --from=stripped /usr/local/lib/python3.12/site-packages/ /usr/local/lib/python3.12/site-packages/

# App source is intact from builder (tests included)
WORKDIR /opt/netbox/netbox

################################################################################
# Stage 4: Runtime — distroless minimal image
################################################################################
FROM gcr.io/distroless/base-debian12 AS runtime

# Copy Python interpreter
COPY --from=stripped /usr/local/bin/python3.12 /usr/local/bin/python3.12
COPY --from=stripped /usr/local/bin/python3 /usr/local/bin/python3
COPY --from=stripped /usr/local/bin/python /usr/local/bin/python
COPY --from=stripped /usr/local/bin/gunicorn /usr/local/bin/gunicorn

# Copy entire /usr/local/lib in one layer (python3.12 + libpython, hardlinks preserved)
COPY --from=stripped /usr/local/lib/ /usr/local/lib/

# Copy runtime shared libraries
COPY --from=stripped /runtime-libs/ /

# Refresh linker cache
# (distroless has no ldconfig, but we include ld.so.conf.d setup via the lib copy)

# Copy stripped application
COPY --from=stripped /opt/netbox /opt/netbox

# Install entrypoint
COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    LD_LIBRARY_PATH=/usr/local/lib \
    NETBOX_CONFIGURATION=netbox.configuration_docker

WORKDIR /opt/netbox/netbox

# distroless runs as nonroot (uid 65534) by default
USER nonroot

EXPOSE 8000

ENTRYPOINT ["python3", "/usr/local/bin/docker-entrypoint.sh"]
CMD ["web"]
