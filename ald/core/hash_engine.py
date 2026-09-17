#!/usr/bin/env python3

import hashlib
import re
import shutil
from pathlib import Path


def _tool(name):
    return shutil.which(name)


def _local_guess(value):
    value = value.strip()

    patterns = {
        "MD5": r"^[a-fA-F0-9]{32}$",
        "SHA1": r"^[a-fA-F0-9]{40}$",
        "SHA256": r"^[a-fA-F0-9]{64}$",
        "SHA512": r"^[a-fA-F0-9]{128}$",
    }

    matches = [name for name, pattern in patterns.items()
               if re.fullmatch(pattern, value)]

    return matches


def run(module, target=None):
    if module == "Hash Identification":
        print("[ALD] Hash module : Hash Identification")
        print()

        value = input("Hash value: ").strip()

        if not value:
            print("[ALD] No hash supplied.")
            return

        matches = _local_guess(value)

        print()
        print("[ALD] Local format analysis")
        print("-" * 54)

        print(f"[+] Length      : {len(value)}")
        print(f"[+] Hexadecimal : {bool(re.fullmatch(r'[0-9a-fA-F]+', value))}")

        if matches:
            for match in matches:
                print(f"[+] Possible    : {match}")
        else:
            print("[ALD] No common fixed-length hex hash matched.")

        return

    if module == "Hashcat":
        print("[ALD] Hash module : Hashcat")
        print()

        tool = _tool("hashcat")

        if not tool:
            print("[ALD] Backend unavailable: hashcat")
            print("[ALD] Install hashcat through the Tool Factory.")
            return

        print(f"[ALD] Backend: {tool}")

        try:
            result = subprocess.run(
                [tool, "--version"],
                text=True,
                capture_output=True,
                timeout=10,
            )

            print(result.stdout.strip())

            if result.stderr:
                print(result.stderr.strip())

            if result.returncode == 0:
                print("[ALD] Hashcat backend verified.")
            else:
                print(f"[ALD] Hashcat exited with code {result.returncode}.")

        except subprocess.TimeoutExpired:
            print("[ALD] Hashcat verification timed out.")

        return

    if module == "John the Ripper":
        print("[ALD] Hash module : John the Ripper")
        print()

        tool = _tool("john")

        if not tool:
            print("[ALD] Backend unavailable: john")
            return

        print(f"[ALD] Backend: {tool}")

        try:
            result = shutil.which("john")
            if result:
                print("[ALD] John backend detected.")
        except Exception as exc:
            print(f"[ALD] Verification failed: {exc}")

        return

    if module == "Wordlist Analysis":
        print("[ALD] Hash module : Wordlist Analysis")
        print()

        dirs = [
            Path("/usr/share/wordlists"),
            Path("/usr/share/john"),
            Path.home() / "wordlists",
        ]

        files = []

        for directory in dirs:
            if not directory.exists():
                continue

            try:
                files.extend(
                    item for item in directory.iterdir()
                    if item.is_file()
                )
            except PermissionError:
                pass

        print(f"[ALD] Wordlist files detected: {len(files)}")
        return

    if module == "Crack Results":
        print("[ALD] Hash module : Crack Results")
        print()

        john = _tool("john")
        hashcat = _tool("hashcat")

        print("[ALD] Backend status")
        print("-" * 54)
        print(f"[+] John     : {john or 'not found'}")
        print(f"[+] Hashcat  : {hashcat or 'not found'}")
        print()

        locations = [
            Path.home() / ".john",
            Path("/root/.john"),
            Path("ald/reports"),
        ]

        result_files = []

        for directory in locations:
            if not directory.exists():
                continue

            try:
                for file in directory.rglob("*"):
                    if file.is_file():
                        result_files.append(file)
            except PermissionError:
                continue

        candidates = [
            file for file in result_files
            if any(
                key in file.name.lower()
                for key in ("john", "hashcat", "crack", "result", ".pot")
            )
        ]

        print("[ALD] Candidate result files")
        print("-" * 54)

        if not candidates:
            print("[ALD] No crack-result files detected.")
        else:
            for file in sorted(set(candidates))[-50:]:
                print(f"[+] {file}")

        print()
        print("[ALD] Result review is passive; no cracking operation is started.")
        return

    if module == "Evidence":
        report_dir = Path("ald/reports")
        report_dir.mkdir(parents=True, exist_ok=True)

        print("[ALD] Hash module : Evidence")
        print()
        print("[ALD] Evidence directory")
        print(report_dir.resolve())
        return

    print(f"[ALD] Unknown hash module: {module}")
