#!/usr/bin/env python3

import base64
import hashlib
import math
import re
import secrets
import shutil
from pathlib import Path


def _tool(name):
    return shutil.which(name)


def run(module, target=None):
    if module == "Hash Functions":
        print("[ALD] Crypto module : Hash Functions")
        print()

        value = input("Data: ")

        if not value:
            print("[ALD] No data supplied.")
            return

        raw = value.encode()

        print()
        print(f"MD5     : {hashlib.md5(raw).hexdigest()}")
        print(f"SHA1    : {hashlib.sha1(raw).hexdigest()}")
        print(f"SHA256  : {hashlib.sha256(raw).hexdigest()}")
        print(f"SHA512  : {hashlib.sha512(raw).hexdigest()}")
        return

    if module == "Cipher Analysis":
        print("[ALD] Crypto module : Cipher Analysis")
        print()
        print("[1] Hexadecimal")
        print("[2] Base64")
        print("[3] ROT13")

        choice = input("Format [1]: ").strip() or "1"
        value = input("Data: ")

        if choice == "1":
            try:
                decoded = bytes.fromhex(value)
                print()
                print(decoded.decode("utf-8", errors="replace"))
            except ValueError:
                print("[ALD] Invalid hexadecimal input.")

        elif choice == "2":
            try:
                decoded = base64.b64decode(value, validate=True)
                print()
                print(decoded.decode("utf-8", errors="replace"))
            except Exception:
                print("[ALD] Invalid Base64 input.")

        elif choice == "3":
            import codecs
            print()
            print(codecs.decode(value, "rot_13"))

        else:
            print("[ALD] Invalid format.")

        return

        print("[ALD] Crypto module : Cipher Analysis")
        print()
        print("[ALD] This node currently performs format/encoding checks only.")
        print("[ALD] No key recovery or decryption is started.")
        return

    if module == "Encoding / Decoding":
        print("[ALD] Crypto module : Encoding / Decoding")
        print()
        print("[1] Base64 Encode")
        print("[2] Base64 Decode")

        choice = input("Choice: ").strip()

        if choice == "1":
            value = input("Text: ")
            print()
            print(base64.b64encode(value.encode()).decode())

        elif choice == "2":
            value = input("Base64: ").strip()

            try:
                decoded = base64.b64decode(
                    value,
                    validate=True,
                )
                print()
                print(decoded.decode("utf-8", errors="replace"))
            except Exception as exc:
                print(f"[ALD] Decode failed: {exc}")
        else:
            print("[ALD] Invalid choice.")

        return

    if module == "Randomness Analysis":
        print("[ALD] Crypto module : Randomness Analysis")
        print()

        value = input("Data: ")

        if not value:
            print("[ALD] No data supplied.")
            return

        raw = value.encode()

        counts = {}
        for byte in raw:
            counts[byte] = counts.get(byte, 0) + 1

        length = len(raw)
        entropy = 0.0

        for count in counts.values():
            probability = count / length
            entropy -= probability * math.log2(probability)

        unique = len(counts)
        max_entropy = math.log2(min(256, length))

        print()
        print("[ALD] Randomness analysis")
        print("-" * 54)
        print(f"[+] Bytes             : {length}")
        print(f"[+] Unique symbols    : {unique}")
        print(f"[+] Shannon entropy   : {entropy:.4f} bits/symbol")
        print(f"[+] Normalized entropy: {(entropy / 8):.4f}")
        print(f"[+] Maximum possible  : {max_entropy:.4f} bits/symbol")

        if entropy >= 7.5:
            assessment = "High entropy"
        elif entropy >= 5.0:
            assessment = "Moderate entropy"
        else:
            assessment = "Low entropy"

        print(f"[+] Assessment        : {assessment}")
        return

        print("[ALD] Crypto module : Randomness Analysis")
        print()

        value = input("Data: ")

        if not value:
            print("[ALD] No data supplied.")
            return

        raw = value.encode()
        counts = {}

        for byte in raw:
            counts[byte] = counts.get(byte, 0) + 1

        length = len(raw)
        entropy = 0.0

        for count in counts.values():
            p = count / length
            entropy -= p * math.log2(p)

        print(f"[ALD] Bytes   : {length}")
        print(f"[ALD] Symbols : {len(counts)}")
        print(f"[ALD] Entropy : {entropy:.4f} bits/symbol")
        return

    if module == "Key Material Analysis":
        print("[ALD] Crypto module : Key Material Analysis")
        print()

        value = input("Hex key material: ").strip()

        if not value:
            print("[ALD] No key material supplied.")
            return

        if not re.fullmatch(r"[0-9a-fA-F]+", value):
            print("[ALD] Input is not hexadecimal.")
            return

        print(f"[ALD] Length     : {len(value)} hex characters")
        print(f"[ALD] Bytes      : {len(value) // 2}")
        print(f"[ALD] Even length: {len(value) % 2 == 0}")
        return

    if module == "Evidence":
        report_dir = Path("ald/reports")
        report_dir.mkdir(parents=True, exist_ok=True)

        print("[ALD] Crypto module : Evidence")
        print()
        print(report_dir.resolve())
        return

    print(f"[ALD] Unknown crypto module: {module}")
