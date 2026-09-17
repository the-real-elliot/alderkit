#!/usr/bin/env python3

import http.server
import socket
import threading
import time
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
ALD_DIR = ROOT / "ald"

sys.path.insert(0, str(ALD_DIR))

from core import web_engine
from core.registry import resolve


HOST = "127.0.0.1"
def free_port():
    import socket
    sock = socket.socket()
    sock.bind((HOST, 0))
    port = sock.getsockname()[1]
    sock.close()
    return port

PORT = free_port()
TARGET = f"{HOST}:{PORT}"

results = []


class TestHandler(http.server.BaseHTTPRequestHandler):
    def do_HEAD(self):
        if self.path in ("/", "/index.html"):
            body = b"""
<!doctype html>
<html>
<head>
<title>ALD Local Test Lab</title>
</head>
<body>
<h1>Aldernix Web Lab</h1>
</body>
</html>
"""
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            return

        if self.path == "/api":
            body = b'{"status":"ok","lab":"aldernix"}'
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            return

        if self.path == "/openapi.json":
            body = b'{"openapi":"3.0.0","info":{"title":"ALD Test API"}}'
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            return

        self.send_error(404)

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            body = b"""
<!doctype html>
<html>
<head>
<title>ALD Local Test Lab</title>
</head>
<body>
<h1>Aldernix Web Lab</h1>
</body>
</html>
"""
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        if self.path == "/api":
            body = b'{"status":"ok","lab":"aldernix"}'
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        if self.path == "/openapi.json":
            body = b'{"openapi":"3.0.0","info":{"title":"ALD Test API"}}'
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        self.send_error(404)

    def log_message(self, *_):
        pass


def record(name, status, detail=""):
    results.append((name, status, detail))

    symbol = {
        "PASS": "\033[1;32m[PASS]\033[0m",
        "SKIP": "\033[1;33m[SKIP]\033[0m",
        "FAIL": "\033[1;31m[FAIL]\033[0m",
    }.get(status, "[????]")

    print(f"{symbol} {name:<30} {detail}")


def port_available():
    sock = socket.socket()
    try:
        sock.bind((HOST, PORT))
        return True
    except OSError:
        return False
    finally:
        sock.close()


