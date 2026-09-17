#!/usr/bin/env python3

TOOLS = {
    "nmap": {
        "category": "NETWORK SECURITY",
        "capabilities": ["Network Discovery", "Service Analysis"],
        "binary": "nmap",
        "packages": ["nmap"],
        "verify": ["nmap", "--version"],
    },

    "curl": {
        "category": "WEB SECURITY",
        "capabilities": ["HTTP Discovery", "Technology Analysis"],
        "binary": "curl",
        "packages": ["curl"],
        "verify": ["curl", "--version"],
    },

    "openssl": {
        "category": "CRYPTOGRAPHY",
        "capabilities": ["TLS / Certificates", "Cryptography"],
        "binary": "openssl",
        "packages": ["openssl"],
        "verify": ["openssl", "version"],
    },

    "nuclei": {
        "category": "WEB SECURITY",
        "capabilities": ["Vulnerability Analysis"],
        "binary": "nuclei",
        "packages": ["nuclei"],
        "verify": ["nuclei", "-version"],
    },

    "nikto": {
        "category": "WEB SECURITY",
        "capabilities": ["Vulnerability Analysis"],
        "binary": "nikto",
        "packages": ["nikto"],
        "verify": ["nikto", "-Version"],
    },

    "ffuf": {
        "category": "WEB SECURITY",
        "capabilities": ["Endpoint Enumeration"],
        "binary": "ffuf",
        "packages": ["ffuf"],
        "verify": ["ffuf", "-V"],
    },

    "feroxbuster": {
        "category": "WEB SECURITY",
        "capabilities": ["Endpoint Enumeration"],
        "binary": "feroxbuster",
        "packages": ["feroxbuster"],
        "verify": ["feroxbuster", "--version"],
    },

    "gobuster": {
        "category": "WEB SECURITY",
        "capabilities": ["Endpoint Enumeration"],
        "binary": "gobuster",
        "packages": ["gobuster"],
        "verify": ["gobuster", "version"],
    },

    "maigret": {
        "category": "OSINT",
        "capabilities": ["Username Discovery"],
        "binary": "maigret",
        "packages": ["maigret"],
        "verify": ["maigret", "--version"],
    },

    "sherlock": {
        "category": "OSINT",
        "capabilities": ["Username Discovery"],
        "binary": "sherlock",
        "packages": ["sherlock"],
        "verify": ["sherlock", "--version"],
    },

    "subfinder": {
        "category": "OSINT",
        "capabilities": ["Domain Intelligence"],
        "binary": "subfinder",
        "packages": ["subfinder"],
        "verify": ["subfinder", "-version"],
    },

    "amass": {
        "category": "OSINT",
        "capabilities": ["Domain Intelligence"],
        "binary": "amass",
        "packages": ["amass"],
        "verify": ["amass", "-version"],
    },

    "aircrack-ng": {
        "category": "WIRELESS",
        "capabilities": ["Wi-Fi Discovery"],
        "binary": "aircrack-ng",
        "packages": ["aircrack-ng"],
        "verify": ["aircrack-ng", "--help"],
    },

    "john": {
        "category": "PASSWORDS",
        "capabilities": ["Password Audit", "Hash Analysis"],
        "binary": "john",
        "packages": ["john"],
        "verify": ["john", "--test"],
    },

    "hashcat": {
        "category": "HASH ANALYSIS",
        "capabilities": ["Password Audit", "Hash Analysis"],
        "binary": "hashcat",
        "packages": ["hashcat"],
        "verify": ["hashcat", "--version"],
    },

    "gdb": {
        "category": "REVERSE ENGINEERING",
        "capabilities": ["Dynamic Analysis", "Debugging"],
        "binary": "gdb",
        "packages": ["gdb"],
        "verify": ["gdb", "--version"],
    },

    "strings": {
        "category": "REVERSE ENGINEERING",
        "capabilities": ["Static Analysis", "Strings / Metadata"],
        "binary": "strings",
        "packages": ["binutils"],
        "verify": ["strings", "--version"],
    },

    "objdump": {
        "category": "REVERSE ENGINEERING",
        "capabilities": ["Static Analysis", "Binary Analysis"],
        "binary": "objdump",
        "packages": ["binutils"],
        "verify": ["objdump", "--version"],
    },

    "readelf": {
        "category": "REVERSE ENGINEERING",
        "capabilities": ["Static Analysis", "ELF Analysis"],
        "binary": "readelf",
        "packages": ["binutils"],
        "verify": ["readelf", "--version"],
    },

    "tcpdump": {
        "category": "NETWORK SECURITY",
        "capabilities": ["Packet Capture"],
        "binary": "tcpdump",
        "packages": ["tcpdump"],
        "verify": ["tcpdump", "--version"],
    },

    "tshark": {
        "category": "NETWORK SECURITY",
        "capabilities": ["Packet Analysis", "Protocol Analysis"],
        "binary": "tshark",
        "packages": ["wireshark-cli"],
        "verify": ["tshark", "--version"],
    },

    "yara": {
        "category": "FORENSICS",
        "capabilities": ["YARA / IOC Analysis", "Malware Analysis"],
        "binary": "yara",
        "packages": ["yara"],
        "verify": ["yara", "--version"],
    },

    "binwalk": {
        "category": "FORENSICS",
        "capabilities": ["Firmware Analysis", "File Analysis"],
        "binary": "binwalk",
        "packages": ["binwalk"],
        "verify": ["binwalk", "--help"],
    },
}


def get(name):
    return TOOLS.get(name)


def find_by_capability(capability):
    wanted = capability.lower().strip()

    return {
        name: info
        for name, info in TOOLS.items()
        if any(
            wanted in capability_name.lower()
            for capability_name in info["capabilities"]
        )
    }


def find_by_category(category):
    wanted = category.lower().strip()

    return {
        name: info
        for name, info in TOOLS.items()
        if info["category"].lower() == wanted
    }


TOOLS.update({
    "dig": {
        "category": "OSINT",
        "capabilities": ["DNS Intelligence"],
        "binary": "dig",
        "packages": ["bind"],
        "verify": ["dig", "-v"],
    },

    "nslookup": {
        "category": "OSINT",
        "capabilities": ["DNS Intelligence"],
        "binary": "nslookup",
        "packages": ["bind"],
        "verify": ["nslookup", "-version"],
    },
})
