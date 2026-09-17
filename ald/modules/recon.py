#!/usr/bin/env python3

import shutil
import subprocess
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime


def run(cmd, output_file=None):
    print(f"\033[1;33m[ALD]\033[0m $ {' '.join(cmd)}")

    try:
        if output_file:
            with open(output_file, "w") as out:
                subprocess.run(
                    cmd,
                    text=True,
                    stdout=out,
                    stderr=subprocess.STDOUT,
                    timeout=180
                )
            return Path(output_file).read_text(errors="replace")

        p = subprocess.run(
            cmd,
            text=True,
            capture_output=True,
            timeout=180
        )
        return p.stdout + p.stderr

    except Exception as e:
        return f"ERROR: {e}"


def parse_nmap(xml_file):
    data = {
        "hosts": [],
        "ports": []
    }

    try:
        root = ET.parse(xml_file).getroot()

        for host in root.findall("host"):
            status = host.find("status")

            host_data = {
                "status": status.get("state") if status is not None else "unknown",
                "addresses": [],
                "hostname": None
            }

            for address in host.findall("address"):
                host_data["addresses"].append(address.get("addr"))

            hostname = host.find("./hostnames/hostname")

            if hostname is not None:
                host_data["hostname"] = hostname.get("name")

            data["hosts"].append(host_data)

            for port in host.findall("./ports/port"):
                state = port.find("state")

                if state is None or state.get("state") != "open":
                    continue

                service = port.find("service")

                port_data = {
                    "port": int(port.get("portid")),
                    "protocol": port.get("protocol"),
                    "service": service.get("name") if service is not None else None,
                    "product": service.get("product") if service is not None else None,
                    "version": service.get("version") if service is not None else None
                }

                data["ports"].append(port_data)

    except Exception as e:
        data["error"] = str(e)

    return data


def print_profile(profile):
    print()
    print("\033[1;31m━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\033[0m")
    print("\033[1;31m TARGET PROFILE\033[0m")
    print("\033[1;31m━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\033[0m")

    for host in profile["hosts"]:
        print(f" Status       : {host['status'].upper()}")

        if host["addresses"]:
            print(f" Address      : {', '.join(host['addresses'])}")

        if host["hostname"]:
            print(f" Hostname     : {host['hostname']}")

    print()

    if not profile["ports"]:
        print(" Open ports   : 0")
        print()
        print(" \033[1;32mNo open TCP services detected.\033[0m")
        return

    print(f" Open ports   : {len(profile['ports'])}")
    print()

    for p in profile["ports"]:
        service = p["service"] or "unknown"

        details = " ".join(
            x for x in [p["product"], p["version"]] if x
        )

        if details:
            service += f" ({details})"

        print(
            f"  {p['port']}/{p['protocol']:<4} {service}"
        )


def recon(target, full=False):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    outdir = Path("ald/reports") / timestamp
    outdir.mkdir(parents=True, exist_ok=True)

    mode = "FULL RECON" if full else "RECON"

    print(f"\n\033[1;31m[ ALD // {mode} ]\033[0m")
    print(f"Target: {target}")
    print(f"Evidence: {outdir}\n")

    if not shutil.which("nmap"):
        print("\033[1;31m[-] nmap is not installed.\033[0m")
        return outdir

    xml_file = outdir / "nmap.xml"
    txt_file = outdir / "nmap.txt"

    run(
        [
            "nmap",
            "-sV",
            "--top-ports",
            "1000",
            "-oX",
            str(xml_file),
            target
        ],
        txt_file
    )

    if not xml_file.exists():
        print("\033[1;31m[-] Nmap XML output was not created.\033[0m")
        return outdir

    profile = parse_nmap(xml_file)

    profile["target"] = target
    profile["timestamp"] = timestamp
    profile["tools"] = ["nmap"]

    json_file = outdir / "target.json"

    json_file.write_text(
        json.dumps(profile, indent=2)
    )

    print_profile(profile)

    print()
    print("\033[1;32m[+] Recon complete\033[0m")
    print(f"[+] Evidence : {outdir}")
    print(f"[+] Profile  : {json_file}")

    return outdir
