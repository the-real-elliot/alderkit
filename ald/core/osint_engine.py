#!/usr/bin/env python3

import json
import re
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORTS = ROOT / "ald" / "reports"

RED = "\033[1;31m"
YELLOW = "\033[1;33m"
GREEN = "\033[1;32m"
CYAN = "\033[1;36m"
RESET = "\033[0m"


def tool(name):
    return shutil.which(name)


def safe_name(value):
    return "".join(
        c if c.isalnum() or c in "._-" else "_"
        for c in str(value)
    )


def evidence_dir(target, module):
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    directory = (
        REPORTS /
        f"{stamp}_{safe_name(module)}"
    )

    directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    (directory / "target.txt").write_text(
        str(target)
    )
    (directory / "module.txt").write_text(
        str(module)
    )
    (directory / "timestamp.txt").write_text(
        stamp
    )

    return directory


def authorized(target):
    print()
    print(f"{YELLOW}[ALD SCOPE CONTROL]{RESET}")
    print(f"Identifier: {target}")
    print()

    answer = input(
        "Do you have authorization to perform this public-source assessment? [y/N]: "
    ).strip().lower()

    return answer == "y"


def execute(command, output_name, evidence):
    print()
    print(
        f"{CYAN}[ALD OSINT ENGINE]{RESET} "
        f"$ {' '.join(command)}"
    )
    print()

    try:
        result = subprocess.run(
            command,
            text=True,
            capture_output=True,
            timeout=300,
        )

        output = (
            result.stdout +
            result.stderr
        )

        (evidence / output_name).write_text(
            output,
            errors="replace",
        )

        (evidence / "command.txt").write_text(
            " ".join(command)
        )

        (evidence / "exit_code.txt").write_text(
            str(result.returncode)
        )

        print(output)

        print(
            f"\n{GREEN}[+] Evidence saved:{RESET} "
            f"{evidence}"
        )

        return evidence

    except subprocess.TimeoutExpired:
        message = "Command timed out after 300 seconds."

        (evidence / output_name).write_text(message)

        print(
            f"{RED}[-] {message}{RESET}"
        )

        return evidence

    except Exception as exc:
        message = f"Execution error: {exc}"

        (evidence / output_name).write_text(message)

        print(
            f"{RED}[-] {message}{RESET}"
        )

        return evidence


# ============================================================
# USERNAME
# ============================================================

def username(target):
    if not authorized(target):
        return None

    evidence = evidence_dir(
        target,
        "osint_username",
    )

    if tool("maigret"):
        return execute(
            [
                "maigret",
                target,
            ],
            "maigret.txt",
            evidence,
        )

    if tool("sherlock"):
        return execute(
            [
                "sherlock",
                target,
                "--print-found",
            ],
            "sherlock.txt",
            evidence,
        )

    print(
        f"{RED}[-] No username OSINT backend installed.{RESET}"
    )
    print(
        "Install: maigret or sherlock"
    )


# ============================================================
# DOMAIN
# ============================================================

def domain(target):
    if not authorized(target):
        return None

    evidence = evidence_dir(
        target,
        "osint_domain",
    )

    if tool("subfinder"):
        return execute(
            [
                "subfinder",
                "-d",
                target,
                "-silent",
            ],
            "subdomains.txt",
            evidence,
        )

    if tool("amass"):
        return execute(
            [
                "amass",
                "enum",
                "-passive",
                "-d",
                target,
            ],
            "amass.txt",
            evidence,
        )

    print(
        f"{RED}[-] No domain OSINT backend installed.{RESET}"
    )


# ============================================================
# DNS
# ============================================================

def dns(target):
    if not authorized(target):
        return None

    evidence = evidence_dir(
        target,
        "osint_dns",
    )

    if tool("dig"):
        return execute(
            [
                "dig",
                target,
                "ANY",
            ],
            "dig.txt",
            evidence,
        )

    if tool("nslookup"):
        return execute(
            [
                "nslookup",
                target,
            ],
            "nslookup.txt",
            evidence,
        )

    print(
        f"{RED}[-] dig/nslookup unavailable.{RESET}"
    )


# ============================================================
# CERTIFICATES
# ============================================================

def certificates(target):
    if not authorized(target):
        return None

    evidence = evidence_dir(
        target,
        "osint_certificates",
    )

    if tool("openssl"):
        output = execute(
            [
                "openssl",
                "s_client",
                "-connect",
                f"{target}:443",
                "-servername",
                target,
            ],
            "certificate.txt",
            evidence,
        )

        return output

    print(
        f"{RED}[-] openssl is not installed.{RESET}"
    )


# ============================================================
# EMAIL ANALYSIS
# ============================================================

def email(target):
    if not authorized(target):
        return None

    evidence = evidence_dir(
        target,
        "osint_email",
    )

    normalized = target.strip().lower()

    result = {
        "input": target,
        "normalized": normalized,
        "valid_basic_format": bool(
            re.fullmatch(
                r"[^@\s]+@[^@\s]+\.[^@\s]+",
                normalized,
            )
        ),
        "domain": (
            normalized.split("@", 1)[1]
            if "@" in normalized
            else None
        ),
    }

    (evidence / "email.json").write_text(
        json.dumps(result, indent=2)
    )

    print(
        json.dumps(result, indent=2)
    )

    print(
        f"\n{GREEN}[+] Evidence saved:{RESET} "
        f"{evidence / 'email.json'}"
    )

    return evidence


# ============================================================
# PHONE NORMALIZATION
# ============================================================

def phone(target):
    if not authorized(target):
        return None

    evidence = evidence_dir(
        target,
        "osint_phone",
    )

    digits = re.sub(
        r"\D",
        "",
        target,
    )

    result = {
        "input": target,
        "normalized_digits": digits,
        "length": len(digits),
    }

    (evidence / "phone.json").write_text(
        json.dumps(result, indent=2)
    )

    print(
        json.dumps(result, indent=2)
    )

    print(
        f"\n{GREEN}[+] Evidence saved:{RESET} "
        f"{evidence / 'phone.json'}"
    )

    return evidence


# ============================================================
# DISPATCH
# ============================================================

def run(module, target):
    modules = {
        "Username Discovery": username,
        "Domain Intelligence": domain,
        "DNS Intelligence": dns,
        "Certificate Intelligence": certificates,
        "Email Intelligence": email,
        "Phone Intelligence": phone,
    }

    function = modules.get(module)

    if function is None:
        print(
            f"{RED}[-] Unknown OSINT module: {module}{RESET}"
        )
        return None

    return function(target)
