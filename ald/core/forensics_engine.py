#!/usr/bin/env python3

import shutil
import subprocess
from pathlib import Path


def _tool(name):
    return shutil.which(name)


def run(module, target=None):
    if module == "File Analysis":
        print("[ALD] Forensics module : File Analysis")
        print()
        path = Path(input("File path: ").strip()).expanduser()
        if not path.is_file():
            print("[ALD] File not found.")
            return
        tool = _tool("file")
        if tool:
            result = subprocess.run([tool, str(path)], text=True, capture_output=True, timeout=10)
            print(result.stdout.strip())
        return

    if module == "Disk Analysis":
        print("[ALD] Forensics module : Disk Analysis")
        print()
        print(f"[ALD] Backend: {_tool('lsblk') or 'lsblk not found'}")
        tool = _tool("lsblk")
        if tool:
            result = subprocess.run([tool, "-o", "NAME,SIZE,TYPE,FSTYPE,MOUNTPOINTS"], text=True, capture_output=True, timeout=10)
            print(result.stdout)
        return

    if module == "Memory Analysis":
        print("[ALD] Forensics module : Memory Analysis")
        print()
        print(f"[ALD] Volatility: {_tool('vol') or _tool('volatility') or 'not found'}")
        return

    if module == "Timeline Analysis":
        print("[ALD] Forensics module : Timeline Analysis")
        print()
        path = Path(input("File/directory path: ").strip()).expanduser()
        if not path.exists():
            print("[ALD] Path not found.")
            return
        print(f"[ALD] Type: {'directory' if path.is_dir() else 'file'}")
        print(f"[ALD] Size: {path.stat().st_size if path.is_file() else 'N/A'}")
        print(f"[ALD] Modified: {path.stat().st_mtime}")
        return

    if module == "Metadata":
        print("[ALD] Forensics module : Metadata")
        print()
        path = Path(input("File path: ").strip()).expanduser()
        if not path.is_file():
            print("[ALD] File not found.")
            return
        tool = _tool("exiftool")
        if not tool:
            print("[ALD] Missing backend: exiftool")
            return
        result = subprocess.run([tool, str(path)], text=True, capture_output=True, timeout=20)
        print(result.stdout)
        return

    if module == "Evidence":
        report_dir = Path("ald/reports")
        report_dir.mkdir(parents=True, exist_ok=True)
        print("[ALD] Forensics module : Evidence")
        print(report_dir.resolve())
        return

    print(f"[ALD] Unknown forensics module: {module}")
