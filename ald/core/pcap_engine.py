#!/usr/bin/env python3

import shutil
import subprocess
from pathlib import Path


def _tool(name):
    return shutil.which(name)


def run(module, target=None):
    if module == "PCAP Inspection":
        print("[ALD] PCAP module : PCAP Inspection")
        print()

        path = Path(input("PCAP path: ").strip()).expanduser()

        if not path.is_file():
            print("[ALD] PCAP file not found.")
            return

        print(f"[ALD] File: {path}")
        print(f"[ALD] Size: {path.stat().st_size} bytes")

        tshark = _tool("tshark")
        capinfos = _tool("capinfos")

        if capinfos:
            try:
                result = subprocess.run(
                    [capinfos, str(path)],
                    text=True,
                    capture_output=True,
                    timeout=20,
                )
                print()
                print("[ALD] Capture information")
                print("-" * 54)
                print(result.stdout.strip())
            except Exception as exc:
                print(f"[ALD] capinfos failed: {exc}")

        if tshark:
            try:
                result = subprocess.run(
                    [
                        tshark,
                        "-r", str(path),
                        "-c", "20",
                        "-T", "fields",
                        "-e", "frame.number",
                        "-e", "frame.time",
                        "-e", "ip.src",
                        "-e", "ip.dst",
                        "-e", "_ws.col.Protocol",
                        "-e", "frame.len",
                    ],
                    text=True,
                    capture_output=True,
                    timeout=20,
                )

                print()
                print("[ALD] Packet sample")
                print("-" * 54)

                if result.stdout.strip():
                    print(result.stdout.strip())
                else:
                    print("[ALD] No packet records returned.")

            except Exception as exc:
                print(f"[ALD] tshark failed: {exc}")

        if not tshark and not capinfos:
            print("[ALD] No PCAP analysis backend found.")
            print("[ALD] Install tshark for packet inspection.")

        return

    if module == "Protocol Analysis":
        print("[ALD] PCAP module : Protocol Analysis")
        print()

        path = Path(input("PCAP path: ").strip()).expanduser()

        if not path.is_file():
            print("[ALD] PCAP file not found.")
            return

        tshark = _tool("tshark")

        if not tshark:
            print("[ALD] tshark backend: not found")
            return

        try:
            result = subprocess.run(
                [
                    tshark,
                    "-r", str(path),
                    "-q",
                    "-z", "io,phs",
                ],
                text=True,
                capture_output=True,
                timeout=30,
            )

            print(result.stdout.strip() or "[ALD] No protocol statistics returned.")

        except Exception as exc:
            print(f"[ALD] Protocol analysis failed: {exc}")

        return

    if module == "Evidence":
        report_dir = Path("ald/reports")
        report_dir.mkdir(parents=True, exist_ok=True)

        print("[ALD] PCAP module : Evidence")
        print(report_dir.resolve())
        return

    print(f"[ALD] Unknown PCAP module: {module}")
