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
    if module == "Static Analysis":
        print("[ALD] Source module : Static Analysis")
        print()

        path = Path(input("Source path/file: ").strip()).expanduser()

        if not path.exists():
            print("[ALD] Path not found.")
            return

        files = [path] if path.is_file() else [
            f for f in path.rglob("*")
            if f.is_file()
            and ".git" not in f.parts
            and "__pycache__" not in f.parts
        ]

        print(f"[ALD] Files discovered: {len(files)}")
        print("-" * 54)

        for f in files[:100]:
            print(f"[+] {f}")

        tools = ["semgrep", "cppcheck", "shellcheck"]

        print()
        print("[ALD] Static-analysis backends")
        print("-" * 54)

        for name in tools:
            tool = _tool(name)
            print(f"[ALD] {name}: {tool or 'not found'}")

        return

    if module == "Secrets Detection":
        print("[ALD] Source module : Secrets Detection")
        print()

        path = Path(input("Source path/file: ").strip()).expanduser()

        if not path.exists():
            print("[ALD] Path not found.")
            return

        files = [path] if path.is_file() else [
            f for f in path.rglob("*")
            if f.is_file()
            and ".git" not in f.parts
            and "__pycache__" not in f.parts
        ]

        patterns = (
            "password",
            "passwd",
            "secret",
            "api_key",
            "apikey",
            "token",
            "private_key",
        )

        hits = 0

        for f in files[:500]:
            try:
                text = f.read_text(errors="replace")
            except Exception:
                continue

            for line_no, line in enumerate(text.splitlines(), 1):
                low = line.lower()
                if any(p in low for p in patterns):
                    print(f"[+] {f}:{line_no}: {line[:180]}")
                    hits += 1

        print()
        print(f"[ALD] Potential secret-related lines: {hits}")
        print("[ALD] Results are heuristic; manual verification is required.")
        return

    if module == "Evidence":
        report_dir = Path("ald/reports")
        report_dir.mkdir(parents=True, exist_ok=True)

        print("[ALD] Source module : Evidence")
        print(report_dir.resolve())
        return

    print(f"[ALD] Unknown source-code module: {module}")
