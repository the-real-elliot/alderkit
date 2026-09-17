#!/usr/bin/env python3

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ALD_DIR = ROOT / "ald"

sys.path.insert(0, str(ALD_DIR))

from core.pages import (
    RED,
    YELLOW,
    GREEN,
    CYAN,
    RESET,
    header,
    pause,
    menu_page,
    info_page,
)

from core.engine import dispatch
from core import web_engine
from core import osint_engine
from core import network_engine
from core import wireless_engine
from core import password_engine
from core import hash_engine
from core import crypto_engine
from core import encryption_engine
from core import reverse_engine
from core import forensics_engine
from core import memory_engine
from core import mobile_engine
from core import cloud_engine
from core import container_engine
from core import api_engine
from core import database_engine
from core import fuzzing_engine
from core import vulnresearch_engine
from core import dos_engine
from core import pcap_engine
from core import dns_engine
from core import email_engine
from core import bluetooth_engine
from core import rfid_engine
from core import sdr_engine
from core import hardware_engine
from core import stego_engine
from core import tls_engine
from core import threat_engine
from core import source_engine
from core import supply_engine
from core import incident_engine
from core import yara_engine
from core import automation_engine
from core import orchestration_engine
from core import evidence_engine
from core import reports_engine
from core import inventory_engine
from core import doctor_engine
from core import update_engine
from core.toolfactory import main as toolfactory_main
from core.updater import main as updater_main
from core.state import get_target, set_target, clear_target
from core.registry import resolve

# Existing ALD engines
try:
    from modules.recon import recon
except Exception:
    recon = None

try:
    from core.toolmatrix import print_matrix, detect_tools
except Exception:
    print_matrix = None
    detect_tools = None

try:
    from core.intel import print_plan
except Exception:
    print_plan = None


# ============================================================
# GLOBAL STATE
# ============================================================

target = get_target()


# ============================================================
# TARGET
# ============================================================

def target_page():
    global target

    while True:
        choice = menu_page(
            "TARGET",
            target,
            [
                ("1", "Set Target"),
                ("2", "Show Target"),
                ("3", "Clear Target"),
            ],
            "ALD TARGET / SCOPE CONTROL",
        )

        if choice is None:
            return

        if choice == "1":
            header("TARGET // SET")

            value = input(
                f"{YELLOW}Target > {RESET}"
            ).strip()

            if value:
                target = value
                set_target(target)
                print(f"\n{GREEN}[+] Target set:{RESET} {target}")
            else:
                print(f"\n{RED}[-] Empty target.{RESET}")

            pause()

        elif choice == "2":
            info_page(
                "TARGET // CURRENT",
                target,
                [
                    f"{YELLOW}Current target:{RESET} "
                    f"{target or 'NOT SET'}"
                ],
            )

        elif choice == "3":
            clear_target()
            target = None

            info_page(
                "TARGET // CLEARED",
                None,
                [
                    f"{GREEN}[+] Target cleared.{RESET}"
                ],
            )


# ============================================================
# RECON
# ============================================================

def recon_page():
    if not target:
        info_page(
            "RECON // NO TARGET",
            None,
            [
                f"{RED}[-] No target has been configured.{RESET}",
                "",
                "Go to:",
                "  Target → Set Target",
            ],
        )
        return

    if recon is None:
        info_page(
            "RECON // ENGINE ERROR",
            target,
            [
                f"{RED}[-] modules.recon could not be loaded.{RESET}",
            ],
        )
        return

    choice = menu_page(
        "RECONNAISSANCE",
        target,
        [
            ("1", "Standard Recon"),
            ("2", "Full Recon"),
            ("3", "Evidence"),
        ],
        "NETWORK / SERVICE RECONNAISSANCE",
    )

    if choice == "1":
        header("RECON // STANDARD")
        print(f"{YELLOW}TARGET:{RESET} {target}")
        print()
        recon(target, full=False)
        pause()

    elif choice == "2":
        header("RECON // FULL")
        print(f"{YELLOW}TARGET:{RESET} {target}")
        print()
        recon(target, full=True)
        pause()

    elif choice == "3":
        info_page(
            "RECON // EVIDENCE",
            target,
            [
                "Recon evidence is stored under:",
                "",
                "  ald/reports/",
                "",
                "Each assessment can contain:",
                "  → nmap output",
                "  → target.json",
                "  → parsed services",
                "  → timestamps",
            ],
        )


# ============================================================
# OSINT
# ============================================================

def osint_platform(title, description, items):
    info_page(
        title,
        target,
        [
            f"{GREEN}[ALD OSINT MODULE]{RESET}",
            "",
            description,
            "",
            *[f"  → {item}" for item in items],
            "",
            "Only public / authorized information is processed.",
        ],
    )


def osint_target_page():
    while True:
        choice = menu_page(
            "OSINT // TARGET INTELLIGENCE",
            target,
            [
                ("1", "Username"),
                ("2", "Email"),
                ("3", "Phone"),
            ],
            "PUBLIC / AUTHORIZED TARGET INTELLIGENCE",
        )

        if choice is None:
            return

        if choice == "1":
            value = input(
                f"{YELLOW}Username > {RESET}"
            ).strip()

            if value:
                osint_engine.run(
                    "Username Discovery",
                    value,
                )
                pause()

        elif choice == "2":
            value = input(
                f"{YELLOW}Email > {RESET}"
            ).strip()

            if value:
                osint_engine.run(
                    "Email Intelligence",
                    value,
                )
                pause()

        elif choice == "3":
            value = input(
                f"{YELLOW}Phone > {RESET}"
            ).strip()

            if value:
                osint_engine.run(
                    "Phone Intelligence",
                    value,
                )
                pause()


def osint_domain_page():
    while True:
        choice = menu_page(
            "OSINT // DOMAIN INTELLIGENCE",
            target,
            [
                ("1", "Subdomain Intelligence"),
                ("2", "DNS Intelligence"),
                ("3", "Certificate Intelligence"),
            ],
            "DOMAIN / INFRASTRUCTURE INTELLIGENCE",
        )

        if choice is None:
            return

        if not target:
            info_page(
                "OSINT // NO DOMAIN",
                None,
                [
                    f"{RED}[-] Set a domain target first.{RESET}",
                ],
            )
            continue

        if choice == "1":
            osint_engine.run(
                "Domain Intelligence",
                target,
            )
            pause()

        elif choice == "2":
            osint_engine.run(
                "DNS Intelligence",
                target,
            )
            pause()

        elif choice == "3":
            osint_engine.run(
                "Certificate Intelligence",
                target,
            )
            pause()


