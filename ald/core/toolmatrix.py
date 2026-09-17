#!/usr/bin/env python3

import shutil

TOOL_MATRIX = {
    "RECON": {
        "nmap": "Network discovery and service enumeration",
        "rustscan": "Fast port discovery",
        "masscan": "High-speed port scanner",
        "naabu": "Fast port enumeration",
        "amass": "Attack-surface and DNS enumeration",
        "subfinder": "Passive subdomain discovery",
        "assetfinder": "Domain asset discovery",
        "dnsx": "DNS resolution and probing",
        "httpx": "HTTP service probing and fingerprinting",
        "katana": "Web crawling and endpoint discovery",
    },

    "WEB": {
        "ffuf": "Web fuzzing and content discovery",
        "feroxbuster": "Recursive content discovery",
        "gobuster": "Directory and DNS enumeration",
        "nuclei": "Template-based vulnerability detection",
        "sqlmap": "SQL injection assessment",
        "dalfox": "XSS analysis",
        "arjun": "HTTP parameter discovery",
        "burpsuite": "Web security testing platform",
        "zaproxy": "Web application security testing",
        "caido": "HTTP interception and analysis",
    },

    "NETWORK": {
        "tcpdump": "Packet capture",
        "tshark": "CLI packet analysis",
        "wireshark": "Deep packet analysis",
        "scapy": "Packet crafting and analysis",
        "zeek": "Network security monitoring",
        "suricata": "Network IDS/IPS analysis",
        "bettercap": "Network assessment framework",
        "ettercap": "Network traffic analysis",
    },

    "OSINT": {
        "theHarvester": "Public-source reconnaissance",
        "sherlock": "Username discovery",
        "maigret": "Username investigation",
        "spiderfoot": "Automated OSINT collection",
        "recon-ng": "Reconnaissance framework",
        "maltego": "Relationship and intelligence analysis",
    },

    "REVERSE": {
        "ghidra": "Static binary analysis",
        "gdb": "Native debugging",
        "lldb": "Low-level debugging",
        "radare2": "Reverse engineering framework",
        "rizin": "Reverse engineering framework",
        "cutter": "GUI reverse engineering",
        "frida": "Dynamic instrumentation",
        "strings": "String extraction",
        "objdump": "Binary inspection",
        "readelf": "ELF analysis",
        "strace": "System-call tracing",
        "ltrace": "Library-call tracing",
    },

    "PWN": {
        "python": "Exploit-development scripting",
        "gdb": "Debugger",
        "pwndbg": "GDB exploitation extension",
        "pwntools": "Binary exploitation framework",
        "ropper": "ROP gadget analysis",
        "ROPgadget": "ROP gadget discovery",
        "angr": "Binary analysis and symbolic execution",
        "checksec": "Binary security-property inspection",
        "qemu-system-x86_64": "System emulation",
    },

    "FORENSICS": {
        "vol": "Memory forensics",
        "volatility": "Memory forensics",
        "binwalk": "Firmware and binary analysis",
        "foremost": "File carving",
        "autopsy": "Digital forensics",
        "yara": "Pattern-based file analysis",
        "fls": "Filesystem forensic analysis",
    },

    "MALWARE": {
        "yara": "Malware pattern matching",
        "capa": "Capability identification",
        "strings": "Static string analysis",
        "file": "File identification",
        "objdump": "Binary inspection",
        "readelf": "ELF inspection",
    },

    "WIRELESS": {
        "aircrack-ng": "Wireless security assessment",
        "airmon-ng": "Wireless interface management",
        "airodump-ng": "Wireless traffic observation",
        "kismet": "Wireless discovery and monitoring",
        "bettercap": "Network assessment",
    },

    "CLOUD": {
        "trivy": "Container and cloud-native scanning",
        "grype": "Software vulnerability scanning",
        "syft": "SBOM generation",
        "semgrep": "Static code analysis",
        "checkov": "Infrastructure-as-code analysis",
        "kube-bench": "Kubernetes security checks",
    },

    "MOBILE": {
        "adb": "Android debugging interface",
        "apktool": "Android package analysis",
        "jadx": "Android decompilation",
        "frida": "Dynamic instrumentation",
        "mobsf": "Mobile security analysis",
    },

    "FUZZING": {
        "afl-fuzz": "Coverage-guided fuzzing",
        "honggfuzz": "Security-oriented fuzzing",
        "boofuzz": "Protocol fuzzing",
        "radamsa": "Input mutation",
    },

    "CRYPTO": {
        "hashcat": "Password/hash auditing",
        "john": "Password/hash auditing",
        "openssl": "Cryptographic operations",
    },

    "HARDWARE": {
        "binwalk": "Firmware analysis",
        "strings": "Firmware string extraction",
        "objdump": "Binary inspection",
        "readelf": "ELF inspection",
    },
}


def detect_tools():
    result = {}

    for category, tools in TOOL_MATRIX.items():
        result[category] = {}

        for command, description in tools.items():
            path = shutil.which(command)

            result[category][command] = {
                "description": description,
                "installed": path is not None,
                "path": path
            }

    return result


def print_matrix():
    matrix = detect_tools()

    total = 0
    installed = 0

    print()
    print("\033[1;31m╔══════════════════════════════════════════════════════════════╗\033[0m")
    print("\033[1;31m║                 ALD // TOOL MATRIX                         ║\033[0m")
    print("\033[1;31m╚══════════════════════════════════════════════════════════════╝\033[0m")

    for category, tools in matrix.items():
        print(f"\n\033[1;33m[{category}]\033[0m")

        for command, data in tools.items():
            total += 1

            if data["installed"]:
                installed += 1
                symbol = "\033[1;32m✓ READY\033[0m"
            else:
                symbol = "\033[1;31m✗ MISSING\033[0m"

            print(f"  {symbol:<20} {command:<24} {data['description']}")

    print()
    print("\033[1;31m──────────────────────────────────────────────────────────────\033[0m")
    print(f"  TOOL COVERAGE: {installed}/{total}")
    print("\033[1;31m──────────────────────────────────────────────────────────────\033[0m")
    print()


if __name__ == "__main__":
    print_matrix()
