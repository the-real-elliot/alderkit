#!/usr/bin/env python3

import shutil
from pathlib import Path
import subprocess


def _tool(name):
    return shutil.which(name)


def run(module, target=None):
    if module == "Wordlist Engine":
        print("[ALD] Password module : Wordlist Engine")
        print()

        john = _tool("john")

        if not john:
            print("[ALD] Missing backend: john")
            return

        wordlist_dirs = [
            Path("/usr/share/wordlists"),
            Path("/usr/share/john"),
            Path.home() / "wordlists",
        ]

        found = []

        for directory in wordlist_dirs:
            if not directory.exists():
                continue

            try:
                for item in sorted(directory.iterdir()):
                    if item.is_file():
                        found.append(item)
            except PermissionError:
                continue

        print("[ALD] Available wordlists")
        print("-" * 54)

        if not found:
            print("[ALD] No wordlist files detected.")
        else:
            for item in found[:100]:
                print(f"[+] {item}")

            if len(found) > 100:
                print(f"[ALD] ... {len(found) - 100} more files")

        print()
        print(f"[ALD] Wordlists detected: {len(found)}")
        return

    if module == "Credential Format Analysis":
        print("[ALD] Password module : Credential Format Analysis")
        print()
        print("[ALD] Analyze an authorized credential/hash file.")
        print()

        path = input("File path: ").strip()

        if not path:
            print("[ALD] No file supplied.")
            return

        file = Path(path).expanduser()

        if not file.is_file():
            print("[ALD] File not found.")
            return

        print()
        print("[ALD] File:", file)
        print("[ALD] Size:", file.stat().st_size, "bytes")

        try:
            sample = file.read_bytes()[:4096]

            text = sample.decode("utf-8", errors="replace")
            lines = [line for line in text.splitlines() if line.strip()]

            print("[ALD] Non-empty lines:", len(lines))

            if lines:
                print("[ALD] First line length:", len(lines[0]))

        except Exception as exc:
            print("[ALD] Analysis failed:", exc)

        return

    if module == "Password Policy":
        print("[ALD] Password module : Password Policy")
        print()
        print("[ALD] Local password-policy inventory")
        print("-" * 54)

        files = [
            Path("/etc/security/pwquality.conf"),
            Path("/etc/login.defs"),
        ]

        found = False

        for file in files:
            if not file.exists():
                continue

            found = True
            print(f"[+] {file}")

            try:
                lines = file.read_text(errors="replace").splitlines()

                for line in lines:
                    line = line.strip()

                    if not line or line.startswith("#"):
                        continue

                    keywords = (
                        "PASS_MIN_LEN",
                        "PASS_MAX_DAYS",
                        "PASS_MIN_DAYS",
                        "PASS_WARN_AGE",
                        "minlen",
                        "minclass",
                        "dcredit",
                        "ucredit",
                        "lcredit",
                        "ocredit",
                    )

                    if any(key.lower() in line.lower() for key in keywords):
                        print(f"    {line}")

            except PermissionError:
                print("    [ALD] Permission denied.")

        if not found:
            print("[ALD] No supported password-policy files found.")

        return

    if module == "Evidence":
        report_dir = Path("ald/reports")
        report_dir.mkdir(parents=True, exist_ok=True)

        print("[ALD] Password module : Evidence")
        print()
        print("[ALD] Evidence directory")
        print("-" * 54)

        files = sorted(
            f for f in report_dir.rglob("*")
            if f.is_file()
        )

        if not files:
            print("[ALD] No password evidence files found.")
        else:
            for file in files[-50:]:
                print(f"[+] {file}")

            if len(files) > 50:
                print(f"[ALD] Showing latest 50 of {len(files)} files.")

        return

    if module != "Password Audit":
        print(f"[ALD] Password module: {module}")
        print("[ALD] Engine not connected yet.")
        return

    john = _tool("john")

    print("[ALD] Password module : Password Audit")
    print()

    if not john:
        print("[ALD] Missing backend: john")
        print("[ALD] Install john.")
        return

    print(f"[ALD] Backend : {john}")
    print()

    try:
        result = subprocess.run(
            [john, "--list=build-info"],
            text=True,
            capture_output=True,
            timeout=10,
        )

        print(result.stdout)

        if result.stderr:
            print(result.stderr)

        print("[ALD] John backend verified.")

    except subprocess.TimeoutExpired:
        print("[ALD] John verification timed out.")
    except KeyboardInterrupt:
        print("\n[ALD] Password audit interrupted.")
