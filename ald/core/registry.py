#!/usr/bin/env python3

import shutil

REGISTRY = {
    "WEB SECURITY": {
        "HTTP Discovery": ["httpx", "curl"],
        "Endpoint Enumeration": ["ffuf", "feroxbuster", "gobuster"],
        "Technology Analysis": ["httpx", "whatweb"],
        "Vulnerability Analysis": ["nuclei", "nikto"],
        "TLS / Certificates": ["openssl", "nmap"],
    },

    "NETWORK SECURITY": {
        "Network Discovery": ["nmap", "rustscan", "naabu"],
        "Service Analysis": ["nmap"],
        "Packet Capture": ["tcpdump", "tshark"],
        "Protocol Analysis": ["tshark", "wireshark"],
        "DNS Security": ["dnsx", "dig", "dnsrecon"],
    },

    "OSINT": {
        "Username Discovery": ["maigret", "sherlock"],
        "Domain Intelligence": ["subfinder", "amass", "assetfinder"],
        "Image / Media": ["exiftool", "strings"],
        "Relationship Mapping": ["maltego", "recon-ng"],
    },

    "WIRELESS": {
        "Wi-Fi Discovery": ["aircrack-ng", "kismet"],
        "Packet Capture": ["airodump-ng", "tcpdump"],
        "Bluetooth": ["bluetoothctl"],
        "SDR / Radio": ["rtl_433", "gqrx"],
    },

    "PASSWORDS": {
        "Password Audit": ["john", "hashcat"],
        "Wordlist Engine": ["john", "hashcat"],
    },

    "HASH ANALYSIS": {
        "Hash Identification": ["hashid"],
        "Hashcat": ["hashcat"],
        "John the Ripper": ["john"],
    },

    "CRYPTOGRAPHY": {
        "OpenSSL": ["openssl"],
        "Encoding / Decoding": ["base64"],
    },

    "REVERSE ENGINEERING": {
        "Static Analysis": ["ghidra", "rizin", "radare2"],
        "Dynamic Analysis": ["gdb", "lldb", "frida"],
        "Strings / Metadata": ["strings", "readelf", "objdump"],
    },

    "FORENSICS": {
        "File Analysis": ["file", "exiftool"],
        "Disk Analysis": ["fls", "mmls"],
        "Memory Analysis": ["vol", "volatility"],
        "Recovery": ["foremost", "binwalk"],
    },

    "MOBILE SECURITY": {
        "ADB": ["adb"],
        "APK Analysis": ["apktool", "jadx"],
        "Dynamic Analysis": ["frida"],
    },

    "FUZZING": {
        "AFL++": ["afl-fuzz"],
        "Honggfuzz": ["honggfuzz"],
        "Radamsa": ["radamsa"],
    },

    "CLOUD SECURITY": {
        "Container Scan": ["trivy", "grype"],
        "SBOM": ["syft"],
        "IaC Analysis": ["checkov"],
        "Code Analysis": ["semgrep"],
    },
}


def available_tools(names):
    return {
        name: shutil.which(name)
        for name in names
        if shutil.which(name)
    }


def resolve(category, module):
    modules = REGISTRY.get(category.upper(), {})
    candidates = modules.get(module, [])

    installed = available_tools(candidates)

    return {
        "category": category,
        "module": module,
        "candidates": candidates,
        "installed": installed,
        "ready": bool(installed),
    }


def status():
    result = {}

    for category, modules in REGISTRY.items():
        result[category] = {}

        for module, tools in modules.items():
            result[category][module] = resolve(
                category,
                module,
            )

    return result
