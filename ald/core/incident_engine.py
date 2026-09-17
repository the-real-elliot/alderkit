#!/usr/bin/env python3

import shutil
import subprocess
from pathlib import Path


def _tool(name):
    return shutil.which(name)


def _run(cmd, timeout=15):
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
    if module == "Triage":
        print("[ALD] Incident Response module : Triage")
        print()

        print("[ALD] Host triage")
        print("-" * 54)

        checks = [
            ("Hostname", ["hostname"]),
            ("Uptime", ["uptime"]),
            ("Kernel", ["uname", "-a"]),
            ("Memory", ["free", "-h"]),
            ("Disk", ["df", "-h"]),
        ]

        for label, command in checks:
            if not _tool(command[0]):
                continue

            result = _run(command)
            if result:
                value = (result.stdout or "").strip()
                print(f"[+] {label}:")
                print(value[:4000])
                print()

        return

    if module == "Evidence":
        report_dir = Path("ald/reports")
        report_dir.mkdir(parents=True, exist_ok=True)

        print("[ALD] Incident Response module : Evidence")
        print(report_dir.resolve())
        return

    if module == "Timeline":
        print("[ALD] Incident Response module : Timeline")
        print()

        path = Path(input("File/directory path: ").strip()).expanduser()

        if not path.exists():
            print("[ALD] Path not found.")
            return

        if path.is_file():
            stat = path.stat()
            print(f"[ALD] File      : {path}")
            print(f"[ALD] Size      : {stat.st_size}")
            print(f"[ALD] Modified  : {stat.st_mtime}")
            print(f"[ALD] Accessed  : {stat.st_atime}")
            print(f"[ALD] Changed   : {stat.st_ctime}")
            return

        files = []
        for item in path.rglob("*"):
            if item.is_file():
                try:
                    files.append((item.stat().st_mtime, item))
                except OSError:
                    pass

        files.sort(reverse=True)

        print(f"[ALD] Files discovered: {len(files)}")
        print("-" * 54)

        for mtime, item in files[:100]:
            print(f"{mtime:.0f}  {item}")

        return

    if module == "Artifact Collection":
        print("[ALD] Incident Response module : Artifact Collection")
        print()
        print("[ALD] Safe local artifact inventory")
        print("-" * 54)

        candidates = [
            Path("/var/log"),
            Path("/tmp"),
            Path("/etc"),
        ]

        for path in candidates:
            print(f"[+] {path}: {'present' if path.exists() else 'missing'}")

        return

    print(f"[ALD] Unknown incident-response module: {module}")