def osint_username_page():
    choice = menu_page(
        "OSINT // USERNAME INTELLIGENCE",
        target,
        [
            ("1", "Username Discovery"),
            ("2", "Cross-Platform Correlation"),
            ("3", "Profile Comparison"),
            ("4", "Evidence"),
        ],
        "PUBLIC USERNAME INTELLIGENCE",
    )

    if choice:
        info_page(
            "OSINT // USERNAME MODULE",
            target,
            [
                f"{GREEN}[MODULE READY]{RESET}",
                "",
                f"Selected module: {choice}",
            ],
        )


def osint_media_page():
    choice = menu_page(
        "OSINT // IMAGE / MEDIA",
        target,
        [
            ("1", "Metadata"),
            ("2", "File Information"),
            ("3", "Hash"),
            ("4", "Visual Indicators"),
            ("5", "Evidence"),
        ],
        "IMAGE / MEDIA INTELLIGENCE",
    )

    if choice:
        info_page(
            "OSINT // MEDIA MODULE",
            target,
            [
                f"{GREEN}[MODULE READY]{RESET}",
                "",
                f"Selected module: {choice}",
            ],
        )


def osint_page():
    while True:
        choice = menu_page(
            "OSINT",
            target,
            [
                ("1", "Target Intelligence"),
                ("2", "Domain Intelligence"),
                ("3", "Username Intelligence"),
                ("4", "Image / Media Analysis"),
                ("5", "Relationship Mapping"),
                ("6", "Threat Intelligence"),
                ("7", "Evidence"),
            ],
            "OPEN-SOURCE INTELLIGENCE OPERATIONS",
        )

        if choice is None:
            return

        if choice == "1":
            osint_target_page()

        elif choice == "2":
            osint_domain_page()

        elif choice == "3":
            osint_username_page()

        elif choice == "4":
            osint_media_page()

        elif choice == "5":
            info_page(
                "OSINT // RELATIONSHIP MAPPING",
                target,
                [
                    "Entity relationship workspace",
                    "",
                    "  → Identity relationships",
                    "  → Domain relationships",
                    "  → Organization relationships",
                    "  → Infrastructure relationships",
                    "  → Evidence graph",
                ],
            )

        elif choice == "6":
            info_page(
                "OSINT // THREAT INTELLIGENCE",
                target,
                [
                    "Threat intelligence workspace",
                    "",
                    "  → IOC collection",
                    "  → IP intelligence",
                    "  → Domain intelligence",
                    "  → Malware intelligence",
                    "  → Threat reporting",
                ],
            )

        elif choice == "7":
            info_page(
                "OSINT // EVIDENCE",
                target,
                [
                    "Evidence workspace",
                    "",
                    "  → URLs",
                    "  → Collected artifacts",
                    "  → Screenshots",
                    "  → Hashes",
                    "  → Timestamps",
                ],
            )


# ============================================================
# GENERIC NESTED CATEGORIES
# ============================================================

def category_page(title, description, options):
    choice = menu_page(
        title,
        target,
        options,
        description,
    )

    if choice is None:
        return

    selected = dict(options).get(choice)

    if not selected:
        return

    # Real engine mappings.
    real_modules = {
        "WEB SECURITY": {
            "HTTP Discovery",
            "Endpoint Enumeration",
            "Vulnerability Analysis",
        },
        "NETWORK SECURITY": {
            "Network Discovery",
            "Service Analysis",
        },
        "OSINT": {
            "Username Discovery",
            "Domain Intelligence",
        },
    }

    if selected in real_modules.get(title, set()):
        header(f"{title} // {selected.upper()}")

        print(f"{YELLOW}TARGET:{RESET} {target}")
        print()

        info = resolve(title, selected)

        print(f"{CYAN}ALD MODULE REGISTRY{RESET}")
        print()

        if info["installed"]:
            print(f"{GREEN}[+] READY{RESET}")
            print()
            print("Available engines:")

            for tool, path in info["installed"].items():
                print(f"  {GREEN}✓{RESET} {tool:<18} {path}")

            print()

            evidence = dispatch(
                title,
                selected,
                target,
            )

            if evidence:
                print()
                print(
                    f"{GREEN}[+] Module complete.{RESET}"
                )
                print(
                    f"{CYAN}Evidence:{RESET} {evidence}"
                )

        else:
            print(f"{RED}[-] NO ENGINE AVAILABLE{RESET}")
            print()
            print("Expected tools:")

            for tool in info["candidates"]:
                print(f"  {YELLOW}•{RESET} {tool}")

            print()
            print(
                "Install one of the listed tools and "
                "ALD will detect it automatically."
            )

        pause()
        return

    info_page(
        f"{title} // {selected.upper()}",
        target,
        [
            f"{GREEN}[MODULE REGISTERED]{RESET}",
            "",
            f"Category : {title}",
            f"Module   : {selected}",
            "",
            "This module is registered.",
            "Its specific engine has not yet been attached.",
        ],
    )


def web_page():
    while True:
        choice = menu_page(
            "WEB SECURITY",
            target,
            [
                ("1", "HTTP Discovery"),
                ("2", "Endpoint Enumeration"),
                ("3", "Technology Analysis"),
                ("4", "API Security"),
                ("5", "Vulnerability Analysis"),
                ("6", "TLS / Certificates"),
                ("7", "Evidence"),
            ],
            "AUTHORIZED WEB APPLICATION SECURITY",
        )

        if choice is None:
            return

        modules = {
            "1": "HTTP Discovery",
            "2": "Endpoint Enumeration",
            "3": "Technology Analysis",
            "4": "API Security",
            "5": "Vulnerability Analysis",
            "6": "TLS / Certificates",
        }

        if choice in modules:
            if not target:
                info_page(
                    "WEB SECURITY // NO TARGET",
                    None,
                    [
                        f"{RED}[-] No target is configured.{RESET}",
                        "",
                        "Set one through:",
                        "  Target → Set Target",
                    ],
                )
                continue

            header(
                f"WEB SECURITY // "
                f"{modules[choice].upper()}"
            )

            print(
                f"{YELLOW}TARGET:{RESET} {target}"
            )
            print()

            web_engine.run(
                modules[choice],
                target,
            )

            pause()

        elif choice == "7":
            info_page(
                "WEB SECURITY // EVIDENCE",
                target,
                [
                    "ALD web evidence is stored under:",
                    "",
                    "  ald/reports/",
                    "",
                    "Each module creates its own timestamped",
                    "evidence directory.",
                ],
            )


