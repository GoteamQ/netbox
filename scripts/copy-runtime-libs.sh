#!/bin/bash
# copy-runtime-libs.sh — Discover and copy only the shared libraries needed at runtime
# that are NOT already present in gcr.io/distroless/base-debian12
set -e

DEST="${1:-/runtime-libs}"
mkdir -p "$DEST"

echo "=== Collecting runtime shared libraries ==="

# ──────────────────────────────────────────────────
# Libraries already in gcr.io/distroless/base-debian12 — DO NOT COPY
# ──────────────────────────────────────────────────
DISTROLESS_LIBS=(
    ld-linux-aarch64
    ld-linux-x86-64
    libBrokenLocale
    libanl
    libc_malloc_debug
    libdl
    libmemusage
    libnss_compat
    libnss_dns
    libnss_files
    libnss_hesiod
    libpcprofile
    libpthread
    'librt\.so'
    libthread_db
    libutil
)
# Build a grep exclusion pattern
EXCLUDE_PATTERN=$(IFS='|'; echo "${DISTROLESS_LIBS[*]}")

# ──────────────────────────────────────────────────
# Collect all binaries that need shared libraries
# ──────────────────────────────────────────────────
ALL_BINARIES="/usr/local/bin/python3"

# All .so files in Python lib + site-packages (only actual files)
SO_FILES=$(find /usr/local/lib -name "*.so*" -type f 2>/dev/null || true)
ALL_BINARIES="$ALL_BINARIES $SO_FILES"

# Gunicorn
[ -f /usr/local/bin/gunicorn ] && ALL_BINARIES="$ALL_BINARIES /usr/local/bin/gunicorn"

# ──────────────────────────────────────────────────
# Trace shared library dependencies
# ──────────────────────────────────────────────────
ALL_DEPS=$(
    for f in $ALL_BINARIES; do
        ldd "$f" 2>/dev/null | awk '/=>/ {print $3}' | grep -v "not found"
    done | sort -u | grep -v '^$'
)

echo ">> Found $(echo "$ALL_DEPS" | wc -l) unique shared library deps (before filtering)"

# ──────────────────────────────────────────────────
# Filter out: libs in distroless, static archives, unneeded libs
# ──────────────────────────────────────────────────
FILTERED_DEPS=$(echo "$ALL_DEPS" \
    | grep -vE "$EXCLUDE_PATTERN" \
    | grep -v '\.a$' \
    | grep -v '/gconv/' \
    | grep -vE '(libmount|libmpfr|libmpc|libcc1|libctf|libdb-5|libcurl-gnutls|libreadline|libncurses|libtinfo|libgdbm|libsqlite3|libmvec|liblzma|ossaudiodev|libblkid)' \
    || true)

echo ">> After filtering: $(echo "$FILTERED_DEPS" | grep -c . || echo 0) libraries to copy"

# ──────────────────────────────────────────────────
# Copy each needed library — real file + soname only, no unversioned .so
# We avoid symlinks since Docker COPY resolves them to full copies
# ──────────────────────────────────────────────────
COPIED_REALS=""
for lib in $FILTERED_DEPS; do
    if [ -f "$lib" ] || [ -L "$lib" ]; then
        target_dir="$DEST$(dirname "$lib")"
        mkdir -p "$target_dir"

        # Resolve to the real file
        real=$(readlink -f "$lib")
        realbase=$(basename "$real")
        libbase=$(basename "$lib")

        # Only copy the real file once
        if [ -f "$real" ] && ! echo "$COPIED_REALS" | grep -qF "$real"; then
            cp "$real" "$target_dir/$realbase" 2>/dev/null || true
            COPIED_REALS="$COPIED_REALS $real"
        fi

        # If ldd referenced a different name (soname), hardlink to same file
        # Docker COPY will copy hardlinks as a single file
        if [ "$realbase" != "$libbase" ] && [ ! -e "$target_dir/$libbase" ]; then
            ln "$target_dir/$realbase" "$target_dir/$libbase" 2>/dev/null || \
            cp "$target_dir/$realbase" "$target_dir/$libbase" 2>/dev/null || true
        fi
    fi
done

# ──────────────────────────────────────────────────
# Strip debug symbols from all copied .so files
# ──────────────────────────────────────────────────
echo ">> Stripping debug symbols from runtime libs..."
find "$DEST" -name "*.so*" -type f -exec strip --strip-debug {} \; 2>/dev/null || true

# ──────────────────────────────────────────────────
# Copy the dynamic linker (must match the glibc version we copied)
# ──────────────────────────────────────────────────
echo ">> Copying dynamic linker..."
for ld in /lib/ld-linux-* /lib/aarch64-linux-gnu/ld-linux-* /lib/x86_64-linux-gnu/ld-linux-*; do
    if [ -e "$ld" ]; then
        target_dir="$DEST$(dirname "$ld")"
        mkdir -p "$target_dir"
        cp -aL "$ld" "$target_dir/" 2>/dev/null || true
    fi
done

echo ">> Runtime libs size:"
du -sh "$DEST"
echo ">> Runtime libs detail:"
find "$DEST" -type f -exec ls -lh {} \; 2>/dev/null | awk '{print $5, $NF}' | sort -rh | head -20
