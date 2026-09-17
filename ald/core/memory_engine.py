#!/usr/bin/env python3
import shutil
import subprocess
from pathlib import Path

def _tool(name):
    return shutil.which(name)

def run(module, target=None):
    if module == "Memory Image Analysis":
        print("[ALD] Memory module : Memory Image Analysis")
        print()
        path = Path(input("Memory image path: ").strip()).expanduser()
        if not path.is_file():
            print("[ALD] File not found.")
            return
        tool = _tool("file")
        if tool:
            r = subprocess.run([tool, str(path)], text=True, capture_output=True, timeout=10)
            print(r.stdout.strip())
        return

    if module == "Process Analysis":
        print("[ALD] Memory module : Process Analysis")
        print()
        print("[ALD] Live process inventory")
        print("-" * 54)
        tool = _tool("ps")
        if tool:
            r = subprocess.run([tool, "-eo", "pid,ppid,user,%cpu,%mem,comm,args"], text=True, capture_output=True, timeout=10)
            print("\n".join(r.stdout.splitlines()[:80]))
        else:
            print("[ALD] ps not found.")
        return

    if module == "Network Artifacts":
        print("[ALD] Memory module : Network Artifacts")
        print()
        tool = _tool("ss")
        if tool:
            r = subprocess.run([tool, "-tunap"], text=True, capture_output=True, timeout=10)
            print(r.stdout)
        else:
            print("[ALD] ss not found.")
        return

    if module == "Evidence":
        report_dir = Path("ald/reports")
        report_dir.mkdir(parents=True, exist_ok=True)
        print("[ALD] Memory module : Evidence")
        print(report_dir.resolve())
        return

    print(f"[ALD] Unknown memory module: {module}")
