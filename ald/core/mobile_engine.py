#!/usr/bin/env python3

import shutil
import subprocess
from pathlib import Path


def _tool(name):
    return shutil.which(name)


def run(module, target=None):
    if module == "ADB":
        print("[ALD] Mobile module : ADB")
        print()

        adb = _tool("adb")

        if not adb:
            print("[ALD] ADB backend: not found")
            return

        print(f"[ALD] Backend: {adb}")

        try:
            result = subprocess.run(
                [adb, "devices", "-l"],
                text=True,
                capture_output=True,
                timeout=10,
            )

            print("[ALD] Connected devices")
            print("-" * 54)
            print(result.stdout.strip() or "[ALD] No Android devices detected.")

            if result.stderr:
                print(result.stderr.strip())

        except subprocess.TimeoutExpired:
            print("[ALD] ADB query timed out.")

        return

    if module == "APK Analysis":
        print("[ALD] Mobile module : APK Analysis")
        print()

        apk = Path(input("APK path: ").strip()).expanduser()

        if not apk.is_file():
            print("[ALD] APK not found.")
            return

        print(f"[ALD] APK: {apk}")
        print(f"[ALD] Size: {apk.stat().st_size} bytes")

        for tool_name in ("aapt", "apkanalyzer", "jadx"):
            tool = _tool(tool_name)
            if tool:
                print(f"[+] {tool_name}: {tool}")

        file_tool = _tool("file")
        if file_tool:
            result = subprocess.run(
                [file_tool, str(apk)],
                text=True,
                capture_output=True,
                timeout=10,
            )
            print(result.stdout.strip())

        return

    if module == "Dynamic Analysis":
        print("[ALD] Mobile module : Dynamic Analysis")
        print()

        adb = _tool("adb")

        if not adb:
            print("[ALD] ADB backend: not found")
            return

        result = subprocess.run(
            [adb, "devices"],
            text=True,
            capture_output=True,
            timeout=10,
        )

        print(result.stdout.strip() or "[ALD] No Android devices detected.")
        return

    if module == "Evidence":
        report_dir = Path("ald/reports")
        report_dir.mkdir(parents=True, exist_ok=True)

        print("[ALD] Mobile module : Evidence")
        print(report_dir.resolve())
        return

    print(f"[ALD] Unknown mobile module: {module}")