def network_page():
    while True:
        choice = menu_page(
            "NETWORK SECURITY",
            target,
            [
                ("1", "Network Discovery"),
                ("2", "Service Analysis"),
                ("3", "DNS Security"),
                ("4", "Packet Capture"),
                ("5", "Evidence"),
            ],
            "AUTHORIZED NETWORK SECURITY OPERATIONS",
        )

        if choice is None:
            return

        if not target:
            info_page(
                "NETWORK SECURITY // NO TARGET",
                None,
                [
                    f"{RED}[-] No target is configured.{RESET}",
                    "",
                    "Set one through Target → Set Target.",
                ],
            )
            continue

        modules = {
            "1": "Network Discovery",
            "2": "Service Analysis",
            "3": "DNS Security",
            "4": "Packet Capture",
        }

        if choice == "5":
            info_page(
                "NETWORK SECURITY // EVIDENCE",
                target,
                [
                    "Evidence location:",
                    "  ald/reports/",
                ],
            )
            continue

        module = modules[choice]

        header(
            f"NETWORK SECURITY // {module.upper()}"
        )

        print(f"{YELLOW}TARGET:{RESET} {target}")
        print()

        network_engine.run(module, target)

        pause()


def wireless_page():
    while True:
        choice = menu_page(
            "WIRELESS",
            target,
            [
                ("1", "Wi-Fi Discovery"),
                ("2", "Access Point Analysis"),
                ("3", "Packet Capture"),
                ("4", "Bluetooth"),
                ("5", "SDR / Radio"),
            ],
            "WIRELESS SECURITY OPERATIONS",
        )

        if choice is None:
            return

        if choice == "1":
            header("WIRELESS // WI-FI DISCOVERY")
            print()

            wireless_engine.run(
                "Wi-Fi Discovery",
                target,
            )

            pause()

        elif choice == "2":
            header("WIRELESS // ACCESS POINT ANALYSIS")
            print()

            wireless_engine.run(
                "Access Point Analysis",
                target,
            )

            pause()

        elif choice == "3":
            header("WIRELESS // PACKET CAPTURE")
            print()

            network_engine.run(
                "Packet Capture",
                target,
            )

            pause()

        elif choice == "4":
            header("WIRELESS // BLUETOOTH")
            print()

            wireless_engine.run(
                "Bluetooth",
                target,
            )

            pause()

        elif choice == "5":
            header("WIRELESS // SDR / RADIO")
            print()

            wireless_engine.run(
                "SDR / Radio",
                target,
            )

            pause()

        else:
            info_page(
                "WIRELESS // MODULE",
                target,
                [
                    f"{YELLOW}[ALD]{RESET} Module registered.",
                    "",
                    "This wireless node will be connected",
                    "to its backend engine next.",
                ],
            )


def passwords_page():
    while True:
        choice = menu_page(
            "PASSWORDS",
            target,
            [
                ("1", "Password Audit"),
                ("2", "Wordlist Engine"),
                ("3", "Credential Format Analysis"),
                ("4", "Password Policy"),
                ("5", "Evidence"),
            ],
            "AUTHORIZED PASSWORD SECURITY TESTING",
        )

        if choice is None:
            return

        if choice == "1":
            header("PASSWORDS // PASSWORD AUDIT")
            print()
            password_engine.run("Password Audit", target)
            pause()

        elif choice == "2":
            header("PASSWORDS // WORDLIST ENGINE")
            print()
            password_engine.run("Wordlist Engine", target)
            pause()

        elif choice == "3":
            header("PASSWORDS // CREDENTIAL FORMAT ANALYSIS")
            print()
            password_engine.run("Credential Format Analysis", target)
            pause()

        elif choice == "4":
            header("PASSWORDS // PASSWORD POLICY")
            print()
            password_engine.run("Password Policy", target)
            pause()

        elif choice == "5":
            header("PASSWORDS // EVIDENCE")
            print()
            password_engine.run("Evidence", target)
            pause()

        else:
            info_page(
                "PASSWORDS // MODULE",
                target,
                [
                    f"{YELLOW}[ALD]{RESET} Module registered.",
                    "",
                    "This password node will be connected",
                    "to its backend engine next.",
                ],
            )


def hash_page():
    while True:
        choice = menu_page(
            "HASH ANALYSIS",
            target,
            [
                ("1", "Hash Identification"),
                ("2", "Hashcat"),
                ("3", "John the Ripper"),
                ("4", "Wordlist Analysis"),
                ("5", "Crack Results"),
                ("6", "Evidence"),
            ],
            "HASH IDENTIFICATION / AUTHORIZED AUDITING",
        )

        if choice is None:
            return

        if choice == "1":
            header("HASH ANALYSIS // HASH IDENTIFICATION")
            print()
            hash_engine.run("Hash Identification", target)
            pause()

        elif choice == "2":
            header("HASH ANALYSIS // HASHCAT")
            print()
            hash_engine.run("Hashcat", target)
            pause()

        elif choice == "3":
            header("HASH ANALYSIS // JOHN THE RIPPER")
            print()
            hash_engine.run("John the Ripper", target)
            pause()

        elif choice == "4":
            header("HASH ANALYSIS // WORDLIST ANALYSIS")
            print()
            hash_engine.run("Wordlist Analysis", target)
            pause()

        elif choice == "5":
            header("HASH ANALYSIS // CRACK RESULTS")
            print()
            hash_engine.run("Crack Results", target)
            pause()

        elif choice == "6":
            header("HASH ANALYSIS // EVIDENCE")
            print()
            hash_engine.run("Evidence", target)
            pause()


def crypto_page():
    while True:
        choice = menu_page(
            "CRYPTOGRAPHY",
            target,
            [
                ("1", "Hash Functions"),
                ("2", "Cipher Analysis"),
                ("3", "Encoding / Decoding"),
                ("4", "Randomness Analysis"),
                ("5", "Key Material Analysis"),
                ("6", "Evidence"),
            ],
            "CRYPTOGRAPHIC ANALYSIS",
        )

        if choice is None:
            return

        if choice == "1":
            header("CRYPTOGRAPHY // HASH FUNCTIONS")
            print()
            crypto_engine.run("Hash Functions", target)
            pause()

        elif choice == "2":
            header("CRYPTOGRAPHY // CIPHER ANALYSIS")
            print()
            crypto_engine.run("Cipher Analysis", target)
            pause()

        elif choice == "3":
            header("CRYPTOGRAPHY // ENCODING / DECODING")
            print()
            crypto_engine.run("Encoding / Decoding", target)
            pause()

        elif choice == "4":
            header("CRYPTOGRAPHY // RANDOMNESS ANALYSIS")
            print()
            crypto_engine.run("Randomness Analysis", target)
            pause()

        elif choice == "5":
            header("CRYPTOGRAPHY // KEY MATERIAL ANALYSIS")
            print()
            crypto_engine.run("Key Material Analysis", target)
            pause()

        elif choice == "6":
            header("CRYPTOGRAPHY // EVIDENCE")
            print()
            crypto_engine.run("Evidence", target)
            pause()


