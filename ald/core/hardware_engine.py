#!/usr/bin/env python3

import shutil
import subprocess
from pathlib import Path

def _tool(name):
    return shutil.which(name)

def _run(cmd, timeout=15):
    try:
        return subprocess.run(cmd, text=True, capture_output=True, timeout=timeout)
    except Exception as exc:
        print(f"[ALD] Command failed: {exc}")
        return None

def run(module, target=None):
    if module == "USB Inventory":
        print("[ALD] Hardware module : USB Inventory")
        print()

        tool = _tool("lsusb")
        if not tool:
            print("[ALD] Backend: lsusb not found")
            return

        result = _run([tool])
        print("[ALD] USB devices")
        print("-" * 54)

        if result and result.stdout.strip():
            print(result.stdout.strip())
        else:
            print("[ALD] No USB devices detected.")

        return

    if module == "Device Analysis":
        print("[ALD] Hardware module : Device Analysis")
        print()

        if _tool("lspci"):
            result = _run(["lspci"])
            print("[ALD] PCI devices")
            print("-" * 54)
            if result:
                print(result.stdout.strip() or "[ALD] No PCI devices detected.")

        print()
        if _tool("lsusb"):
            result = _run(["lsusb"])
            print("[ALD] USB devices")
            print("-" * 54)
            if result:
                print(result.stdout.strip() or "[ALD] No USB devices detected.")

        return

    if module == "Evidence":
        report_dir = Path("ald/reports")
        report_dir.mkdir(parents=True, exist_ok=True)
        print("[ALD] Hardware module : Evidence")
        print(report_dir.resolve())
        return

    print(f"[ALD] Unknown hardware module: {module}")
