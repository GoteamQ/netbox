#!/bin/bash
# strip-python.sh — Aggressively strip Python installation for minimal runtime
# Run this in the builder stage after pip install to shrink site-packages
set -e

SITE_PACKAGES="${1:-/usr/local/lib/python3.12/site-packages}"
APP_DIR="${2:-/opt/netbox}"

echo "=== Stripping Python for production ==="
echo "  site-packages: $SITE_PACKAGES"
echo "  app dir:       $APP_DIR"

# ──────────────────────────────────────────────────
# 1. Remove packages not needed at runtime
# ──────────────────────────────────────────────────
echo ">> Removing build/doc tools..."
REMOVE_PACKAGES=(
    # Documentation tooling (not needed at runtime)
    mkdocs mkdocs_material mkdocs_material_extensions mkdocs_autorefs
    mkdocs_get_deps mkdocstrings mkdocstrings_python
    material  # mkdocs-material theme assets
    ghp_import
    griffe griffecli griffelib
    # Markdown extensions used by mkdocs only
    pymdownx pymdown_extensions pymdown-extensions
    backrefs
    # Package management
    pip pip-* setuptools* wheel* pkg_resources
    # Not needed at runtime
    colorama
    # Rich — terminal rendering, not needed in production container
    rich django_rich
    # Debug toolbar — not for production
    debug_toolbar django_debug_toolbar
    django_graphiql_debug_toolbar graphiql_debug_toolbar
    # drf-spectacular-sidecar — keep module but strip statics (done in step 6)
    # Pygments — syntax highlighting for DRF browsable API (not needed headless)
    pygments
    # text-unidecode — only used by python-slugify at install time
    text_unidecode
    # pyasn1 modules — large ASN.1 definitions, only needed if doing complex cert parsing
    # (keep pyasn1 base, remove the big modules collection if not needed)
    # pyparsing — needed at runtime by httplib2 / google-api-python-client
    # pyparsing
)
for pkg in "${REMOVE_PACKAGES[@]}"; do
    rm -rf "$SITE_PACKAGES"/$pkg "$SITE_PACKAGES"/$pkg-*.dist-info
done

# ──────────────────────────────────────────────────
# 2. Strip tests, docs, examples from all packages
# ──────────────────────────────────────────────────
echo ">> Removing tests, docs, examples..."
# Remove test directories but preserve django/test (DRF depends on it)
find "$SITE_PACKAGES" -type d \( \
    -name "test" -o -name "tests" -o -name "testing" \
    -o -name "test_*" -o -name "*_test" \
    -o -name "docs" -o -name "doc" -o -name "examples" \
    -o -name "example" -o -name "samples" \
    -o -name "__pycache__" \
\) ! -path "*/django/test" ! -path "*/django/test/*" \
   -exec rm -rf {} + 2>/dev/null || true

# ──────────────────────────────────────────────────
# 3. Strip type stubs, .pyi, .pth, dist-info bloat
# ──────────────────────────────────────────────────
echo ">> Removing type stubs, dist-info extras..."
# Remove general bloat files but NOT inside dist-info (handled separately below)
find "$SITE_PACKAGES" -type f \( \
    -name "*.pyi" -o -name "*.typed" \
    -o -name "*.pth" \
    -o -name "AUTHORS*" -o -name "CHANGELOG*" -o -name "CHANGES*" \
    -o -name "HISTORY*" -o -name "NEWS*" \
    -o -name "README*" -o -name "*.md" -o -name "*.rst" \
    -o -name "COPYING*" \
\) ! -path "*dist-info*" -delete 2>/dev/null || true

# Clean dist-info dirs: keep METADATA, top_level.txt, entry_points.txt
find "$SITE_PACKAGES" -type d -name "*.dist-info" | while read d; do
    find "$d" -type f ! -name "METADATA" ! -name "top_level.txt" ! -name "entry_points.txt" -delete 2>/dev/null || true
done

# ──────────────────────────────────────────────────
# 4. Trim locale data (babel, django, pytz)
# ──────────────────────────────────────────────────
echo ">> Trimming locale/i18n data..."
# Babel: keep only English + core data
if [ -d "$SITE_PACKAGES/babel/locale-data" ]; then
    find "$SITE_PACKAGES/babel/locale-data" -type f ! -name "en*" ! -name "root*" -delete
fi
if [ -d "$SITE_PACKAGES/babel/global.dat" ]; then
    : # keep
fi

# Django: keep only English locale
if [ -d "$SITE_PACKAGES/django/conf/locale" ]; then
    find "$SITE_PACKAGES/django/conf/locale" -mindepth 1 -maxdepth 1 -type d ! -name "en*" -exec rm -rf {} +
