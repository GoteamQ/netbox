#!/usr/bin/env python3
"""Inspect image sizes for optimization."""
import os

def dir_size(path):
    total = 0
    for root, dirs, files in os.walk(path):
        for f in files:
            try:
                total += os.path.getsize(os.path.join(root, f))
            except Exception:
                pass
    return total

def mb(n):
    return f"{n/1024/1024:8.2f} MB"

print("=== TOP LEVEL BREAKDOWN ===")
paths = [
    ("/usr/local/lib/python3.12/site-packages", "site-packages"),
    ("/usr/local/lib/python3.12/lib-dynload", "lib-dynload"),
    ("/usr/local/lib/python3.12", "python3.12 (total with site-packages)"),
    ("/opt/netbox", "app"),
]
for path, label in paths:
    print(f"  {mb(dir_size(path))}  {label}")

# libpython
for f in os.listdir("/usr/local/lib"):
    fp = os.path.join("/usr/local/lib", f)
    if "python" in f.lower() and not os.path.isdir(fp):
        s = os.path.getsize(fp)
        lnk = " -> " + os.readlink(fp) if os.path.islink(fp) else ""
        print(f"  {mb(s)}  /usr/local/lib/{f}{lnk}")

print("\n=== SITE-PACKAGES TOP 30 ===")
sp = "/usr/local/lib/python3.12/site-packages"
sizes = {}
for item in os.listdir(sp):
    p = os.path.join(sp, item)
    sizes[item] = dir_size(p) if os.path.isdir(p) else os.path.getsize(p)
for k, v in sorted(sizes.items(), key=lambda x: -x[1])[:30]:
    print(f"  {mb(v)}  {k}")

# Django deep dive
print("\n=== DJANGO INTERNALS (>100KB) ===")
django_dir = os.path.join(sp, "django")
if os.path.isdir(django_dir):
    for item in sorted(os.listdir(django_dir)):
        p = os.path.join(django_dir, item)
        s = dir_size(p) if os.path.isdir(p) else os.path.getsize(p)
        if s > 100000:
            print(f"  {mb(s)}  django/{item}")
    # contrib breakdown
    contrib = os.path.join(django_dir, "contrib")
    if os.path.isdir(contrib):
        print("\n=== DJANGO CONTRIB ===")
        for item in sorted(os.listdir(contrib)):
            p = os.path.join(contrib, item)
            s = dir_size(p) if os.path.isdir(p) else os.path.getsize(p)
            if s > 50000:
                print(f"  {mb(s)}  django/contrib/{item}")

# Cryptography deep dive
print("\n=== CRYPTOGRAPHY ===")
cr = os.path.join(sp, "cryptography")
if os.path.isdir(cr):
    for item in sorted(os.listdir(cr)):
        p = os.path.join(cr, item)
        s = dir_size(p) if os.path.isdir(p) else os.path.getsize(p)
        if s > 50000:
            print(f"  {mb(s)}  cryptography/{item}")

# Runtime libs
print("\n=== RUNTIME LIBS >200KB ===")
seen = set()
for search_root in ["/lib", "/usr/lib"]:
    if not os.path.isdir(search_root):
        continue
    for root, dirs, files in os.walk(search_root):
        for f in files:
            p = os.path.join(root, f)
            if p in seen:
                continue
            seen.add(p)
            try:
                s = os.path.getsize(p)
                lnk = ""
                if os.path.islink(p):
                    lnk = f" -> {os.readlink(p)}"
                if s > 200000:
                    print(f"  {mb(s)}  {p}{lnk}")
            except Exception:
                pass

print("\n=== APP SUBDIRS ===")
netbox_dir = "/opt/netbox/netbox"
if os.path.isdir(netbox_dir):
    for item in sorted(os.listdir(netbox_dir)):
        p = os.path.join(netbox_dir, item)
        s = dir_size(p) if os.path.isdir(p) else os.path.getsize(p)
        if s > 50000:
            print(f"  {mb(s)}  netbox/{item}")
