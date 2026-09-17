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
        print("[ALD] Bluetooth module : Discovery")
        print()

        btctl = _tool("bluetoothctl")
        hciconfig = _tool("hciconfig")

        if not btctl and not hciconfig:
            print("[ALD] Bluetooth backend: not found")
            print("[ALD] Install BlueZ utilities.")
            return

        if btctl:
            print(f"[ALD] Backend: {btctl}")
            print()
            print("[ALD] Controller inventory")
            print("-" * 54)
            result = _run([btctl, "list"])
            if result:
                print(result.stdout.strip() or "[ALD] No Bluetooth controllers detected.")

            print()
            print("[ALD] Adapter status")
            print("-" * 54)
            result = _run([btctl, "show"])
            if result:
                print(result.stdout.strip() or "[ALD] No adapter information returned.")

            return

        print(f"[ALD] Backend: {hciconfig}")
        result = _run([hciconfig, "-a"])
        if result:
            print(result.stdout.strip() or "[ALD] No Bluetooth controllers detected.")
        return

    if module == "Device Information":
        print("[ALD] Bluetooth module : Device Information")
        print()

        btctl = _tool("bluetoothctl")
        if not btctl:
            print("[ALD] bluetoothctl backend: not found")
            return

        result = _run([btctl, "show"])
        if result:
            print(result.stdout.strip() or "[ALD] No Bluetooth adapter information.")
        return

    if module == "Evidence":
        report_dir = Path("ald/reports")
        report_dir.mkdir(parents=True, exist_ok=True)

        print("[ALD] Bluetooth module : Evidence")
        print(report_dir.resolve())
        return

    print(f"[ALD] Unknown Bluetooth module: {module}")
