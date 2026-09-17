#!/usr/bin/env python3

import shutil
import subprocess
from pathlib import Path

TOOLS = [
    "nmap", "masscan", "arp", "ip", "ss",
    "curl", "wget", "whatweb", "nikto",
    "file", "exiftool", "strings", "tshark", "yara",
    "adb", "docker", "podman",
    "afl-fuzz", "honggfuzz", "radamsa",
    "semgrep", "cppcheck", "shellcheck",
    "openssl", "dig", "bluetoothctl",
    "sqlite3", "psql",
]

def _version(tool):
    for args in ([tool, "--version"], [tool, "-V"], [tool, "-h"]):
        try:
            r = subprocess.run(
                args,
                text=True,
                capture_output=True,
                timeout=5,
            )
        except Exception:
            continue

        text = (r.stdout or r.stderr).strip()
        if text:
            return text.splitlines()[0][:180]

    return "version unavailable"


def run(module, target=None):
    if module == "Status":
        print("[ALD] Tool Inventory module : Status")
        print()
        print("[ALD] Executable inventory")
        print("-" * 54)

        available = 0

        for name in TOOLS:
            path = shutil.which(name)

            if path:
                available += 1
                print(f"[+] {name}")
                print(f"    Path    : {path}")
                print(f"    Version : {_version(path)}")
            else:
                print(f"[-] {name}: not found")

        print()
        print(f"[ALD] Available: {available}/{len(TOOLS)}")
        return

    if module == "Refresh":
        print("[ALD] Tool Inventory module : Refresh")
        print()
        print("[ALD] PATH-based inventory refreshed.")
        print("[ALD] No packages were installed or modified.")
        return

    if module == "Verify":
        print("[ALD] Tool Inventory module : Verify")
        print()
        print("[ALD] Verifying detected tools")
        print("-" * 54)

        failures = 0
        checked = 0

        for name in TOOLS:
            path = shutil.which(name)

            if not path:
                continue

            checked += 1

            try:
                result = subprocess.run(
                    [path, "--version"],
                    text=True,
                    capture_output=True,
                    timeout=5,
                )

                output = (result.stdout or result.stderr).strip()

                if result.returncode == 0 or output:
                    version = output.splitlines()[0] if output else "version unavailable"
                    print(f"[+] {name}: OK — {version[:160]}")
                else:
                    failures += 1
                    print(f"[!] {name}: verification failed")

            except Exception as exc:
                failures += 1
                print(f"[!] {name}: {exc}")

        print()
        print(f"[ALD] Verified : {checked}")
        print(f"[ALD] Failures : {failures}")
        return

    if module == "Evidence":
        report_dir = Path("ald/reports")
        report_dir.mkdir(parents=True, exist_ok=True)

        output = report_dir / "tool_inventory.txt"
        lines = ["ALD // TOOL INVENTORY", ""]

        for name in TOOLS:
            path = shutil.which(name)
            if path:
                lines.append(f"{name}: {path} | {_version(path)}")
            else:
                lines.append(f"{name}: NOT FOUND")

        output.write_text("\n".join(lines))

        print("[ALD] Tool Inventory module : Evidence")
        print(f"[+] Evidence saved: {output}")
        return

    print(f"[ALD] Unknown inventory module: {module}")
