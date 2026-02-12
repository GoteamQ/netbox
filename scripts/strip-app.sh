#!/bin/bash
# strip-app.sh — Strip application directory for minimal runtime
# Removes source .py (keeps .pyc), dev files, and non-essential assets
set -e

APP_DIR="${1:-/opt/netbox}"

echo "=== Stripping app directory ==="

# ──────────────────────────────────────────────────
# 1. Remove files not needed at runtime
# ──────────────────────────────────────────────────
echo ">> Removing non-runtime files..."
cd "$APP_DIR"
rm -rf \
    .git .github .gitignore \
    .ruff_cache \
    docs contrib \
    mkdocs.yml pyproject.toml ruff.toml \
    cookies.txt login*.html page.html \
    CONTRIBUTING.md SECURITY.md NOTICE README.md LICENSE.txt CHANGELOG.md \
    cloudbuild.yaml \
    upgrade.sh \
    Dockerfile .dockerignore docker-compose*.yml

# Remove project-static (already collected into static/)
rm -rf "$APP_DIR/netbox/project-static"

# Remove test files
find "$APP_DIR/netbox" -type d -name "tests" -exec rm -rf {} + 2>/dev/null || true
find "$APP_DIR/netbox" -type f -name "test_*.py" -delete 2>/dev/null || true
find "$APP_DIR/netbox" -type f -name "*_test.py" -delete 2>/dev/null || true

# Remove migration .py (keep .pyc after compilation)
# Actually, keep migrations as Django needs them
# Remove scripts dir (verify/dev scripts)
rm -rf "$APP_DIR/scripts"

# ──────────────────────────────────────────────────
# 1b. Strip collected static files bloat
# ──────────────────────────────────────────────────
echo ">> Stripping static file bloat..."
STATIC_DIR="$APP_DIR/netbox/static"
if [ -d "$STATIC_DIR" ]; then
    # Remove drf_spectacular_sidecar statics (Swagger UI — 11MB)
    rm -rf "$STATIC_DIR/drf_spectacular_sidecar"
    # Remove graphiql statics (GraphQL browser UI — 3MB)
    rm -rf "$STATIC_DIR/graphiql"
    # Remove debug_toolbar statics
    rm -rf "$STATIC_DIR/debug_toolbar"
    # Remove admin statics (NetBox serves its own UI)
    rm -rf "$STATIC_DIR/admin/js/vendor"
    rm -rf "$STATIC_DIR/admin/fonts"
    # Remove source maps
    find "$STATIC_DIR" -name "*.map" -delete 2>/dev/null || true
    find "$STATIC_DIR" -name "*.map.gz" -delete 2>/dev/null || true
    # Remove .woff files (keep .woff2 which are smaller/better)
    find "$STATIC_DIR" -name "*.woff" ! -name "*.woff2" -delete 2>/dev/null || true
    # Remove .eot files (IE only, not needed)
    find "$STATIC_DIR" -name "*.eot" -delete 2>/dev/null || true
    find "$STATIC_DIR" -name "*.eot.gz" -delete 2>/dev/null || true
    # Remove .ttf files (keep woff2 for web serving)
    find "$STATIC_DIR" -name "*.ttf" -delete 2>/dev/null || true
    find "$STATIC_DIR" -name "*.ttf.gz" -delete 2>/dev/null || true
fi

# ──────────────────────────────────────────────────
# 2. Strip translations to English only
# ──────────────────────────────────────────────────
echo ">> Trimming translations..."
if [ -d "$APP_DIR/netbox/translations" ]; then
    find "$APP_DIR/netbox/translations" -mindepth 1 -maxdepth 1 -type d ! -name "en" -exec rm -rf {} +
fi

# ──────────────────────────────────────────────────
# 3. Compile app .py → .pyc
# ──────────────────────────────────────────────────
echo ">> Compiling app to .pyc..."
python -B -m compileall -b -q "$APP_DIR/netbox" 2>/dev/null || true

# Remove .py source files (keep .pyc)
# IMPORTANT: Keep manage.py, wsgi.py, configuration*.py as some are loaded by name
find "$APP_DIR/netbox" -name "*.py" \
    ! -name "manage.py" \
    ! -name "wsgi.py" \
    ! -name "asgi.py" \
    ! -name "configuration.py" \
    ! -name "configuration_example.py" \
    ! -name "configuration_testing.py" \
    -delete 2>/dev/null || true

# ──────────────────────────────────────────────────
# 4. Remove __pycache__ dirs (we compiled in-place)
# ──────────────────────────────────────────────────
find "$APP_DIR" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

echo ">> Done stripping app. Final size:"
du -sh "$APP_DIR"