fi
if [ -d "$SITE_PACKAGES/django/contrib/admin/locale" ]; then
    find "$SITE_PACKAGES/django/contrib/admin/locale" -mindepth 1 -maxdepth 1 -type d ! -name "en*" -exec rm -rf {} +
fi

# pytz: trim zone data (keep only UTC, basic zones)
if [ -d "$SITE_PACKAGES/pytz/zoneinfo" ]; then
    find "$SITE_PACKAGES/pytz/zoneinfo" -type f ! -name "UTC" ! -name "zone.tab" ! -name "iso3166.tab" -delete 2>/dev/null || true
    find "$SITE_PACKAGES/pytz/zoneinfo" -empty -type d -delete 2>/dev/null || true
fi

# tzdata: trim to just UTC and common timezones
if [ -d "$SITE_PACKAGES/tzdata/zoneinfo" ]; then
    # Keep top level files and the key timezone dirs
    find "$SITE_PACKAGES/tzdata/zoneinfo" -mindepth 1 -maxdepth 1 -type d \
        ! -name "Etc" ! -name "UTC" -exec rm -rf {} + 2>/dev/null || true
fi

# ──────────────────────────────────────────────────
# 5. Strip googleapiclient discovery cache
# ──────────────────────────────────────────────────
echo ">> Stripping googleapiclient discovery cache..."
if [ -d "$SITE_PACKAGES/googleapiclient/discovery_cache" ]; then
    rm -rf "$SITE_PACKAGES/googleapiclient/discovery_cache/documents"
fi

# ──────────────────────────────────────────────────
# 6. Strip drf-spectacular-sidecar static files
# ──────────────────────────────────────────────────
echo ">> Stripping drf-spectacular-sidecar statics..."
rm -rf "$SITE_PACKAGES/drf_spectacular_sidecar/static" 2>/dev/null || true

# ──────────────────────────────────────────────────
# 6b. Strip Django — remove unused contrib apps and admin assets
#     NetBox only uses: auth, contenttypes, sessions, messages, staticfiles, humanize
# ──────────────────────────────────────────────────
echo ">> Stripping Django unused contrib and admin assets..."
# Remove entire contrib apps not used by NetBox
# NOTE: django.contrib.admin must stay (gcp/admin.py imports it), but strip its assets
# NOTE: django.contrib.admindocs must stay (DRF rest_framework.schemas.generators imports it)
rm -rf "$SITE_PACKAGES/django/contrib/admin/static" 2>/dev/null || true
rm -rf "$SITE_PACKAGES/django/contrib/admin/templates" 2>/dev/null || true
rm -rf "$SITE_PACKAGES/django/contrib/admin/locale" 2>/dev/null || true
rm -rf "$SITE_PACKAGES/django/contrib/admindocs/templates" 2>/dev/null || true
rm -rf "$SITE_PACKAGES/django/contrib/admindocs/locale" 2>/dev/null || true
rm -rf "$SITE_PACKAGES/django/contrib/flatpages" 2>/dev/null || true
rm -rf "$SITE_PACKAGES/django/contrib/redirects" 2>/dev/null || true
rm -rf "$SITE_PACKAGES/django/contrib/sitemaps" 2>/dev/null || true
rm -rf "$SITE_PACKAGES/django/contrib/syndication" 2>/dev/null || true
# Remove DRF browsable API templates & static
rm -rf "$SITE_PACKAGES/rest_framework/static/rest_framework/docs" 2>/dev/null || true
rm -rf "$SITE_PACKAGES/rest_framework/static/rest_framework/css/prettify.css" 2>/dev/null || true
rm -rf "$SITE_PACKAGES/rest_framework/static/rest_framework/js/prettify*" 2>/dev/null || true

# ──────────────────────────────────────────────────
# 6c. Strip Pillow bundled libs — strip debug but keep the libs
#     PIL C extensions have rpath pointing to pillow.libs/ for bundled libs
#     (libtiff, libwebp, etc.) We must keep them but can strip debug symbols.
# ──────────────────────────────────────────────────
echo ">> Stripping pillow.libs debug symbols..."
find "$SITE_PACKAGES/pillow.libs" -name "*.so*" -exec strip --strip-debug {} \; 2>/dev/null || true
# Remove tkinter support (not needed)
rm -f "$SITE_PACKAGES/PIL/_imagingtk"*.so 2>/dev/null || true

# ──────────────────────────────────────────────────
# 6d. Strip cryptography — remove hazmat test vectors & backends not needed
# ──────────────────────────────────────────────────
echo ">> Stripping cryptography bloat..."
rm -rf "$SITE_PACKAGES/cryptography/hazmat/bindings/_rust/__pycache__" 2>/dev/null || true
find "$SITE_PACKAGES/cryptography" -name "*.pyi" -delete 2>/dev/null || true
# Strip the large Rust-compiled .so
find "$SITE_PACKAGES/cryptography" -name "*.so" -exec strip --strip-debug {} \; 2>/dev/null || true