def encryption_page():
    while True:
        choice = menu_page(
            "ENCRYPTION / DECRYPTION",
            target,
            [
                ("1", "Base64"),
                ("2", "Hex"),
                ("3", "URL Encoding"),
                ("4", "AES"),
                ("5", "RSA"),
                ("6", "OpenSSL"),
                ("7", "File Encryption Analysis"),
                ("8", "Evidence"),
            ],
            "AUTHORIZED ENCRYPTION ANALYSIS",
        )

        if choice is None:
            return

        if choice == "1":
            header("ENCRYPTION // BASE64")
            print()
            encryption_engine.run("Base64", target)
            pause()

        elif choice == "6":
            header("ENCRYPTION // OPENSSL")
            print()
            encryption_engine.run("OpenSSL", target)
            pause()

        elif choice == "7":
            header("ENCRYPTION // FILE HASH")
            print()
            encryption_engine.run("File Hash", target)
            pause()

        elif choice == "8":
            header("ENCRYPTION // EVIDENCE")
            print()
            encryption_engine.run("Evidence", target)
            pause()

        else:
            info_page(
                "ENCRYPTION // MODULE",
                target,
                [
                    f"{YELLOW}[ALD]{RESET} Module registered.",
                    "",
                    "This encryption node will be connected",
                    "to its backend engine next.",
                ],
            )


def reverse_page():
    while True:
        choice = menu_page(
            "REVERSE ENGINEERING",
            target,
            [
                ("1", "Static Analysis"),
                ("2", "Dynamic Analysis"),
                ("3", "Disassembly"),
                ("4", "Debugging"),
                ("5", "Instrumentation"),
                ("6", "Strings / Metadata"),
                ("7", "Evidence"),
            ],
            "BINARY / SOFTWARE ANALYSIS",
        )

        if choice is None:
            return

        if choice == "1":
            header("REVERSE // STATIC ANALYSIS")
            print()
            reverse_engine.run("Static Analysis", target)
            pause()

        elif choice == "2":
            header("REVERSE // DYNAMIC ANALYSIS")
            print()
            reverse_engine.run("Dynamic Analysis", target)
            pause()

        elif choice == "3":
            header("REVERSE // DISASSEMBLY")
            print()
            reverse_engine.run("Disassembly", target)
            pause()

        elif choice == "4":
            header("REVERSE // DEBUGGING")
            print()
            reverse_engine.run("Debugging", target)
            pause()

        elif choice == "6":
            header("REVERSE // STRINGS / METADATA")
            print()
            reverse_engine.run("Strings / Metadata", target)
            pause()

        elif choice == "7":
            header("REVERSE // EVIDENCE")
            print()
            reverse_engine.run("Evidence", target)
            pause()

        else:
            info_page(
                "REVERSE // MODULE",
                target,
                [
                    f"{YELLOW}[ALD]{RESET} Module registered.",
                    "",
                    "This reverse-engineering node will be connected",
                    "to its backend engine next.",
                ],
            )


def forensics_page():
    while True:
        choice = menu_page(
            "FORENSICS",
            target,
            [
                ("1", "File Analysis"),
                ("2", "Disk Analysis"),
                ("3", "Memory Analysis"),
                ("4", "Timeline Analysis"),
                ("5", "Metadata"),
                ("6", "Evidence"),
            ],
            "DIGITAL FORENSIC ANALYSIS",
        )
        if choice is None:
            return
        if choice == "1":
            header("FORENSICS // FILE ANALYSIS"); print(); forensics_engine.run("File Analysis", target); pause()
        elif choice == "2":
            header("FORENSICS // DISK ANALYSIS"); print(); forensics_engine.run("Disk Analysis", target); pause()
        elif choice == "3":
            header("FORENSICS // MEMORY ANALYSIS"); print(); forensics_engine.run("Memory Analysis", target); pause()
        elif choice == "4":
            header("FORENSICS // TIMELINE ANALYSIS"); print(); forensics_engine.run("Timeline Analysis", target); pause()
        elif choice == "5":
            header("FORENSICS // METADATA"); print(); forensics_engine.run("Metadata", target); pause()
        elif choice == "6":
            header("FORENSICS // EVIDENCE"); print(); forensics_engine.run("Evidence", target); pause()
        else:
            info_page("FORENSICS // MODULE", target, [f"{YELLOW}[ALD]{RESET} Module registered."])

# ============================================================
# REMAINING CATEGORY PAGES
# ============================================================

def memory_page():
    while True:
        choice = menu_page(
            "MEMORY FORENSICS",
            target,
            [
                ("1", "Memory Image Analysis"),
                ("2", "Process Analysis"),
                ("3", "Network Artifacts"),
                ("4", "Evidence"),
            ],
            "MEMORY FORENSIC ANALYSIS",
        )
        if choice is None:
            return
        if choice == "1":
            header("MEMORY FORENSICS // MEMORY IMAGE ANALYSIS"); print(); memory_engine.run("Memory Image Analysis", target); pause()
        elif choice == "2":
            header("MEMORY FORENSICS // PROCESS ANALYSIS"); print(); memory_engine.run("Process Analysis", target); pause()
        elif choice == "3":
            header("MEMORY FORENSICS // NETWORK ARTIFACTS"); print(); memory_engine.run("Network Artifacts", target); pause()
        elif choice == "4":
            header("MEMORY FORENSICS // EVIDENCE"); print(); memory_engine.run("Evidence", target); pause()

def mobile_page():
    while True:
        choice = menu_page(
            "MOBILE SECURITY",
            target,
            [
                ("1", "ADB"),
                ("2", "APK Analysis"),
                ("3", "Dynamic Analysis"),
                ("4", "Evidence"),
            ],
            "AUTHORIZED MOBILE SECURITY TESTING",
        )

        if choice is None:
            return

        if choice == "1":
            header("MOBILE // ADB")
            print()
            mobile_engine.run("ADB", target)
            pause()

        elif choice == "2":
            header("MOBILE // APK ANALYSIS")
            print()
            mobile_engine.run("APK Analysis", target)
            pause()

        elif choice == "3":
            header("MOBILE // DYNAMIC ANALYSIS")
            print()
            mobile_engine.run("Dynamic Analysis", target)
            pause()

        elif choice == "4":
            header("MOBILE // EVIDENCE")
            print()
            mobile_engine.run("Evidence", target)
            pause()

