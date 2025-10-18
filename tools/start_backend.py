#!/usr/bin/env python3
"""
Small utility to start the FastAPI backend when running locally.

Strategy (best-effort):
 1. If /health responds, do nothing.
 2. Try to start the backend with `python -m uvicorn app.main:app --host 127.0.0.1 --port 8000` in background.
 3. If uvicorn isn't available or that fails, fall back to `docker-compose up -d api` if docker-compose is present.

The script prints helpful log lines and writes a short log to ./logs/backend_start.log.
"""
import os
import sys
import subprocess
import time
import urllib.request

ROOT = os.path.dirname(os.path.dirname(__file__))
LOG_DIR = os.path.join(ROOT, "logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_PATH = os.path.join(LOG_DIR, "backend_start.log")

def log(msg: str):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}\n"
    with open(LOG_PATH, "a") as f:
        f.write(line)
    print(line, end="")

def health_ok(url: str = "http://127.0.0.1:8000/health", timeout: int = 2) -> bool:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as r:
            return r.status == 200
    except Exception:
        return False

def try_uvicorn():
    cmd = [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"]
    log(f"Attempting to start backend with: {' '.join(cmd)}")
    try:
        # Start detached on POSIX
        p = subprocess.Popen(cmd, cwd=ROOT, stdout=open(LOG_PATH, "a"), stderr=subprocess.STDOUT, preexec_fn=os.setsid)
        log(f"Started uvicorn process, pid={p.pid}")
        return True
    except FileNotFoundError:
        log("uvicorn module not found (or python executable not found).")
        return False
    except Exception as e:
        log(f"Failed to start uvicorn: {e}")
        return False

def try_docker_compose():
    cmd = ["docker-compose", "up", "-d", "api"]
    log(f"Falling back to docker-compose: {' '.join(cmd)}")
    try:
        r = subprocess.run(cmd, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        log(r.stdout or "(no output)")
        return r.returncode == 0
    except FileNotFoundError:
        log("docker-compose not found in PATH.")
        return False
    except Exception as e:
        log(f"docker-compose failed: {e}")
        return False

def main():
    log("=== start_backend.py invoked ===")
    if health_ok():
        log("Backend already healthy. Nothing to do.")
        return 0

    # First, try uvicorn in-process
    if try_uvicorn():
        # give it a few seconds to bind
        for i in range(20):
            if health_ok():
                log("Backend became healthy after starting uvicorn.")
                return 0
            time.sleep(0.5)
        log("Timed out waiting for backend started by uvicorn to become healthy.")

    # Next try docker-compose
    if try_docker_compose():
        for i in range(30):
            if health_ok():
                log("Backend became healthy after docker-compose up.")
                return 0
            time.sleep(1)
        log("Timed out waiting for backend after docker-compose up.")

    log("Unable to start backend automatically. Check logs or start the API manually.")
    return 2

if __name__ == '__main__':
    sys.exit(main())
