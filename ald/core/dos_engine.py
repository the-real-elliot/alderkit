#!/usr/bin/env python3

import shutil
import subprocess
from pathlib import Path
import time


def _tool(name):
    return shutil.which(name)


def run(module, target=None):
    if module == "Local Test":
        print("[ALD] DoS module : Local Test")
        print()
        print("[ALD] Safe lab check: bounded local loop only.")
        print("[ALD] No network traffic is generated.")

        duration = input("Duration seconds [3]: ").strip() or "3"

        try:
            duration = max(1, min(int(duration), 10))
        except ValueError:
            print("[ALD] Invalid duration.")
            return

        start = time.monotonic()
        iterations = 0

        while time.monotonic() - start < duration:
            _ = sum(range(5000))
            iterations += 1

        print(f"[ALD] Duration   : {duration}s")
        print(f"[ALD] Iterations : {iterations}")
        print("[ALD] Local resource test complete.")
        return

    if module == "Resource Monitoring":
        print("[ALD] DoS module : Resource Monitoring")
        print()

        commands = [
            ("CPU / process snapshot", ["ps", "-eo", "pid,comm,%cpu,%mem", "--sort=-%cpu"]),
            ("Memory", ["free", "-h"]),
            ("Load", ["uptime"]),
        ]

        for label, command in commands:
            if not _tool(command[0]):
                continue

            print(f"[ALD] {label}")
            print("-" * 54)

            try:
                result = subprocess.run(
                    command,
                    text=True,
                    capture_output=True,
                    timeout=10,
                )
                print("\n".join(result.stdout.splitlines()[:15]))
            except Exception as exc:
                print(f"[ALD] Monitor failed: {exc}")

            print()

        return

    if module == "Evidence":
        report_dir = Path("ald/reports")
        report_dir.mkdir(parents=True, exist_ok=True)

        print("[ALD] DoS module : Evidence")
        print(report_dir.resolve())
        return

    print(f"[ALD] Unknown DoS module: {module}")
