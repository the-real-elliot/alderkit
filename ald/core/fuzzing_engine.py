#!/usr/bin/env python3

import shutil
import subprocess
from pathlib import Path

def _tool(name):
    return shutil.which(name)

def run(module, target=None):
    if module == "AFL++":
        print("[ALD] Fuzzing module : AFL++")
        print()
        tool = _tool("afl-fuzz")
        print(f"[ALD] Backend: {tool or 'not found'}")
        return

    if module == "Honggfuzz":
        print("[ALD] Fuzzing module : Honggfuzz")
        print()
        tool = _tool("honggfuzz")
        print(f"[ALD] Backend: {tool or 'not found'}")
        return

    if module == "Radamsa":
        print("[ALD] Fuzzing module : Radamsa")
        print()
        tool = _tool("radamsa")
        print(f"[ALD] Backend: {tool or 'not found'}")
        return

    if module == "Evidence":
        report_dir = Path("ald/reports")
        report_dir.mkdir(parents=True, exist_ok=True)
        print("[ALD] Fuzzing module : Evidence")
        print(report_dir.resolve())
        return

    print(f"[ALD] Unknown fuzzing module: {module}")
