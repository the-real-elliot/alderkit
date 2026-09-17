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
    if module == "Hardware Inventory":
        print("[ALD] RFID/NFC module : Hardware Inventory")
        print()

        print("[ALD] NFC / RFID related interfaces")
        print("-" * 54)

        tools = ("lsusb", "udevadm")

        found = False

        if _tool("lsusb"):
            result = _run(["lsusb"])
            if result:
                for line in result.stdout.splitlines():
                    low = line.lower()
                    if any(k in low for k in ("nfc", "rfid", "pn532", "acr", "reader")):
                        print(f"[+] {line}")
                        found = True

        if _tool("udevadm"):
            result = _run(
                [
                    "udevadm",
                    "info",
                    "--export-db",
                ],
                timeout=20,
            )
            if result:
                hits = [
                    line for line in result.stdout.splitlines()
                    if any(
                        k in line.lower()
                        for k in ("nfc", "rfid", "pn532", "acr", "reader")
                    )
                ]
                for line in hits[:40]:
                    print(f"[+] {line}")
                    found = True

        if not found:
            print("[ALD] No NFC/RFID hardware identified.")

        return

    if module == "Tag Analysis":
        print("[ALD] RFID/NFC module : Tag Analysis")
        print()
        print("[ALD] Passive tag-analysis interface.")
        print("[ALD] No tag write or cloning operation is performed.")
        return

    if module == "Evidence":
        report_dir = Path("ald/reports")
        report_dir.mkdir(parents=True, exist_ok=True)

        print("[ALD] RFID/NFC module : Evidence")
        print(report_dir.resolve())
        return

    print(f"[ALD] Unknown RFID/NFC module: {module}")