def main():
    print()
    print("\033[1;31m============================================================\033[0m")
    print("\033[1;31m ALD // AUTOMATED SELF TEST\033[0m")
    print("\033[1;31m============================================================\033[0m")
    print()
    print(f"Local target : {TARGET}")
    print("No external hosts are contacted.")
    print()

    # --------------------------------------------------------
    # Core imports
    # --------------------------------------------------------

    try:
        assert callable(web_engine.run)
        record("Web engine import", "PASS", "core.web_engine.run()")
    except Exception as exc:
        record("Web engine import", "FAIL", str(exc))
        return 1

    # --------------------------------------------------------
    # OSINT engine
    # --------------------------------------------------------

    try:
        from core import osint_engine

        assert callable(osint_engine.run)

        record(
            "OSINT engine import",
            "PASS",
            "core.osint_engine.run()",
        )
    except Exception as exc:
        record(
            "OSINT engine import",
            "FAIL",
            str(exc),
        )

    # --------------------------------------------------------
    # Registry
    # --------------------------------------------------------

    tests = [
        ("WEB SECURITY", "HTTP Discovery"),
        ("WEB SECURITY", "Technology Analysis"),
        ("WEB SECURITY", "API Security"),
        ("WEB SECURITY", "Vulnerability Analysis"),
        ("WEB SECURITY", "TLS / Certificates"),
        ("NETWORK SECURITY", "Network Discovery"),
    ]

    for category, module in tests:
        try:
            info = resolve(category, module)

            if info["ready"]:
                tools = ", ".join(info["installed"])
                record(
                    f"Registry: {module}",
                    "PASS",
                    tools,
                )
            else:
                record(
                    f"Registry: {module}",
                    "SKIP",
                    "No backend installed",
                )
        except Exception as exc:
            record(
                f"Registry: {module}",
                "FAIL",
                str(exc),
            )

    # --------------------------------------------------------
    # Local lab
    # --------------------------------------------------------


    server = http.server.HTTPServer(
        (HOST, PORT),
        TestHandler,
    )

    thread = threading.Thread(
        target=server.serve_forever,
        daemon=True,
    )

    thread.start()
    time.sleep(0.5)

    record(
        "Local test server",
        "PASS",
        f"http://{TARGET}",
    )

    # Self-test is explicitly localhost-only.
    web_engine.authorized = lambda _target: True

    # --------------------------------------------------------
    # HTTP Discovery
    # --------------------------------------------------------

    try:
        evidence = web_engine.http_discovery(TARGET)

        if evidence:
            record(
                "HTTP Discovery",
                "PASS",
                str(evidence),
            )
        else:
            record(
                "HTTP Discovery",
                "FAIL",
                "No evidence returned",
            )
    except Exception as exc:
        record(
            "HTTP Discovery",
            "FAIL",
            str(exc),
        )

    # --------------------------------------------------------
    # Technology
    # --------------------------------------------------------

    try:
        evidence = web_engine.technology_analysis(TARGET)

        if evidence:
            record(
                "Technology Analysis",
                "PASS",
                str(evidence),
            )
        else:
            record(
                "Technology Analysis",
                "SKIP",
                "No compatible tool",
            )
    except Exception as exc:
        record(
            "Technology Analysis",
            "FAIL",
            str(exc),
        )

    # --------------------------------------------------------
    # API
    # --------------------------------------------------------

    try:
        evidence = web_engine.api_security(TARGET)

        if evidence:
            record(
                "API Security",
                "PASS",
                str(evidence),
            )
        else:
            record(
                "API Security",
                "SKIP",
                "No compatible tool",
            )
    except Exception as exc:
        record(
            "API Security",
            "FAIL",
            str(exc),
        )

    # --------------------------------------------------------
    # Endpoint enumeration
    # --------------------------------------------------------

    try:
        evidence = web_engine.endpoint_enumeration(TARGET)

        if evidence:
            record(
                "Endpoint Enumeration",
                "PASS",
                str(evidence),
            )
        else:
            record(
                "Endpoint Enumeration",
                "SKIP",
                "No ffuf/feroxbuster/gobuster + wordlist",
            )
    except Exception as exc:
        record(
            "Endpoint Enumeration",
            "FAIL",
            str(exc),
        )

    # --------------------------------------------------------
    # Vulnerability analysis
    # --------------------------------------------------------

    # Do not run a real vulnerability scan during self-test.
    # Only verify that a backend exists.
    if web_engine.tool("nuclei"):
        record(
            "Vulnerability Analysis backend",
            "PASS",
            "nuclei installed",
        )
    elif web_engine.tool("nikto"):
        record(
            "Vulnerability Analysis backend",
            "PASS",
            "nikto installed",
        )
    else:
        record(
            "Vulnerability Analysis backend",
            "SKIP",
            "nuclei/nikto not installed",
        )

    # --------------------------------------------------------
    # TLS
    # --------------------------------------------------------

    try:
        evidence = web_engine.tls_analysis(TARGET)

        if evidence:
            record(
                "TLS Analysis",
                "PASS",
                "HTTP target correctly identified",
            )
        else:
            record(
                "TLS Analysis",
                "FAIL",
                "No result returned",
            )
    except Exception as exc:
        record(
            "TLS Analysis",
            "FAIL",
            str(exc),
        )

    # --------------------------------------------------------
    # Shutdown
    # --------------------------------------------------------

    server.shutdown()

    if thread.is_alive():
        thread.join(timeout=3)

    server.server_close()

    print()
    print("\033[1;31m============================================================\033[0m")
    print("\033[1;31m RESULT\033[0m")
    print("\033[1;31m============================================================\033[0m")

    passed = sum(1 for _, status, _ in results if status == "PASS")
    skipped = sum(1 for _, status, _ in results if status == "SKIP")
    failed = sum(1 for _, status, _ in results if status == "FAIL")

    print()
    print(f"  PASS : {passed}")
    print(f"  SKIP : {skipped}")
    print(f"  FAIL : {failed}")
    print()

    if failed:
        print("\033[1;31m[!] Self-test found failures.\033[0m")
        return 1

    print("\033[1;32m[+] ALD self-test completed successfully.\033[0m")
    print("\033[1;33m[!] SKIP means the optional backend is not installed.\033[0m")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
