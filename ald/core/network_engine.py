#!/usr/bin/env python3

import shutil
import subprocess


def run(module, target):
    tools = {
        "Network Discovery": "nmap",
        "Service Analysis": "nmap",
        "DNS Security": "dig",
        "Packet Capture": "tcpdump",
    }

    tool = tools.get(module)

    if not tool:
        print(f"[ALD] Unknown network module: {module}")
        return

    if not shutil.which(tool):
        print(f"[ALD] Missing backend: {tool}")
        return

    print(f"[ALD] Network module : {module}")
    print(f"[ALD] Target        : {target}")
    print(f"[ALD] Backend       : {tool}")
    print()

    if module == "Network Discovery":
        cmd = ["nmap", "-Pn", "--top-ports", "100", target]

    elif module == "Service Analysis":
        cmd = ["nmap", "-Pn", "-sV", "--top-ports", "1000", target]

    elif module == "DNS Security":
        cmd = ["dig", target]

    else:
        import os
        from pathlib import Path
        from datetime import datetime

        print("[ALD] Packet capture backend detected.")
        print()
        print("Available interfaces:")

        try:
            interfaces = [
                p.name
                for p in Path("/sys/class/net").iterdir()
            ]
        except Exception:
            interfaces = []

        for index, interface in enumerate(interfaces, 1):
            print(f"  [{index}] {interface}")

        if not interfaces:
            print("[ALD] No interfaces detected.")
            return

        print()
        choice = input("Interface number [1]: ").strip() or "1"

        try:
            interface = interfaces[int(choice) - 1]
        except (ValueError, IndexError):
            print("[ALD] Invalid interface.")
            return

        duration = input("Capture seconds [10]: ").strip() or "10"

        try:
            duration = max(1, min(60, int(duration)))
        except ValueError:
            duration = 10

        outdir = Path("ald/reports") / (
            datetime.now().strftime(
                "%Y%m%d_%H%M%S_packet_capture"
            )
        )
        outdir.mkdir(parents=True, exist_ok=True)

        pcap = outdir / "capture.pcap"

        cmd = [
            "tcpdump",
            "-i",
            interface,
            "-w",
            str(pcap),
            "-G",
            str(duration),
            "-W",
            "1",
        ]

        print()
        print("[ALD ENGINE] $", " ".join(cmd))
        print()

        try:
            result = subprocess.run(
                cmd,
                text=True,
                timeout=duration + 10,
            )

            print()

            if result.returncode == 0 and pcap.exists():
                print("[ALD] Packet capture complete.")
                print("[ALD] Evidence:", pcap)
            else:
                print(
                    "[ALD] Packet capture failed "
                    f"(exit code {result.returncode})."
                )

        except subprocess.TimeoutExpired:
            print("[ALD] Capture timed out safely.")

        return

    print("[ALD ENGINE] $", " ".join(cmd))
    print()

    try:
        subprocess.run(
            cmd,
            text=True,
            timeout=180,
        )
    except subprocess.TimeoutExpired:
        print("[ALD] Engine timed out.")
    except KeyboardInterrupt:
        print("\n[ALD] Engine interrupted.")
