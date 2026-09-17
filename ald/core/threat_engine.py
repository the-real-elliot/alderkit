#!/usr/bin/env python3

import hashlib
import ipaddress
import re
from pathlib import Path


def classify(value):
    value = value.strip()

    try:
        ipaddress.ip_address(value)
        return "IPv4" if "." in value else "IPv6"
    except ValueError:
        pass

    if re.fullmatch(r"[0-9a-fA-F]{32}", value):
        return "MD5-like hash"

    if re.fullmatch(r"[0-9a-fA-F]{40}", value):
        return "SHA1-like hash"

    if re.fullmatch(r"[0-9a-fA-F]{64}", value):
        return "SHA256-like hash"

    if re.fullmatch(
        r"[a-fA-F0-9]{2}(:[a-fA-F0-9]{2}){5}",
        value,
    ):
        return "MAC address"

    if re.fullmatch(
        r"[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
        value,
    ):
        return "Domain"

    return "Unknown"


def run(module, target=None):
    if module == "IOC Analysis":
        print("[ALD] Threat Intelligence module : IOC Analysis")
        print()

        value = input("IOC value: ").strip()

        if not value:
            print("[ALD] Empty IOC.")
            return

        print(f"[ALD] Type: {classify(value)}")
        print(f"[ALD] Length: {len(value)}")

        sha256 = hashlib.sha256(value.encode()).hexdigest()

        print(f"[ALD] SHA256: {sha256}")
        print("[ALD] Reputation lookup is not performed automatically.")

        return

    if module == "Reputation":
        print("[ALD] Threat Intelligence module : Reputation")
        print()
        print("[ALD] Passive/local analysis only.")
        print("[ALD] External reputation APIs are not configured.")
        return

    if module == "Evidence":
        report_dir = Path("ald/reports")
        report_dir.mkdir(parents=True, exist_ok=True)

        print("[ALD] Threat Intelligence module : Evidence")
        print(report_dir.resolve())
        return

    print(f"[ALD] Unknown threat-intelligence module: {module}")
