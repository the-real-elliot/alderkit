#!/usr/bin/env python3

import base64
import hashlib
import shutil
import subprocess
from pathlib import Path


def _tool(name):
    return shutil.which(name)


def run(module, target=None):
    if module == "File Hash":
        print("[ALD] Encryption module : File Hash")
        print()

        path = Path(input("File path: ").strip()).expanduser()

        if not path.is_file():
            print("[ALD] File not found.")
            return

        data = path.read_bytes()

        print(f"[ALD] File   : {path}")
        print(f"[ALD] Size   : {len(data)} bytes")
        print(f"[ALD] MD5    : {hashlib.md5(data).hexdigest()}")
        print(f"[ALD] SHA1   : {hashlib.sha1(data).hexdigest()}")
        print(f"[ALD] SHA256 : {hashlib.sha256(data).hexdigest()}")
        print(f"[ALD] SHA512 : {hashlib.sha512(data).hexdigest()}")
        return

    if module == "Base64":
        print("[ALD] Encryption module : Base64")
        print()
        print("[1] Encode")
        print("[2] Decode")

        choice = input("Choice [1]: ").strip() or "1"
        value = input("Data: ")

        if choice == "1":
            print(base64.b64encode(value.encode()).decode())
        elif choice == "2":
            try:
                print(base64.b64decode(value, validate=True).decode(
                    "utf-8", errors="replace"
                ))
            except Exception:
                print("[ALD] Invalid Base64 data.")
        else:
            print("[ALD] Invalid choice.")

        return

    if module == "OpenSSL":
        tool = _tool("openssl")

        print("[ALD] Encryption module : OpenSSL")
        print()

        if not tool:
            print("[ALD] OpenSSL backend unavailable.")
            return

        result = subprocess.run(
            [tool, "version"],
            text=True,
            capture_output=True,
            timeout=10,
        )

        print(result.stdout.strip())

        if result.stderr:
            print(result.stderr.strip())

        return

    if module == "Evidence":
        report_dir = Path("ald/reports")
        report_dir.mkdir(parents=True, exist_ok=True)

        print("[ALD] Encryption module : Evidence")
        print()
        print(report_dir.resolve())
        return

    print(f"[ALD] Unknown encryption module: {module}")