# ──────────────────────────────────────────────────
# 7. Strip .c, .h, .cpp source files from native exts
# ──────────────────────────────────────────────────
echo ">> Removing C/C++ source files..."
find "$SITE_PACKAGES" -type f \( -name "*.c" -o -name "*.h" -o -name "*.cpp" \) -delete

# ──────────────────────────────────────────────────
# 8. Strip .so debug symbols
# ──────────────────────────────────────────────────
echo ">> Stripping .so debug symbols..."
find "$SITE_PACKAGES" -name "*.so" -exec strip --strip-debug {} \; 2>/dev/null || true
find /usr/local/lib -name "*.so*" -exec strip --strip-debug {} \; 2>/dev/null || true

# ──────────────────────────────────────────────────
# 9. Compile all .py → .pyc and remove .py source
# ──────────────────────────────────────────────────
echo ">> Compiling .py to .pyc..."
python -B -m compileall -b -q "$SITE_PACKAGES" 2>/dev/null || true
find "$SITE_PACKAGES" -name "*.py" ! -name "__init__.py" -delete
# Ensure __init__.py files are also compiled but keep the .pyc
find "$SITE_PACKAGES" -name "__init__.py" -exec python -B -m compileall -b -q {} \; 2>/dev/null || true
# Now we can remove __init__.py too since .pyc exists
find "$SITE_PACKAGES" -name "__init__.py" -delete 2>/dev/null || true

# ──────────────────────────────────────────────────
# 10. Strip stdlib (remove test, unused modules)
# ──────────────────────────────────────────────────
echo ">> Stripping Python stdlib..."
STDLIB="/usr/local/lib/python3.12"

# Remove entire stdlib directories not needed at runtime
rm -rf \
    "$STDLIB/test" "$STDLIB/tests" \
    "$STDLIB/tkinter" \
    "$STDLIB/idlelib" \
    "$STDLIB/turtle.py" "$STDLIB/turtle.pyc" "$STDLIB/turtledemo" \
    "$STDLIB/lib2to3" \
    "$STDLIB/pydoc.py" "$STDLIB/pydoc.pyc" "$STDLIB/pydoc_data" \
    "$STDLIB/ensurepip" \
    "$STDLIB/venv" \
    "$STDLIB/distutils" \
    "$STDLIB/xmlrpc" \
    "$STDLIB/doctest.py" "$STDLIB/doctest.pyc" \
    "$STDLIB/pdb.py" "$STDLIB/pdb.pyc" \
    "$STDLIB/profile.py" "$STDLIB/profile.pyc" \
    "$STDLIB/pstats.py" "$STDLIB/pstats.pyc" \
    "$STDLIB/cProfile.py" "$STDLIB/cProfile.pyc" \
    "$STDLIB/trace.py" "$STDLIB/trace.pyc" \
    "$STDLIB/tabnanny.py" "$STDLIB/tabnanny.pyc" \
    "$STDLIB/this.py" "$STDLIB/this.pyc" \
    "$STDLIB/antigravity.py" "$STDLIB/antigravity.pyc" \
    "$STDLIB/webbrowser.py" "$STDLIB/webbrowser.pyc" \
    "$STDLIB/mailbox.py" "$STDLIB/mailbox.pyc" \
    "$STDLIB/mailcap.py" "$STDLIB/mailcap.pyc" \
    "$STDLIB/imghdr.py" "$STDLIB/imghdr.pyc" \
    "$STDLIB/sndhdr.py" "$STDLIB/sndhdr.pyc" \
    "$STDLIB/nntplib.py" "$STDLIB/nntplib.pyc" \
    "$STDLIB/poplib.py" "$STDLIB/poplib.pyc" \
    "$STDLIB/imaplib.py" "$STDLIB/imaplib.pyc" \
    "$STDLIB/ftplib.py" "$STDLIB/ftplib.pyc" \
    "$STDLIB/telnetlib.py" "$STDLIB/telnetlib.pyc" \
    "$STDLIB/aifc.py" "$STDLIB/aifc.pyc" \
    "$STDLIB/sunau.py" "$STDLIB/sunau.pyc" \
    "$STDLIB/wave.py" "$STDLIB/wave.pyc" \
    "$STDLIB/chunk.py" "$STDLIB/chunk.pyc" \
    "$STDLIB/cgi.py" "$STDLIB/cgi.pyc" \
    "$STDLIB/cgitb.py" "$STDLIB/cgitb.pyc" \
    "$STDLIB/config-3.12-"* \
    2>/dev/null || true

