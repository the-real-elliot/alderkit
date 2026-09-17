#!/usr/bin/env python3

import shutil
import subprocess
from pathlib import Path


def _tool(name):
    return shutil.which(name)


def _run(cmd, timeout=30):
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
    if module == "YARA":
        print("[ALD] YARA module : YARA")
        print()

        yara = _tool("yara")

        if not yara:
            print("[ALD] Backend: yara not found")
            print("[ALD] Install YARA to enable rule matching.")
            return

        rule = Path(input("YARA rule file: ").strip()).expanduser()
        target_path = Path(input("Target file/directory: ").strip()).expanduser()

        if not rule.is_file():
            print("[ALD] Rule file not found.")
            return

        if not target_path.exists():
            print("[ALD] Target not found.")
            return

        print(f"[ALD] Backend: {yara}")
        print(f"[ALD] Rule   : {rule}")
        print(f"[ALD] Target : {target_path}")
        print("-" * 54)

        result = _run(
            [yara, "-r", str(rule), str(target_path)],
            timeout=60,
        )

        if not result:
            return

        output = result.stdout.strip()

        if output:
            print(output)
        else:
            print("[ALD] No rule matches.")

        if result.stderr.strip():
            print(result.stderr.strip())

        return

    if module == "IOC Matching":
        print("[ALD] YARA module : IOC Matching")
        print()
        print("[ALD] Local IOC/YARA matching interface.")
        print("[ALD] No external reputation lookup is performed.")
        return

    if module == "Evidence":
        report_dir = Path("ald/reports")
        report_dir.mkdir(parents=True, exist_ok=True)

        print("[ALD] YARA module : Evidence")
        print(report_dir.resolve())
        return

    print(f"[ALD] Unknown YARA module: {module}")