def cloud_page():
    while True:
        choice = menu_page(
            "CLOUD SECURITY",
            target,
            [
                ("1", "Container Scan"),
                ("2", "IaC Analysis"),
                ("3", "SBOM"),
                ("4", "Code Analysis"),
                ("5", "Evidence"),
            ],
            "AUTHORIZED CLOUD SECURITY ANALYSIS",
        )
        if choice is None:
            return
        if choice == "1":
            header("CLOUD // CONTAINER SCAN"); print(); cloud_engine.run("Container Scan", target); pause()
        elif choice == "2":
            header("CLOUD // IAC ANALYSIS"); print(); cloud_engine.run("IaC Analysis", target); pause()
        elif choice == "3":
            header("CLOUD // SBOM"); print(); cloud_engine.run("SBOM", target); pause()
        elif choice == "4":
            header("CLOUD // CODE ANALYSIS"); print(); cloud_engine.run("Code Analysis", target); pause()
        elif choice == "5":
            header("CLOUD // EVIDENCE"); print(); cloud_engine.run("Evidence", target); pause()

def container_page():
    while True:
        choice = menu_page(
            "CONTAINER SECURITY",
            target,
            [
                ("1", "Image Analysis"),
                ("2", "Runtime Analysis"),
                ("3", "SBOM"),
                ("4", "Evidence"),
            ],
            "AUTHORIZED CONTAINER ANALYSIS",
        )
        if choice is None:
            return
        if choice == "1":
            header("CONTAINER SECURITY // IMAGE ANALYSIS"); print(); container_engine.run("Image Analysis", target); pause()
        elif choice == "2":
            header("CONTAINER SECURITY // RUNTIME ANALYSIS"); print(); container_engine.run("Runtime Analysis", target); pause()
        elif choice == "3":
            header("CONTAINER SECURITY // SBOM"); print(); container_engine.run("SBOM", target); pause()
        elif choice == "4":
            header("CONTAINER SECURITY // EVIDENCE"); print(); container_engine.run("Evidence", target); pause()

def api_page():
    while True:
        choice = menu_page(
            "API SECURITY",
            target,
            [
                ("1", "API Discovery"),
                ("2", "Schema Analysis"),
                ("3", "Authentication Analysis"),
                ("4", "Evidence"),
            ],
            "AUTHORIZED API SECURITY TESTING",
        )

        if choice is None:
            return

        if choice == "1":
            header("API SECURITY // API DISCOVERY")
            print()
            api_engine.run("API Discovery", target)
            pause()

        elif choice == "2":
            header("API SECURITY // SCHEMA ANALYSIS")
            print()
            api_engine.run("Schema Analysis", target)
            pause()

        elif choice == "3":
            header("API SECURITY // AUTHENTICATION ANALYSIS")
            print()
            api_engine.run("Authentication Analysis", target)
            pause()

        elif choice == "4":
            header("API SECURITY // EVIDENCE")
            print()
            api_engine.run("Evidence", target)
            pause()

def database_page():
    while True:
        choice = menu_page(
            "DATABASE SECURITY",
            target,
            [
                ("1", "Discovery"),
                ("2", "Configuration Analysis"),
                ("3", "Evidence"),
            ],
            "AUTHORIZED DATABASE SECURITY",
        )

        if choice is None:
            return

        if choice == "1":
            header("DATABASE SECURITY // DISCOVERY")
            print()
            database_engine.run("Discovery", target)
            pause()

        elif choice == "2":
            header("DATABASE SECURITY // CONFIGURATION ANALYSIS")
            print()
            database_engine.run("Configuration Analysis", target)
            pause()

        elif choice == "3":
            header("DATABASE SECURITY // EVIDENCE")
            print()
            database_engine.run("Evidence", target)
            pause()

def fuzzing_page():
    while True:
        choice = menu_page(
            "FUZZING",
            target,
            [
                ("1", "AFL++"),
                ("2", "Honggfuzz"),
                ("3", "Radamsa"),
                ("4", "Evidence"),
            ],
            "AUTHORIZED FUZZING",
        )
        if choice is None:
            return
        if choice == "1":
            header("FUZZING // AFL++"); print(); fuzzing_engine.run("AFL++", target); pause()
        elif choice == "2":
            header("FUZZING // HONGGFUZZ"); print(); fuzzing_engine.run("Honggfuzz", target); pause()
        elif choice == "3":
            header("FUZZING // RADAMSA"); print(); fuzzing_engine.run("Radamsa", target); pause()
        elif choice == "4":
            header("FUZZING // EVIDENCE"); print(); fuzzing_engine.run("Evidence", target); pause()

def vulnresearch_page():
    while True:
        choice = menu_page(
            "VULNERABILITY RESEARCH",
            target,
            [
                ("1", "Input Analysis"),
                ("2", "Crash Analysis"),
                ("3", "PoC Management"),
                ("4", "Evidence"),
            ],
            "AUTHORIZED VULNERABILITY RESEARCH",
        )
        if choice is None:
            return
        if choice == "1":
            header("VULN RESEARCH // INPUT ANALYSIS"); print(); vulnresearch_engine.run("Input Analysis", target); pause()
        elif choice == "2":
            header("VULN RESEARCH // CRASH ANALYSIS"); print(); vulnresearch_engine.run("Crash Analysis", target); pause()
        elif choice == "3":
            header("VULN RESEARCH // POC MANAGEMENT"); print(); vulnresearch_engine.run("PoC Management", target); pause()
        elif choice == "4":
            header("VULN RESEARCH // EVIDENCE"); print(); vulnresearch_engine.run("Evidence", target); pause()

def dos_page():
    while True:
        choice = menu_page(
            "DOS / STRESS TESTING",
            target,
            [
                ("1", "Local Test"),
                ("2", "Resource Monitoring"),
                ("3", "Evidence"),
            ],
            "AUTHORIZED LAB STRESS TESTING",
        )

        if choice is None:
            return

        if choice == "1":
            header("DOS // LOCAL TEST")
            print()
            dos_engine.run("Local Test", target)
            pause()

        elif choice == "2":
            header("DOS // RESOURCE MONITORING")
            print()
            dos_engine.run("Resource Monitoring", target)
            pause()

        elif choice == "3":
            header("DOS // EVIDENCE")
            print()
            dos_engine.run("Evidence", target)
            pause()

def pcap_page():
    while True:
        choice = menu_page(
            "TRAFFIC / PCAP",
            target,
            [
                ("1", "PCAP Inspection"),
                ("2", "Protocol Analysis"),
                ("3", "Evidence"),
            ],
            "AUTHORIZED TRAFFIC ANALYSIS",
        )

        if choice is None:
            return

        if choice == "1":
            header("TRAFFIC / PCAP // PCAP INSPECTION")
            print()
            pcap_engine.run("PCAP Inspection", target)
            pause()

        elif choice == "2":
            header("TRAFFIC / PCAP // PROTOCOL ANALYSIS")
            print()
            pcap_engine.run("Protocol Analysis", target)
            pause()

        elif choice == "3":
            header("TRAFFIC / PCAP // EVIDENCE")
            print()
            pcap_engine.run("Evidence", target)
            pause()

