#!/usr/bin/env python3

import shutil
import subprocess
from pathlib import Path


def _tool(name):
    return shutil.which(name)


def _run(cmd, timeout=20):
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
    if module == "Image Analysis":
        print("[ALD] Steganography module : Image Analysis")
        print()

        path = Path(input("Image/file path: ").strip()).expanduser()

        if not path.is_file():
            print("[ALD] File not found.")
            return

        print(f"[ALD] File : {path}")
        print(f"[ALD] Size : {path.stat().st_size} bytes")

        file_tool = _tool("file")
        if file_tool:
            result = _run([file_tool, str(path)])
            if result:
                print(f"[ALD] Type : {result.stdout.strip()}")

        tools = [
            ("exiftool", [str(path)]),
            ("strings", [str(path)]),
            ("binwalk", ["--quiet", str(path)]),
        ]

        found = False

        for name, args in tools:
            tool = _tool(name)
            if not tool:
                continue

            found = True
            print()
            print(f"[ALD] {name}")
            print("-" * 54)

            result = _run([tool] + args)
            if result:
                output = (result.stdout or result.stderr).strip()
                if output:
                    print("\n".join(output.splitlines()[:80]))
                else:
                    print("[ALD] No output.")

        if not found:
            print()
            print("[ALD] No steganography-analysis backend detected.")
            print("[ALD] Basic file/type analysis is still available.")

        return

    if module == "File Analysis":
        print("[ALD] Steganography module : File Analysis")
        print()

        path = Path(input("File path: ").strip()).expanduser()

        if not path.is_file():
            print("[ALD] File not found.")
            return

        strings = _tool("strings")
        if strings:
            result = _run([strings, str(path)])
            if result:
                print("\n".join(result.stdout.splitlines()[:100]))
        else:
            print("[ALD] strings backend not found.")

        return

    if module == "Evidence":
        report_dir = Path("ald/reports")
        report_dir.mkdir(parents=True, exist_ok=True)

        print("[ALD] Steganography module : Evidence")
        print(report_dir.resolve())
        return

    print(f"[ALD] Unknown steganography module: {module}")
