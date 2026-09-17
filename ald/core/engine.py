#!/usr/bin/env python3

import shutil
import subprocess
from datetime import datetime
from pathlib import Path

RED = "\033[1;31m"
YELLOW = "\033[1;33m"
GREEN = "\033[1;32m"
CYAN = "\033[1;36m"
RESET = "\033[0m"


ROOT = Path(__file__).resolve().parents[2]
REPORTS = ROOT / "ald" / "reports"


def slug(value):
    return "".join(
        c if c.isalnum() or c in "._-" else "_"
        for c in value
    )


def tool_exists(name):
    return shutil.which(name) is not None


def tool_status(names):
    return {
        name: shutil.which(name)
        for name in names
    }


def confirm_scope(target):
    print()
    print(f"{YELLOW}[ALD SCOPE CONTROL]{RESET}")
    print(f"Target: {target}")
    print()
    answer = input(
        "Do you have explicit authorization to assess this target? [y/N]: "
    ).strip().lower()
    return answer == "y"


def start_evidence(target, module):
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    directory = REPORTS / f"{stamp}_{slug(module)}"
    directory.mkdir(parents=True, exist_ok=True)

    (directory / "target.txt").write_text(str(target))
    (directory / "module.txt").write_text(str(module))
    (directory / "timestamp.txt").write_text(stamp)

    return directory


def execute(
    target,
    module,
    command,
    output_name="output.txt",
    requires_scope=True,
):
    if requires_scope and not confirm_scope(target):
        print(f"\n{RED}[-] Scope authorization not confirmed.{RESET}")
        return None

    binary = command[0]

    if not tool_exists(binary):
        print(
            f"\n{RED}[-] Tool not installed: {binary}{RESET}"
        )
        print(
            f"{YELLOW}Install it first, then rerun the module.{RESET}"
        )
        return None

    evidence = start_evidence(target, module)
    output_file = evidence / output_name

    print()
    print(f"{CYAN}[ALD ENGINE]{RESET}")
    print(f"Tool     : {binary}")
    print(f"Target   : {target}")
    print(f"Evidence : {evidence}")
    print()
    print(f"{YELLOW}$ {' '.join(command)}{RESET}")
    print()

    try:
        result = subprocess.run(
            command,
            text=True,
            capture_output=True,
            timeout=300,
        )

        combined = result.stdout + result.stderr
        output_file.write_text(combined, errors="replace")

        print(combined)

        (evidence / "command.txt").write_text(
            " ".join(command)
        )

        (evidence / "exit_code.txt").write_text(
            str(result.returncode)
        )

        print()
        print(
            f"{GREEN}[+] Evidence saved:{RESET} "
            f"{output_file}"
        )

        return evidence

    except subprocess.TimeoutExpired:
        output_file.write_text(
            "ALD: command timed out after 300 seconds."
        )

        print(
            f"\n{RED}[-] Tool execution timed out.{RESET}"
        )

        return evidence

    except Exception as exc:
        output_file.write_text(
            f"ALD execution error:\n{exc}"
        )

        print(
            f"\n{RED}[ALD ERROR] {exc}{RESET}"
        )

        return evidence


# ============================================================
# WEB
# ============================================================

def web_http_discovery(target):
    url = target

    if "://" not in url:
        url = "http://" + url

    if tool_exists("httpx"):
        return execute(
            target,
            "web_http_discovery",
            [
                "httpx",
                "-silent",
                "-title",
                "-status-code",
                "-tech-detect",
                "-u",
                url,
            ],
            "httpx.txt",
        )

    if tool_exists("curl"):
        return execute(
            target,
            "web_http_discovery",
            [
                "curl",
                "-I",
                "--max-time",
                "20",
                url,
            ],
            "headers.txt",
        )

    print(f"{RED}[-] Neither httpx nor curl is installed.{RESET}")


def web_vulnerability(target):
    url = target

    if "://" not in url:
        url = "http://" + url

    if tool_exists("nuclei"):
        return execute(
            target,
            "web_vulnerability_analysis",
            [
                "nuclei",
                "-u",
                url,
                "-o",
                "findings.txt",
            ],
            "nuclei.txt",
        )

    if tool_exists("nikto"):
        return execute(
            target,
            "web_vulnerability_analysis",
            [
                "nikto",
                "-h",
                url,
            ],
            "nikto.txt",
        )

    print(
        f"{RED}[-] No supported web vulnerability scanner installed.{RESET}"
    )