def dns_page():
    while True:
        choice = menu_page(
            "DNS SECURITY",
            target,
            [
                ("1", "DNS Discovery"),
                ("2", "Record Analysis"),
                ("3", "Evidence"),
            ],
            "AUTHORIZED DNS ANALYSIS",
        )

        if choice is None:
            return

        if choice == "1":
            header("DNS SECURITY // DNS DISCOVERY")
            print()
            dns_engine.run("DNS Discovery", target)
            pause()

        elif choice == "2":
            header("DNS SECURITY // RECORD ANALYSIS")
            print()
            dns_engine.run("Record Analysis", target)
            pause()

        elif choice == "3":
            header("DNS SECURITY // EVIDENCE")
            print()
            dns_engine.run("Evidence", target)
            pause()

def email_page():
    while True:
        choice = menu_page(
            "EMAIL SECURITY",
            target,
            [
                ("1", "Header Analysis"),
                ("2", "SPF / DKIM / DMARC"),
                ("3", "Evidence"),
            ],
            "AUTHORIZED EMAIL SECURITY",
        )

        if choice is None:
            return

        if choice == "1":
            header("EMAIL SECURITY // HEADER ANALYSIS")
            print()
            email_engine.run("Header Analysis", target)
            pause()

        elif choice == "2":
            header("EMAIL SECURITY // SPF / DKIM / DMARC")
            print()
            email_engine.run("SPF / DKIM / DMARC", target)
            pause()

        elif choice == "3":
            header("EMAIL SECURITY // EVIDENCE")
            print()
            email_engine.run("Evidence", target)
            pause()

def bluetooth_page():
    while True:
        choice = menu_page(
            "BLUETOOTH",
            target,
            [
                ("1", "Discovery"),
                ("2", "Device Information"),
                ("3", "Evidence"),
            ],
            "AUTHORIZED BLUETOOTH ANALYSIS",
        )

        if choice is None:
            return

        if choice == "1":
            header("BLUETOOTH // DISCOVERY")
            print()
            bluetooth_engine.run("Discovery", target)
            pause()

        elif choice == "2":
            header("BLUETOOTH // DEVICE INFORMATION")
            print()
            bluetooth_engine.run("Device Information", target)
            pause()

        elif choice == "3":
            header("BLUETOOTH // EVIDENCE")
            print()
            bluetooth_engine.run("Evidence", target)
            pause()

def rfid_page():
    while True:
        choice = menu_page(
            "RFID / NFC",
            target,
            [
                ("1", "Hardware Inventory"),
                ("2", "Tag Analysis"),
                ("3", "Evidence"),
            ],
            "AUTHORIZED RFID / NFC ANALYSIS",
        )

        if choice is None:
            return

        if choice == "1":
            header("RFID / NFC // HARDWARE INVENTORY")
            print()
            rfid_engine.run("Hardware Inventory", target)
            pause()

        elif choice == "2":
            header("RFID / NFC // TAG ANALYSIS")
            print()
            rfid_engine.run("Tag Analysis", target)
            pause()

        elif choice == "3":
            header("RFID / NFC // EVIDENCE")
            print()
            rfid_engine.run("Evidence", target)
            pause()

def sdr_page():
    while True:
        choice = menu_page(
            "SDR / RADIO",
            target,
            [
                ("1", "Radio Inventory"),
                ("2", "Device Detection"),
                ("3", "Evidence"),
            ],
            "AUTHORIZED SDR / RADIO ANALYSIS",
        )
        if choice is None:
            return
        if choice == "1":
            header("SDR / RADIO // RADIO INVENTORY"); print(); sdr_engine.run("Radio Inventory", target); pause()
        elif choice == "2":
            header("SDR / RADIO // DEVICE DETECTION"); print(); sdr_engine.run("Device Detection", target); pause()
        elif choice == "3":
            header("SDR / RADIO // EVIDENCE"); print(); sdr_engine.run("Evidence", target); pause()

def hardware_page():
    while True:
        choice = menu_page(
            "HARDWARE / IOT",
            target,
            [
                ("1", "USB Inventory"),
                ("2", "Device Analysis"),
                ("3", "Evidence"),
            ],
            "AUTHORIZED HARDWARE / IOT ANALYSIS",
        )

        if choice is None:
            return

        if choice == "1":
            header("HARDWARE / IOT // USB INVENTORY")
            print()
            hardware_engine.run("USB Inventory", target)
            pause()

        elif choice == "2":
            header("HARDWARE / IOT // DEVICE ANALYSIS")
            print()
            hardware_engine.run("Device Analysis", target)
            pause()

        elif choice == "3":
            header("HARDWARE / IOT // EVIDENCE")
            print()
            hardware_engine.run("Evidence", target)
            pause()

def stego_page():
    while True:
        choice = menu_page(
            "STEGANOGRAPHY",
            target,
            [
                ("1", "Image Analysis"),
                ("2", "File Analysis"),
                ("3", "Evidence"),
            ],
            "AUTHORIZED STEGANOGRAPHY ANALYSIS",
        )

        if choice is None:
            return

        if choice == "1":
            header("STEGANOGRAPHY // IMAGE ANALYSIS")
            print()
            stego_engine.run("Image Analysis", target)
            pause()

        elif choice == "2":
            header("STEGANOGRAPHY // FILE ANALYSIS")
            print()
            stego_engine.run("File Analysis", target)
            pause()

        elif choice == "3":
            header("STEGANOGRAPHY // EVIDENCE")
            print()
            stego_engine.run("Evidence", target)
            pause()

def tls_page():
    while True:
        choice = menu_page(
            "CERTIFICATE / TLS",
            target,
            [
                ("1", "Certificate"),
                ("2", "TLS Configuration"),
                ("3", "Evidence"),
            ],
            "AUTHORIZED TLS ANALYSIS",
        )

        if choice is None:
            return

        if choice == "1":
            header("CERTIFICATE / TLS // CERTIFICATE")
            print()
            tls_engine.run("Certificate", target)
            pause()

        elif choice == "2":
            header("CERTIFICATE / TLS // TLS CONFIGURATION")
            print()
            tls_engine.run("TLS Configuration", target)
            pause()

        elif choice == "3":
            header("CERTIFICATE / TLS // EVIDENCE")
            print()
            tls_engine.run("Evidence", target)
            pause()

def threat_page():
    while True:
        choice = menu_page(
            "THREAT INTELLIGENCE",
            target,
            [
                ("1", "IOC Analysis"),
                ("2", "Reputation"),
                ("3", "Evidence"),
            ],
            "AUTHORIZED THREAT INTELLIGENCE",
        )

        if choice is None:
            return

        if choice == "1":
            header("THREAT INTELLIGENCE // IOC ANALYSIS")
            print()
            threat_engine.run("IOC Analysis", target)
            pause()

        elif choice == "2":
            header("THREAT INTELLIGENCE // REPUTATION")
            print()
            threat_engine.run("Reputation", target)
            pause()

        elif choice == "3":
            header("THREAT INTELLIGENCE // EVIDENCE")
            print()
            threat_engine.run("Evidence", target)
            pause()

