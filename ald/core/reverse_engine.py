#!/usr/bin/env python3

import shutil
import subprocess
from pathlib import Path


def _tool(name):
    return shutil.which(name)


def run(module, target=None):
    if module == "Static Analysis":
        print("[ALD] Reverse module : Static Analysis")
        print()
        path = Path(input("Binary/file path: ").strip()).expanduser()

        if not path.is_file():
            print("[ALD] File not found.")
            return

        tool = _tool("file")

        if not tool:
            print("[ALD] Missing backend: file")
            return

        result = subprocess.run(
            [tool, str(path)],
            text=True,
            capture_output=True,
            timeout=10,
        )

        print(result.stdout.strip())
        return

    if module == "Dynamic Analysis":
        print("[ALD] Reverse module : Dynamic Analysis")
        print()
        tool = _tool("gdb")
        print(f"[ALD] GDB backend: {tool or 'not found'}")
        return

    if module == "Disassembly":
        print("[ALD] Reverse module : Disassembly")
        print()

        path = Path(input("Binary path: ").strip()).expanduser()

        if not path.is_file():
            print("[ALD] File not found.")
            return

        tool = _tool("objdump")

        if not tool:
            print("[ALD] Missing backend: objdump")
            return

        result = subprocess.run(
            [tool, "-d", str(path)],
            text=True,
            capture_output=True,
            timeout=30,
        )

        print("\n".join(result.stdout.splitlines()[:80]))

        if len(result.stdout.splitlines()) > 80:
            print("[ALD] Output limited to first 80 lines.")

        return

    if module == "Debugging":
        print("[ALD] Reverse module : Debugging")
        print()
        tool = _tool("gdb")
        print(f"[ALD] GDB backend: {tool or 'not found'}")
        return

    if module == "Strings / Metadata":
        print("[ALD] Reverse module : Strings / Metadata")
        print()

        path = Path(input("File path: ").strip()).expanduser()

        if not path.is_file():
            print("[ALD] File not found.")
            return

        strings = _tool("strings")
        readelf = _tool("readelf")

        if strings:
            result = subprocess.run(
                [strings, str(path)],
                text=True,
                capture_output=True,
                timeout=10,
            )
            print("[ALD] Strings")
            print("-" * 54)
            print("\n".join(result.stdout.splitlines()[:60]))

        if readelf:
            result = subprocess.run(
                [readelf, "-h", str(path)],
                text=True,
                capture_output=True,
                timeout=10,
            )
            print()
            print("[ALD] ELF Header")
            print("-" * 54)
            print(result.stdout)

        return

    if module == "Evidence":
        report_dir = Path("ald/reports")
        report_dir.mkdir(parents=True, exist_ok=True)

        print("[ALD] Reverse module : Evidence")
        print()
        print(report_dir.resolve())
        return

    print(f"[ALD] Unknown reverse module: {module}")