def web_endpoint_enum(target):
    url = target

    if "://" not in url:
        url = "http://" + url

    if tool_exists("ffuf"):
        evidence = start_evidence(target, "web_endpoint_enumeration")

        wordlist = "/usr/share/wordlists/dirb/common.txt"

        if not Path(wordlist).exists():
            print(
                f"{RED}[-] Wordlist not found: {wordlist}{RESET}"
            )
            return None

        command = [
            "ffuf",
            "-u",
            url.rstrip("/") + "/FUZZ",
            "-w",
            wordlist,
            "-of",
            "json",
            "-o",
            str(evidence / "ffuf.json"),
        ]

        if not confirm_scope(target):
            return None

        print(f"{YELLOW}$ {' '.join(command)}{RESET}")

        try:
            result = subprocess.run(
                command,
                text=True,
                capture_output=True,
                timeout=300,
            )

            (evidence / "ffuf.txt").write_text(
                result.stdout + result.stderr
            )

            print(result.stdout)
            print(
                f"\n{GREEN}[+] Evidence saved:{RESET} {evidence}"
            )

            return evidence

        except Exception as exc:
            print(f"{RED}[ALD ERROR] {exc}{RESET}")

    else:
        print(f"{RED}[-] ffuf is not installed.{RESET}")


# ============================================================
# NETWORK
# ============================================================

def network_discovery(target):
    if tool_exists("nmap"):
        return execute(
            target,
            "network_discovery",
            [
                "nmap",
                "-sV",
                "--top-ports",
                "1000",
                target,
            ],
            "nmap.txt",
        )

    print(f"{RED}[-] nmap is not installed.{RESET}")


def network_quick(target):
    if tool_exists("nmap"):
        return execute(
            target,
            "network_quick_scan",
            [
                "nmap",
                "-T3",
                "--top-ports",
                "100",
                target,
            ],
            "nmap_quick.txt",
        )

    print(f"{RED}[-] nmap is not installed.{RESET}")


# ============================================================
# OSINT
# ============================================================

def osint_username(target):
    if tool_exists("maigret"):
        return execute(
            target,
            "osint_username",
            [
                "maigret",
                target,
            ],
            "maigret.txt",
        )

    if tool_exists("sherlock"):
        return execute(
            target,
            "osint_username",
            [
                "sherlock",
                target,
            ],
            "sherlock.txt",
        )

    print(
        f"{RED}[-] Neither maigret nor sherlock is installed.{RESET}"
    )


def osint_domain(target):
    if tool_exists("subfinder"):
        return execute(
            target,
            "osint_domain",
            [
                "subfinder",
                "-d",
                target,
                "-silent",
            ],
            "subdomains.txt",
        )

    if tool_exists("amass"):
        return execute(
            target,
            "osint_domain",
            [
                "amass",
                "enum",
                "-passive",
                "-d",
                target,
            ],
            "amass.txt",
        )

    print(
        f"{RED}[-] Neither subfinder nor amass is installed.{RESET}"
    )


# ============================================================
# FILE / BINARY
# ============================================================

def file_analysis(target):
    if tool_exists("file"):
        return execute(
            target,
            "file_analysis",
            [
                "file",
                target,
            ],
            "file.txt",
            requires_scope=False,
        )

    print(f"{RED}[-] file is not installed.{RESET}")


# ============================================================
# HASH
# ============================================================

def hash_identify(value):
    if tool_exists("hashid"):
        return execute(
            value,
            "hash_identification",
            [
                "hashid",
                value,
            ],
            "hashid.txt",
            requires_scope=False,
        )

    print(f"{RED}[-] hashid is not installed.{RESET}")


# ============================================================
# DISPATCH
# ============================================================

def dispatch(category, module, target):
    category = category.upper()
    module = module.lower()

    if not target:
        print(f"{RED}[-] No target is configured.{RESET}")
        return None

    if category == "WEB SECURITY":
        if module == "http discovery":
            return web_http_discovery(target)

        if module == "endpoint enumeration":
            return web_endpoint_enum(target)

        if module == "vulnerability analysis":
            return web_vulnerability(target)

    if category == "NETWORK SECURITY":
        if module == "network discovery":
            return network_discovery(target)

        if module == "service analysis":
            return network_discovery(target)

    if category == "OSINT":
        if module == "username discovery":
            return osint_username(target)

        if module == "domain intelligence":
            return osint_domain(target)

    if category == "FILE ANALYSIS":
        return file_analysis(target)

    return None
