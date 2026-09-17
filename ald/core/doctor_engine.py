#!/usr/bin/env python3

import shutil
import subprocess
from pathlib import Path


TOOLS = [
    "python",
    "nmap",
    "curl",
    "wget",
    "tshark",
    "yara",
    "adb",
    "docker",
    "afl-fuzz",
    "honggfuzz",
    "radamsa",
    "semgrep",
    "cppcheck",
    "shellcheck",
    "openssl",
    "dig",
    "bluetoothctl",
    "sqlite3",
    "psql",
]


def _run(cmd, timeout=10):
    try:
        return subprocess.run(
            cmd,
            text=True,
            capture_output=True,
            timeout=timeout,
        )
    except Exception as exc:
        print(f"[ALD] Check failed: {exc}")
        return None


def run(module, target=None):
    if module != "Doctor":
        print(f"[ALD] Unknown Doctor module: {module}")
        return

    print("[ALD] Doctor")
    print()
    print("[ALD] ALD system health")
    print("-" * 54)

    root = Path.home() / "Aldernix"

    checks = [
        ("Aldernix root", root.is_dir()),
        ("ald.py", (root / "ald" / "ald.py").is_file()),
        ("core directory", (root / "ald" / "core").is_dir()),
        ("reports directory", (root / "ald" / "reports").is_dir()),
        ("Python", shutil.which("python") is not None),
    ]

    passed = 0

    for name, ok in checks:
        print(f"[{'+' if ok else '-'}] {name}: {'OK' if ok else 'FAIL'}")
        passed += int(ok)

    print()
    print("[ALD] Tool availability")
    print("-" * 54)

    tool_ok = 0

    for name in TOOLS:
        path = shutil.which(name)

        if not path:
            print(f"[-] {name}: missing")
            continue

        tool_ok += 1

        result = _run([path, "--version"])

        if result and (result.stdout.strip() or result.stderr.strip()):
            text = (result.stdout or result.stderr).strip().splitlines()[0]
            print(f"[+] {name}: {text[:160]}")
        else:
            print(f"[+] {name}: {path}")

    print()
    print("[ALD] Python syntax check")
    print("-" * 54)

    python = shutil.which("python")
    syntax_failures = 0

    if python and root.is_dir():
        py_files = [
            p for p in (root / "ald").rglob("*.py")
            if ".git" not in p.parts
            and "__pycache__" not in p.parts
        ]

        for path in py_files:
            result = _run(
                [python, "-m", "py_compile", str(path)],
                timeout=10,
            )

            if not result or result.returncode != 0:
                syntax_failures += 1
                print(f"[FAIL] {path}")

        if syntax_failures == 0:
            print(f"[+] Compiled successfully: {len(py_files)} Python files")
    else:
        print("[-] Python project could not be checked.")

    print()
    print(f"[ALD] Core checks : {passed}/{len(checks)}")
    print(f"[ALD] Tools found : {tool_ok}/{len(TOOLS)}")
    print(f"[ALD] Syntax fails: {syntax_failures}")

    if passed == len(checks) and syntax_failures == 0:
        print("[ALD] Doctor status: HEALTHY")
    else:
        print("[ALD] Doctor status: ATTENTION REQUIRED")