# Remove stdlib .py source files (keep .pyc) — compile first
echo ">> Compiling stdlib to .pyc..."
python -B -m compileall -b -q "$STDLIB" 2>/dev/null || true
# Remove .py source, keep only .pyc (the -b flag puts .pyc next to .py)
find "$STDLIB" -path "$SITE_PACKAGES" -prune -o -name "*.py" ! -name "__init__.py" -type f -delete 2>/dev/null || true
find "$STDLIB" -path "$SITE_PACKAGES" -prune -o -name "__init__.py" -type f -delete 2>/dev/null || true

# Strip encodings — keep only commonly needed ones
echo ">> Stripping unused encodings..."
if [ -d "$STDLIB/encodings" ]; then
    KEEP_ENCODINGS="__init__|aliases|ascii|base64_codec|charmap|cp437|hex_codec|idna|latin_1|raw_unicode_escape|unicode_escape|utf_8|utf_8_sig|utf_16|utf_16_be|utf_16_le|utf_32|utf_32_be|utf_32_le|mbcs|undefined|punycode|iso8859_1|iso8859_15"
    find "$STDLIB/encodings" -maxdepth 1 -type f \( -name "*.py" -o -name "*.pyc" \) | while read f; do
        base=$(basename "$f" | sed 's/\.\(py\|pyc\)$//')
        if ! echo "$base" | grep -qE "^($KEEP_ENCODINGS)$"; then
            rm -f "$f"
        fi
    done
fi

# ──────────────────────────────────────────────────
# 10b. Strip lib-dynload — remove C extensions not needed at runtime
# ──────────────────────────────────────────────────
echo ">> Stripping unused lib-dynload modules..."
DYNLOAD="$STDLIB/lib-dynload"

# Remove test modules (~700KB)
rm -f "$DYNLOAD"/_test*.so 2>/dev/null || true

# Remove CJK codec modules (~1.1MB) — not needed for English-only deployment
rm -f "$DYNLOAD"/_codecs_jp*.so "$DYNLOAD"/_codecs_hk*.so \
      "$DYNLOAD"/_codecs_cn*.so "$DYNLOAD"/_codecs_kr*.so \
      "$DYNLOAD"/_codecs_tw*.so "$DYNLOAD"/_codecs_iso2022*.so \
      2>/dev/null || true

# Remove unused modules
rm -f "$DYNLOAD"/_tkinter*.so \
      "$DYNLOAD"/ossaudiodev*.so \
      "$DYNLOAD"/spwd*.so \
      "$DYNLOAD"/audioop*.so \
      "$DYNLOAD"/_curses*.so \
      "$DYNLOAD"/_gdbm*.so \
      "$DYNLOAD"/_dbm*.so \
      "$DYNLOAD"/_sqlite3*.so \
      "$DYNLOAD"/xxlimited*.so \
      "$DYNLOAD"/xxsubtype*.so \
      "$DYNLOAD"/_xxinterpchannels*.so \
      "$DYNLOAD"/_xxsubinterpreters*.so \
      "$DYNLOAD"/_xxtestfuzz*.so \
      "$DYNLOAD"/_lsprof*.so \
      "$DYNLOAD"/_crypt*.so \
      "$DYNLOAD"/readline*.so \
      "$DYNLOAD"/termios*.so \
      "$DYNLOAD"/syslog*.so \
      "$DYNLOAD"/resource*.so \
      "$DYNLOAD"/_lzma*.so \
      "$DYNLOAD"/_bz2*.so \
      "$DYNLOAD"/cmath*.so \
      "$DYNLOAD"/_ctypes_test*.so \
      2>/dev/null || true

# Strip debug symbols from remaining lib-dynload modules
find "$DYNLOAD" -name "*.so" -exec strip --strip-debug {} \; 2>/dev/null || true

# ──────────────────────────────────────────────────
# 10c. Strip libpython shared library
# ──────────────────────────────────────────────────
echo ">> Stripping libpython debug symbols..."
find /usr/local/lib -maxdepth 1 -name "libpython3.12.so*" -type f \
    -exec strip --strip-debug {} \; 2>/dev/null || true

find "$STDLIB" -path "$SITE_PACKAGES" -prune -o -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

echo ">> Done stripping."
echo ">> site-packages size:"
du -sh "$SITE_PACKAGES"
echo ">> lib-dynload size:"
du -sh "$DYNLOAD"
echo ">> stdlib total size:"
du -sh "$STDLIB"
echo ">> libpython size:"
ls -lh /usr/local/lib/libpython3.12.so* 2>/dev/null || true
