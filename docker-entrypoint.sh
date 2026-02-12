#!/usr/bin/env python3
"""Docker entrypoint for NetBox — pure Python, no shell required."""
import os
import socket
import subprocess
import sys
import time


def wait_for_db():
    host = os.environ.get("DB_HOST", "localhost")
    port = int(os.environ.get("DB_PORT", "5432"))
    retries = int(os.environ.get("DB_WAIT_RETRIES", "30"))
    delay = int(os.environ.get("DB_WAIT_DELAY", "2"))

    print(f"Waiting for database at {host}:{port}...")
    for attempt in range(1, retries + 1):
        try:
            s = socket.create_connection((host, port), timeout=3)
            s.close()
            print("Database is ready.")
            return
        except (OSError, ConnectionRefusedError):
            print(f"  attempt {attempt}/{retries} — retrying in {delay}s...")
            time.sleep(delay)

    print(f"ERROR: Database not reachable after {retries} attempts.", file=sys.stderr)
    sys.exit(1)


def run(args):
    """Run a command, replacing the current process."""
    os.execvp(args[0], args)


def main():
    if len(sys.argv) < 2:
        print("Usage: docker-entrypoint.sh <web|worker|migrate> [args...]", file=sys.stderr)
        sys.exit(1)

    command = sys.argv[1]

    if command == "web":
        wait_for_db()

        if os.environ.get("RUN_MIGRATIONS", "true").lower() == "true":
            print("Running database migrations...")
            subprocess.check_call(["python", "manage.py", "migrate", "--no-input"])

        workers = os.environ.get("GUNICORN_WORKERS", "3")
        threads = os.environ.get("GUNICORN_THREADS", "3")
        timeout = os.environ.get("GUNICORN_TIMEOUT", "120")
        max_req = os.environ.get("GUNICORN_MAX_REQUESTS", "5000")
        max_jit = os.environ.get("GUNICORN_MAX_REQUESTS_JITTER", "500")

        print("Starting NetBox web server...")
        run([
            "gunicorn", "netbox.wsgi",
            "--bind", "0.0.0.0:8000",
            "--workers", workers,
            "--threads", threads,
            "--timeout", timeout,
            "--max-requests", max_req,
            "--max-requests-jitter", max_jit,
            "--access-logfile", "-",
            "--error-logfile", "-",
        ])

    elif command == "worker":
        wait_for_db()
        print("Starting NetBox RQ worker...")
        run(["python", "manage.py", "rqworker", "high", "default", "low"])

    elif command == "migrate":
        wait_for_db()
        print("Running database migrations...")
        run(["python", "manage.py", "migrate", "--no-input"])

    else:
        # Pass through arbitrary commands
        run(sys.argv[1:])


if __name__ == "__main__":
    main()
