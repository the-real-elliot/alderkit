#!/usr/bin/env python3
import shutil
import subprocess
from pathlib import Path

def _tool(name):
    return shutil.which(name)

def run(module, target=None):
    if module == "Input Analysis":
        print("[ALD] Vulnerability Research module : Input Analysis")
        print()
        value = input("Test input: ")
        print(f"[ALD] Length : {len(value)}")
        print(f"[ALD] Bytes  : {len(value.encode())}")
        print(f"[ALD] NUL    : {chr(0) in value}")
        print(f"[ALD] Newline: {'\\n' in value or '\\r' in value}")
        return

    if module == "Crash Analysis":
        print("[ALD] Vulnerability Research module : Crash Analysis")
        print()
        path = Path(input("Crash/log file: ").strip()).expanduser()
        if not path.is_file():
            print("[ALD] File not found.")
            return
        text = path.read_text(errors="replace")
        lines = text.splitlines()
        keywords = ("segfault", "sigsegv", "signal", "asan", "ubsan", "assert", "panic", "abort", "crash")
        hits = [line for line in lines if any(k in line.lower() for k in keywords)]
        print(f"[ALD] Lines: {len(lines)}")
        print(f"[ALD] Crash indicators: {len(hits)}")
        for line in hits[:50]:
            print(f"[+] {line}")
        return

    if module == "PoC Management":
        print("[ALD] Vulnerability Research module : PoC Management")
        print()
        print("[ALD] Passive PoC inventory only.")
        print(f"[ALD] Repository: {Path('ald/reports').resolve()}")
        return

    if module == "Evidence":
        report_dir = Path("ald/reports")
        report_dir.mkdir(parents=True, exist_ok=True)
        print("[ALD] Vulnerability Research module : Evidence")
        print(report_dir.resolve())
        return

    print(f"[ALD] Unknown vulnerability-research module: {module}")
