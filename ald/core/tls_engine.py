#!/usr/bin/env python3

import socket
import ssl
import shutil
import subprocess
from pathlib import Path


def _tool(name):
    return shutil.which(name)


def run(module, target=None):
    host = (target or "127.0.0.1").strip()
    port = 443

    if ":" in host and host.count(":") == 1:
        h, p = host.rsplit(":", 1)
        if p.isdigit():
            host, port = h, int(p)

    if module == "Certificate":
        print("[ALD] TLS module : Certificate")
        print()
        print(f"[ALD] Target: {host}:{port}")

        context = ssl.create_default_context()

        try:
            with socket.create_connection((host, port), timeout=5) as sock:
                with context.wrap_socket(sock, server_hostname=host) as tls:
                    cert = tls.getpeercert()
                    cipher = tls.cipher()
                    version = tls.version()

                    print("[ALD] TLS connection established")
                    print("-" * 54)
                    print(f"Protocol : {version}")
                    print(f"Cipher   : {cipher[0] if cipher else 'unknown'}")

                    subject = cert.get("subject", ())
                    issuer = cert.get("issuer", ())
                    san = cert.get("subjectAltName", ())

                    print(f"Subject  : {subject or 'unavailable'}")
                    print(f"Issuer   : {issuer or 'unavailable'}")
                    print(f"Expires  : {cert.get('notAfter', 'unavailable')}")
                    print(f"SAN      : {san or 'unavailable'}")

        except Exception as exc:
            print(f"[-] TLS connection failed: {exc}")

            openssl = _tool("openssl")
            if openssl:
                print()
                print("[ALD] OpenSSL backend available for manual certificate analysis.")
                print(f"[ALD] Backend: {openssl}")

        return

    if module == "TLS Configuration":
        print("[ALD] TLS module : TLS Configuration")
        print()

        openssl = _tool("openssl")
        if not openssl:
            print("[ALD] OpenSSL backend: not found")
            return

        print(f"[ALD] Backend: {openssl}")
        print(f"[ALD] Target : {host}:{port}")
        print()
        print("[ALD] TLS configuration probe")

        try:
            result = subprocess.run(
                [
                    openssl, "s_client",
                    "-connect", f"{host}:{port}",
                    "-servername", host,
                    "-brief",
                ],
                input="",
                text=True,
                capture_output=True,
                timeout=12,
            )

            output = (result.stdout + "\n" + result.stderr).strip()

            if output:
                print("\n".join(output.splitlines()[:80]))
            else:
                print("[ALD] No TLS response.")

        except Exception as exc:
            print(f"[ALD] OpenSSL probe failed: {exc}")

        return

    if module == "Evidence":
        report_dir = Path("ald/reports")
        report_dir.mkdir(parents=True, exist_ok=True)
        print("[ALD] TLS module : Evidence")
        print(report_dir.resolve())
        return

    print(f"[ALD] Unknown TLS module: {module}")
