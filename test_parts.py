#!/usr/bin/env python3
"""
Test runner for CODE_LAB.md Parts 4, 5, 6
Run from project root: python3 test_parts.py
"""
import os, sys, subprocess, time, requests, json, signal

BASE = os.path.dirname(os.path.abspath(__file__))
VENV_PYTHON = os.path.join(BASE, "venv", "bin", "python3")

def separator(title):
    print(f"\n{'='*55}")
    print(f"  {title}")
    print('='*55)

def start_server(app_dir, env_vars, port=8001):
    env = {**os.environ, **env_vars, "PORT": str(port)}
    # Ensure utils path is accessible
    env["PYTHONPATH"] = BASE
    proc = subprocess.Popen(
        [VENV_PYTHON, "app.py"],
        cwd=app_dir,
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    time.sleep(2)
    return proc

def stop_server(proc):
    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()


# ─────────────────────────────────────────────
# PART 4: API Security
# ─────────────────────────────────────────────
separator("PART 4: API Security — Exercise 4.1")

port = 8010
app_dir = os.path.join(BASE, "04-api-gateway", "develop")
proc = start_server(app_dir, {"AGENT_API_KEY": "secret-key-123"}, port)

try:
    base_url = f"http://localhost:{port}"

    # Test 1: No key
    r = requests.post(f"{base_url}/ask", params={"question": "Hello"})
    status = "✅ PASS" if r.status_code == 401 else f"❌ FAIL (got {r.status_code})"
    print(f"\n  Test 1 — No API key: {status}")
    print(f"  Response: {r.json()}")

    # Test 2: Wrong key
    r = requests.post(f"{base_url}/ask", params={"question": "Hello"},
                      headers={"X-API-Key": "wrong-key"})
    status = "✅ PASS" if r.status_code == 403 else f"❌ FAIL (got {r.status_code})"
    print(f"\n  Test 2 — Wrong API key: {status}")
    print(f"  Response: {r.json()}")

    # Test 3: Correct key
    r = requests.post(f"{base_url}/ask", params={"question": "Hello"},
                      headers={"X-API-Key": "secret-key-123"})
    status = "✅ PASS" if r.status_code == 200 else f"❌ FAIL (got {r.status_code})"
    print(f"\n  Test 3 — Correct API key: {status}")
    print(f"  Response: {r.json()}")

finally:
    stop_server(proc)
    print("\n  Server stopped.")

# ─────────────────────────────────────────────
# PART 4 Exercise 4.2: JWT Auth
# ─────────────────────────────────────────────
separator("PART 4: API Security — Exercise 4.2 (JWT)")

port = 8011
app_dir = os.path.join(BASE, "04-api-gateway", "production")
proc = start_server(app_dir, {"JWT_SECRET": "my-jwt-secret"}, port)

try:
    base_url = f"http://localhost:{port}"

    # Step 1: Get token
    r = requests.post(f"{base_url}/auth/token",
                      json={"username": "student", "password": "demo123"})
    if r.status_code == 200:
        token = r.json().get("access_token", "")
        print(f"\n  ✅ Got JWT token: {token[:30]}...")

        # Step 2: Use token
        r2 = requests.post(f"{base_url}/ask",
                           params={"question": "Explain JWT"},
                           headers={"Authorization": f"Bearer {token}"})
        status = "✅ PASS" if r2.status_code == 200 else f"❌ FAIL (got {r2.status_code})"
        print(f"  JWT auth test: {status}")
        print(f"  Response: {r2.json()}")
    else:
        print(f"  ❌ Failed to get token: {r.status_code} -> {r.text}")

finally:
    stop_server(proc)
    print("\n  Server stopped.")

# ─────────────────────────────────────────────
# PART 4 Exercise 4.3: Rate Limiting
# ─────────────────────────────────────────────
separator("PART 4: Rate Limiting — Exercise 4.3")

port = 8012
app_dir = os.path.join(BASE, "04-api-gateway", "production")
proc = start_server(app_dir, {"JWT_SECRET": "my-jwt-secret"}, port)

try:
    base_url = f"http://localhost:{port}"

    # Get token first
    r = requests.post(f"{base_url}/auth/token",
                      json={"username": "student", "password": "demo123"})
    token = r.json().get("access_token", "") if r.status_code == 200 else ""

    if token:
        hit_limit = False
        for i in range(15):
            r = requests.post(f"{base_url}/ask",
                              params={"question": f"Test {i+1}"},
                              headers={"Authorization": f"Bearer {token}"})
            if r.status_code == 429:
                print(f"\n  ✅ Rate limit hit at request #{i+1}: HTTP 429")
                print(f"  Detail: {r.json()}")
                hit_limit = True
                break
        if not hit_limit:
            print("  ❌ Rate limit was NOT triggered after 15 requests")
    else:
        print("  ❌ Could not get token for rate limit test")

finally:
    stop_server(proc)
    print("\n  Server stopped.")

# ─────────────────────────────────────────────
# PART 5: Scaling & Reliability
# ─────────────────────────────────────────────
separator("PART 5: Scaling & Reliability — Exercise 5.1 (Health Checks)")

port = 8013
app_dir = os.path.join(BASE, "05-scaling-reliability", "develop")
proc = start_server(app_dir, {}, port)

try:
    base_url = f"http://localhost:{port}"

    r = requests.get(f"{base_url}/health")
    status = "✅ PASS" if r.status_code == 200 else f"❌ FAIL ({r.status_code})"
    print(f"\n  /health check: {status}")
    print(f"  Response: {json.dumps(r.json(), indent=4)}")

    r = requests.get(f"{base_url}/ready")
    status = "✅ PASS" if r.status_code == 200 else f"❌ FAIL ({r.status_code})"
    print(f"\n  /ready check: {status}")
    print(f"  Response: {r.json()}")

finally:
    stop_server(proc)
    print("\n  Server stopped.")

# ─────────────────────────────────────────────
# PART 5: Exercise 5.2 — Graceful Shutdown
# ─────────────────────────────────────────────
separator("PART 5: Scaling & Reliability — Exercise 5.2 (Graceful Shutdown)")

port = 8014
app_dir = os.path.join(BASE, "05-scaling-reliability", "develop")
env = {**os.environ, "PORT": str(port), "PYTHONPATH": BASE}
proc = subprocess.Popen([VENV_PYTHON, "app.py"], cwd=app_dir, env=env,
                        stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
time.sleep(2)
print(f"\n  Server started (PID={proc.pid})")

# Send a request then SIGTERM
proc.send_signal(signal.SIGTERM)
try:
    log_output = proc.stdout.read(4096).decode(errors="ignore")
    print("  Server log during shutdown:")
    for line in log_output.splitlines():
        if line.strip():
            print(f"    {line}")
    proc.wait(timeout=10)
    print("  ✅ Server shut down gracefully (exit code:", proc.returncode, ")")
except subprocess.TimeoutExpired:
    proc.kill()
    print("  ❌ Server did not shut down in time (killed)")

# ─────────────────────────────────────────────
# PART 6: Final Project Validation
# ─────────────────────────────────────────────
separator("PART 6: Final Project — check_production_ready.py")

result = subprocess.run(
    [VENV_PYTHON, "check_production_ready.py"],
    cwd=os.path.join(BASE, "06-lab-complete"),
    capture_output=True, text=True
)
print(result.stdout)
if result.returncode == 0:
    print("  🎉 PRODUCTION READY — All checks passed!")
else:
    print("  ❌ Some checks failed. See above.")
    if result.stderr:
        print(result.stderr)
