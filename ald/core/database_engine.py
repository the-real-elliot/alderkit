#!/usr/bin/env python3

import shutil
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
    if module == "Discovery":
        print("[ALD] Database module : Discovery")
        print()
        print("[ALD] Local database backend inventory")
        print("-" * 54)

        tools = {
            "PostgreSQL": ("psql", "--version"),
            "MySQL": ("mysql", "--version"),
            "MariaDB": ("mariadb", "--version"),
            "SQLite": ("sqlite3", "--version"),
            "MongoDB": ("mongosh", "--version"),
            "Redis": ("redis-cli", "--version"),
        }

        found = 0

        for name, args in tools.items():
            tool = _tool(args[0])

            if not tool:
                print(f"[-] {name}: not found")
                continue

            found += 1
            result = _run([tool, args[1]])

            version = ""
            if result:
                version = (result.stdout or result.stderr).strip()

            print(f"[+] {name}: {tool}")
            if version:
                print(f"    {version}")

        print()
        print(f"[ALD] Database backends detected: {found}")
        return

    if module == "Configuration Analysis":
        print("[ALD] Database module : Configuration Analysis")
        print()

        candidates = [
            Path("/etc/postgresql"),
            Path("/etc/mysql"),
            Path("/etc/my.cnf"),
            Path("/etc/redis"),
        ]

        found = []

        for path in candidates:
            if path.exists():
                found.append(path)

        print("[ALD] Local configuration candidates")
        print("-" * 54)

        if not found:
            print("[ALD] No supported database configuration paths detected.")
        else:
            for path in found:
                print(f"[+] {path}")

        return

    if module == "Evidence":
        report_dir = Path("ald/reports")
        report_dir.mkdir(parents=True, exist_ok=True)

        print("[ALD] Database module : Evidence")
        print(report_dir.resolve())
        return

    print(f"[ALD] Unknown database module: {module}")
