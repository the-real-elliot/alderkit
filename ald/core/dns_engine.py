#!/usr/bin/env python3

import shutil
import socket
import subprocess
from pathlib import Path


def _tool(name):
    return shutil.which(name)


def _run(cmd, timeout=10):
    try:
        return subprocess.run(
            cmd,
            text=True,
            capture_output=True,
            timeout=timeout,
        )
    except Exception as exc:
        print(f"[ALD] Command failed: {exc}")
        return None


def run(module, target=None):
    host = (target or "127.0.0.1").strip()

    if module == "DNS Discovery":
        print("[ALD] DNS module : DNS Discovery")
        print()

        print(f"[ALD] Target : {host}")
        print("[ALD] Resolver configuration")
        print("-" * 54)

        resolv = Path("/etc/resolv.conf")
        if resolv.exists():
            for line in resolv.read_text(errors="replace").splitlines():
                line = line.strip()
                if line and not line.startswith("#"):
                    print(f"[+] {line}")
        else:
            print("[ALD] /etc/resolv.conf not found.")

        print()
        print("[ALD] DNS resolution test")
        print("-" * 54)

        try:
            name, aliases, addresses = socket.gethostbyname_ex(host)
            print(f"[+] Name     : {name}")
            print(f"[+] Aliases  : {aliases or 'none'}")
            print(f"[+] Addresses: {addresses}")
        except socket.gaierror as exc:
            print(f"[-] Resolution failed: {exc}")

        return

    if module == "Record Analysis":
        print("[ALD] DNS module : Record Analysis")
        print()

        dig = _tool("dig")
        if not dig:
            print("[ALD] Backend: dig not found")
            print("[ALD] Install dnsutils/bind utilities for record inspection.")
            return

        records = ["A", "AAAA", "CNAME", "MX", "NS", "TXT"]

        for record in records:
            print(f"[ALD] {record}")
            print("-" * 54)

            result = _run(
                [
                    dig,
                    "+short",
                    host,
                    record,
                ]
            )

            if result and result.stdout.strip():
                print(result.stdout.strip())
            else:
                print("[ALD] No response.")

            print()

        return

    if module == "Evidence":
        report_dir = Path("ald/reports")
        report_dir.mkdir(parents=True, exist_ok=True)

        print("[ALD] DNS module : Evidence")
        print(report_dir.resolve())
        return

    print(f"[ALD] Unknown DNS module: {module}")
