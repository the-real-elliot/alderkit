#!/usr/bin/env python3

import shutil
import subprocess
from pathlib import Path

def _tool(name):
    return shutil.which(name)

def _run(cmd, timeout=10):
    try:
        return subprocess.run(cmd, text=True, capture_output=True, timeout=timeout)
    except Exception as exc:
        print(f"[ALD] Command failed: {exc}")
        return None

def run(module, target=None):
    if module == "Radio Inventory":
        print("[ALD] SDR module : Radio Inventory")
        print()

        tools = ["rtl_test", "hackrf_info", "SoapySDRUtil", "uhd_find_devices"]
        found = False

        for name in tools:
            tool = _tool(name)
            print(f"[ALD] {name}: {tool or 'not found'}")
            if tool:
                found = True

        if not found:
            print()
            print("[ALD] No supported SDR backend detected.")

        return

    if module == "Device Detection":
        print("[ALD] SDR module : Device Detection")
        print()

        checks = [
            ("USB devices", ["lsusb"]),
            ("PCI devices", ["lspci"]),
        ]

        for label, cmd in checks:
            if not _tool(cmd[0]):
                continue

            print(f"[ALD] {label}")
            print("-" * 54)

            result = _run(cmd)
            if result:
                lines = [
                    line for line in result.stdout.splitlines()
                    if any(k in line.lower() for k in ("rtl", "hackrf", "sdr", "radio", "airspy", "bladerf"))
                ]
                print("\n".join(lines) if lines else "[ALD] No obvious SDR hardware found.")
            print()

        return

    if module == "Evidence":
        report_dir = Path("ald/reports")
        report_dir.mkdir(parents=True, exist_ok=True)
        print("[ALD] SDR module : Evidence")
        print(report_dir.resolve())
        return

    print(f"[ALD] Unknown SDR module: {module}")