def source_page():
    while True:
        choice = menu_page(
            "SOURCE CODE ANALYSIS",
            target,
            [
                ("1", "Static Analysis"),
                ("2", "Secrets Detection"),
                ("3", "Evidence"),
            ],
            "AUTHORIZED SOURCE ANALYSIS",
        )

        if choice is None:
            return

        if choice == "1":
            header("SOURCE CODE ANALYSIS // STATIC ANALYSIS")
            print()
            source_engine.run("Static Analysis", target)
            pause()

        elif choice == "2":
            header("SOURCE CODE ANALYSIS // SECRETS DETECTION")
            print()
            source_engine.run("Secrets Detection", target)
            pause()

        elif choice == "3":
            header("SOURCE CODE ANALYSIS // EVIDENCE")
            print()
            source_engine.run("Evidence", target)
            pause()

def supply_page():
    while True:
        choice = menu_page(
            "SUPPLY CHAIN SECURITY",
            target,
            [
                ("1", "Dependency Analysis"),
                ("2", "SBOM"),
                ("3", "Evidence"),
            ],
            "AUTHORIZED SUPPLY CHAIN ANALYSIS",
        )

        if choice is None:
            return

        if choice == "1":
            header("SUPPLY CHAIN SECURITY // DEPENDENCY ANALYSIS")
            print()
            supply_engine.run("Dependency Analysis", target)
            pause()

        elif choice == "2":
            header("SUPPLY CHAIN SECURITY // SBOM")
            print()
            supply_engine.run("SBOM", target)
            pause()

        elif choice == "3":
            header("SUPPLY CHAIN SECURITY // EVIDENCE")
            print()
            supply_engine.run("Evidence", target)
            pause()

def incident_page():
    while True:
        choice = menu_page(
            "INCIDENT RESPONSE",
            target,
            [
                ("1", "Triage"),
                ("2", "Timeline"),
                ("3", "Artifact Collection"),
                ("4", "Evidence"),
            ],
            "AUTHORIZED INCIDENT RESPONSE",
        )

        if choice is None:
            return

        if choice == "1":
            header("INCIDENT RESPONSE // TRIAGE")
            print()
            incident_engine.run("Triage", target)
            pause()

        elif choice == "2":
            header("INCIDENT RESPONSE // TIMELINE")
            print()
            incident_engine.run("Timeline", target)
            pause()

        elif choice == "3":
            header("INCIDENT RESPONSE // ARTIFACT COLLECTION")
            print()
            incident_engine.run("Artifact Collection", target)
            pause()

        elif choice == "4":
            header("INCIDENT RESPONSE // EVIDENCE")
            print()
            incident_engine.run("Evidence", target)
            pause()

def yara_page():
    while True:
        choice = menu_page(
            "YARA / IOC ANALYSIS",
            target,
            [
                ("1", "YARA"),
                ("2", "IOC Matching"),
                ("3", "Evidence"),
            ],
            "AUTHORIZED IOC ANALYSIS",
        )

        if choice is None:
            return

        if choice == "1":
            header("YARA / IOC ANALYSIS // YARA")
            print()
            yara_engine.run("YARA", target)
            pause()

        elif choice == "2":
            header("YARA / IOC ANALYSIS // IOC MATCHING")
            print()
            yara_engine.run("IOC Matching", target)
            pause()

        elif choice == "3":
            header("YARA / IOC ANALYSIS // EVIDENCE")
            print()
            yara_engine.run("Evidence", target)
            pause()

def automation_page():
    while True:
        choice = menu_page(
            "AUTOMATION",
            target,
            [
                ("1", "Task Runner"),
                ("2", "Evidence"),
            ],
            "AUTHORIZED AUTOMATION",
        )

        if choice is None:
            return

        if choice == "1":
            header("AUTOMATION // TASK RUNNER")
            print()
            automation_engine.run("Task Runner", target)
            pause()

        elif choice == "2":
            header("AUTOMATION // EVIDENCE")
            print()
            automation_engine.run("Evidence", target)
            pause()

def orchestration_page():
    while True:
        choice = menu_page(
            "TOOL ORCHESTRATION",
            target,
            [
                ("1", "Detect"),
                ("2", "Capability Matrix"),
                ("3", "Evidence"),
            ],
            "AUTHORIZED TOOL ORCHESTRATION",
        )

        if choice is None:
            return

        if choice == "1":
            header("TOOL ORCHESTRATION // DETECT")
            print()
            orchestration_engine.run("Detect", target)
            pause()

        elif choice == "2":
            header("TOOL ORCHESTRATION // CAPABILITY MATRIX")
            print()
            orchestration_engine.run("Capability Matrix", target)
            pause()

        elif choice == "3":
            header("TOOL ORCHESTRATION // EVIDENCE")
            print()
            orchestration_engine.run("Evidence", target)
            pause()

def evidence_page():
    while True:
        choice = menu_page(
            "EVIDENCE",
            target,
            [
                ("1", "Browse"),
                ("2", "Inspect"),
                ("3", "Summary"),
            ],
            "EVIDENCE MANAGEMENT",
        )

        if choice is None:
            return

        if choice == "1":
            header("EVIDENCE // BROWSE")
            print()
            evidence_engine.run("Browse", target)
            pause()

        elif choice == "2":
            header("EVIDENCE // INSPECT")
            print()
            evidence_engine.run("Inspect", target)
            pause()

        elif choice == "3":
            header("EVIDENCE // SUMMARY")
            print()
            evidence_engine.run("Summary", target)
            pause()

def reports_page():
    while True:
        choice = menu_page(
            "REPORTS",
            target,
            [
                ("1", "List Reports"),
                ("2", "Generate Index"),
                ("3", "Inspect"),
                ("4", "Evidence"),
            ],
            "REPORT MANAGEMENT",
        )

        if choice is None:
            return

        if choice == "1":
            header("REPORTS // LIST REPORTS")
            print()
            reports_engine.run("List Reports", target)
            pause()

        elif choice == "2":
            header("REPORTS // GENERATE INDEX")
            print()
            reports_engine.run("Generate Index", target)
            pause()

        elif choice == "3":
            header("REPORTS // INSPECT")
            print()
            reports_engine.run("Inspect", target)
            pause()

        elif choice == "4":
            header("REPORTS // EVIDENCE")
            print()
            reports_engine.run("Evidence", target)
            pause()

