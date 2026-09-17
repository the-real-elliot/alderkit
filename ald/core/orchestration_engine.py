#!/usr/bin/env python3

import shutil
from pathlib import Path


TOOL_GROUPS = {
    "Recon": [
        "nmap", "masscan", "arp", "ip", "ss",
    ],
    "Web": [
        "curl", "wget", "whatweb", "nikto",
    ],
    "Forensics": [
        "file", "exiftool", "strings", "tshark", "yara",
    ],
    "Mobile": [
        "adb",
    ],
    "Containers": [
        "docker", "podman",
    ],
    "Fuzzing": [
        "afl-fuzz", "honggfuzz", "radamsa",
    ],
    "Source": [
        "semgrep", "cppcheck", "shellcheck",
    ],
}


def run(module, target=None):
    if module == "Detect":
        print("[ALD] Orchestration module : Detect")
        print()
        print("[ALD] Tool availability")
        print("-" * 54)

        total = 0
        available = 0

        for group, tools in TOOL_GROUPS.items():
            print(f"\n[{group}]")

            for name in tools:
                total += 1
                path = shutil.which(name)

                if path:
                    available += 1
                    print(f"[+] {name}: {path}")
                else:
                    print(f"[-] {name}: not found")

        print()
        print(f"[ALD] Available: {available}/{total}")
        return

    if module == "Capability Matrix":
        print("[ALD] Orchestration module : Capability Matrix")
        print()

        for group, tools in TOOL_GROUPS.items():
            found = [name for name in tools if shutil.which(name)]
            print(f"{group}: {len(found)}/{len(tools)} available")

        return

    if module == "Evidence":
        report_dir = Path("ald/reports")
        report_dir.mkdir(parents=True, exist_ok=True)

        report = report_dir / "tool_orchestration_inventory.txt"

        lines = ["ALD // TOOL ORCHESTRATION", ""]

        for group, tools in TOOL_GROUPS.items():
            lines.append(f"[{group}]")
            for name in tools:
                path = shutil.which(name)
                lines.append(
                    f"{name}: {path or 'not found'}"
                )
            lines.append("")

        report.write_text("\n".join(lines))

        print("[ALD] Orchestration module : Evidence")
        print(f"[+] Evidence saved: {report}")
        return

    print(f"[ALD] Unknown orchestration module: {module}")