def inventory_page():
    while True:
        choice = menu_page(
            "TOOL INVENTORY",
            target,
            [
                ("1", "Status"),
                ("2", "Verify"),
                ("3", "Evidence"),
            ],
            "ALD TOOL INVENTORY",
        )

        if choice is None:
            return

        if choice == "1":
            header("TOOL INVENTORY // STATUS")
            print()
            inventory_engine.run("Status", target)
            pause()

        elif choice == "2":
            header("TOOL INVENTORY // VERIFY")
            print()
            inventory_engine.run("Verify", target)
            pause()

        elif choice == "3":
            header("TOOL INVENTORY // EVIDENCE")
            print()
            inventory_engine.run("Evidence", target)
            pause()

def doctor_page():
    header("DOCTOR")
    print()
    doctor_engine.run("Doctor", target)
    pause()

def intel_page():
    header("ALD INTEL")
    print()
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(" ALD // INTELLIGENCE PLAN")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print()
    print(f"[ALD] Target: {target}")

    report_root = Path("ald/reports")
    report_files = 0

    if report_root.exists():
        report_files = sum(
            1 for p in report_root.rglob("*")
            if p.is_file()
        )

    print(f"[ALD] Evidence files: {report_files}")
    print()
    print("[ALD] Available intelligence sources")
    print("-" * 54)
    print("[+] Target context")
    print("[+] Local evidence inventory")
    print("[+] Tool availability")
    print("[+] Historical report artifacts")
    print()
    print("[ALD] Intelligence plan generated.")
    pause()

def matrix_page():
    header("TOOL MATRIX")
    print()
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(" ALD // TOOL CAPABILITY MATRIX")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print()

    groups = {
        "RECON": ["nmap", "arp", "ip", "ss", "masscan"],
        "WEB": ["curl", "wget", "whatweb", "nikto"],
        "FORENSICS": ["file", "exiftool", "strings", "tshark", "yara"],
        "MOBILE": ["adb"],
        "CONTAINERS": ["docker", "podman"],
        "FUZZING": ["afl-fuzz", "honggfuzz", "radamsa"],
        "SOURCE": ["semgrep", "cppcheck", "shellcheck"],
        "CRYPTO / TLS": ["openssl", "dig"],
        "WIRELESS": ["bluetoothctl"],
        "DATABASE": ["sqlite3", "psql"],
    }

    import shutil

    total = 0
    available = 0

    for category, tools in groups.items():
        found = sum(1 for tool in tools if shutil.which(tool))
        total += len(tools)
        available += found

        print(f"[{category}] {found}/{len(tools)}")
        for tool in tools:
            path = shutil.which(tool)
            if path:
                print(f"  [+] {tool:<15} {path}")
            else:
                print(f"  [-] {tool:<15} missing")
        print()

    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"[ALD] Capability coverage: {available}/{total}")
    print("[ALD] Tool Matrix generated.")
    pause()

def menu():
    global target

    while True:
        choice = menu_page(
            "A L D // E L L I O T",
            target,
            [
                ("1", "Target"),
                ("2", "Reconnaissance"),
                ("3", "Web Security"),
                ("4", "Network Security"),
                ("5", "Wireless"),
                ("6", "Passwords"),
                ("7", "Hash Analysis"),
                ("8", "Cryptography"),
                ("9", "Encryption / Decryption"),
                ("10", "OSINT"),
                ("11", "Social Engineering"),
                ("12", "Active Directory"),
                ("13", "Windows Security"),
                ("14", "Linux Security"),
                ("15", "Privilege Escalation"),
                ("16", "Exploitation"),
                ("17", "Reverse Engineering"),
                ("18", "Binary Exploitation"),
                ("19", "Malware Analysis"),
                ("20", "Forensics"),
                ("21", "Memory Forensics"),
                ("22", "Mobile Security"),
                ("23", "Cloud Security"),
                ("24", "Container Security"),
                ("25", "API Security"),
                ("26", "Database Security"),
                ("27", "Fuzzing"),
                ("28", "Vulnerability Research"),
                ("29", "DoS / Stress Testing"),
                ("30", "Traffic / PCAP"),
                ("31", "DNS Security"),
                ("32", "Email Security"),
                ("33", "Bluetooth"),
                ("34", "RFID / NFC"),
                ("35", "SDR / Radio"),
                ("36", "Hardware / IoT"),
                ("37", "Steganography"),
                ("38", "Certificate / TLS"),
                ("39", "Threat Intelligence"),
                ("40", "Source Code Analysis"),
                ("41", "Supply Chain Security"),
                ("42", "Incident Response"),
                ("43", "YARA / IOC Analysis"),
                ("44", "Automation"),
                ("45", "Tool Orchestration"),
                ("46", "Evidence"),
                ("47", "Reports"),
                ("48", "Tool Inventory"),
                ("49", "Doctor"),
                ("50", "ALD Intel"),
                ("51", "Tool Matrix"),
            ],
            "SECURITY OPERATIONS CORE",
        )

        if choice is None or choice == "0":
            return

        pages = {
            "1": target_page,
            "2": recon_page,
            "3": web_page,
            "4": network_page,
            "5": wireless_page,
            "6": passwords_page,
            "7": hash_page,
            "8": crypto_page,
            "9": encryption_page,
            "10": osint_page,
            "17": reverse_page,
            "20": forensics_page,
            "21": memory_page,
            "22": mobile_page,
            "23": cloud_page,
            "24": container_page,
            "25": api_page,
            "26": database_page,
            "27": fuzzing_page,
            "28": vulnresearch_page,
            "29": dos_page,
            "30": pcap_page,
            "31": dns_page,
            "32": email_page,
            "33": bluetooth_page,
            "34": rfid_page,
            "35": sdr_page,
            "36": hardware_page,
            "37": stego_page,
            "38": tls_page,
            "39": threat_page,
            "40": source_page,
            "41": supply_page,
            "42": incident_page,
            "43": yara_page,
            "44": automation_page,
            "45": orchestration_page,
            "46": evidence_page,
            "47": reports_page,
            "48": inventory_page,
            "49": doctor_page,
            "50": intel_page,
            "51": matrix_page,
        }

        page = pages.get(choice)

        if page:
            try:
                page()
            except KeyboardInterrupt:
                print("\n[ALD] Session interrupted.")
                return
        else:
            info_page(
                "ALD // MODULE",
                target,
                [f"{YELLOW}[ALD]{RESET} Module registered."],
            )


if __name__ == "__main__":
    try:
        if len(sys.argv) > 1 and sys.argv[1] in {"update", "install"}:
            raise SystemExit(update_engine.cli())
        else:
            menu()
    except KeyboardInterrupt:
        print("\n[ALD] Session interrupted.")
