#!/usr/bin/env python3

import json
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"

RED = "\033[1;31m"
YELLOW = "\033[1;33m"
GREEN = "\033[1;32m"
CYAN = "\033[1;36m"
RESET = "\033[0m"


def tool(name):
    return shutil.which(name)


def normalize_url(target):
    target = target.strip()

    if "://" not in target:
        return "http://" + target

    return target


def safe_name(value):
    return "".join(
        c if c.isalnum() or c in "._-" else "_"
        for c in value
    )


def evidence_dir(target, module):
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    directory = (
        REPORTS
        / f"{stamp}_{safe_name(module)}"
    )

    directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    (directory / "target.txt").write_text(
        target
    )

    (directory / "module.txt").write_text(
        module
    )

    (directory / "timestamp.txt").write_text(
        stamp
    )

    return directory


def authorized(target):
    print()
    print(f"{YELLOW}[ALD SCOPE CONTROL]{RESET}")
    print(f"Target: {target}")
    print()
    answer = input(
        "Do you have explicit authorization to assess this target? [y/N]: "
    ).strip().lower()

    return answer == "y"


def execute(command, output_file, evidence):
    print()
    print(
        f"{CYAN}[ALD ENGINE]{RESET} "
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

        (evidence / output_file).write_text(
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
            f"\n{GREEN}[+] Evidence:{RESET} "
            f"{evidence}"
        )

        return output

    except subprocess.TimeoutExpired:
        msg = "Command timed out after 300 seconds."

        (evidence / output_file).write_text(msg)

        print(f"{RED}[-] {msg}{RESET}")

    except Exception as exc:
        msg = f"Execution error: {exc}"

        (evidence / output_file).write_text(msg)

        print(f"{RED}[-] {msg}{RESET}")


# ============================================================
# HTTP DISCOVERY
# ============================================================

def http_discovery(target):
    url = normalize_url(target)

    if not authorized(target):
        return

    evidence = evidence_dir(
        target,
        "web_http_discovery",
    )

    if tool("httpx"):
        execute(
            [
                "httpx",
                "-silent",
                "-u",
                url,
                "-status-code",
                "-title",
                "-tech-detect",
                "-server",
                "-web-server",
            ],
            "httpx.txt",
            evidence,
        )
        return

    if tool("curl"):
        execute(
            [
                "curl",
                "-I",
                "--max-time",
                "20",
                url,
            ],
            "headers.txt",
            evidence,
        )
        return

    print(
        f"{RED}[-] Neither httpx nor curl is installed.{RESET}"
    )


# ============================================================
# TECHNOLOGY ANALYSIS
# ============================================================

def technology_analysis(target):
    url = normalize_url(target)

    if not authorized(target):
        return

    evidence = evidence_dir(
        target,
        "web_technology_analysis",
    )

    if tool("whatweb"):
        execute(
            [
                "whatweb",
                "--color=never",
                url,
            ],
            "whatweb.txt",
            evidence,
        )
        return

    if tool("httpx"):
        execute(
            [
                "httpx",
                "-silent",
                "-u",
                url,
                "-title",
                "-tech-detect",
                "-web-server",
                "-status-code",
            ],
            "httpx.txt",
            evidence,
        )
        return

    if tool("curl"):
        execute(
            [
                "curl",
                "-I",
                "--max-time",
                "20",
                url,
            ],
            "headers.txt",
            evidence,
        )
        return

    print(
        f"{RED}[-] No HTTP technology tool available.{RESET}"
    )


# ============================================================
# ENDPOINT ENUMERATION
# ============================================================

def endpoint_enumeration(target):
    url = normalize_url(target).rstrip("/")

    if not authorized(target):
        return

    evidence = evidence_dir(
        target,
        "web_endpoint_enumeration",
    )

    wordlists = [
        "/usr/share/wordlists/dirb/common.txt",
        "/usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt",
    ]

    wordlist = next(
        (
            path
            for path in wordlists
            if Path(path).exists()
        ),
        None,
    )

    if tool("ffuf") and wordlist:
        execute(
            [
                "ffuf",
                "-u",
                url + "/FUZZ",
                "-w",
                wordlist,
                "-of",
                "json",
                "-o",
                str(evidence / "ffuf.json"),
                "-s",
            ],
            "ffuf.txt",
            evidence,
        )
        return

    if tool("feroxbuster"):
        execute(
            [
                "feroxbuster",
                "-u",
                url,
                "--no-state",
            ],
            "feroxbuster.txt",
            evidence,
        )
        return

    if tool("gobuster") and wordlist:
        execute(
            [
                "gobuster",
                "dir",
                "-u",
                url,
                "-w",
                wordlist,
            ],
            "gobuster.txt",
            evidence,
        )
        return

    print(
        f"{RED}[-] No endpoint-enumeration engine is available.{RESET}"
    )


# ============================================================
# API SECURITY
# ============================================================

def api_security(target):
    url = normalize_url(target)

    if not authorized(target):
        return

    evidence = evidence_dir(
        target,
        "web_api_security",
    )

    print(
        f"{YELLOW}[ALD] API discovery / passive assessment{RESET}"
    )
    print()

    # Detect likely API documentation/resources without
    # attempting authentication bypass or exploitation.
    paths = [
        "/openapi.json",
        "/swagger.json",
        "/api",
        "/api/",
        "/docs",
        "/swagger",
        "/graphql",
    ]

    results = []

    for path in paths:
        endpoint = url.rstrip("/") + path

        if tool("curl"):
            try:
                result = subprocess.run(
                    [
                        "curl",
                        "-k",
                        "-sS",
                        "-o",
                        "/dev/null",
                        "-w",
                        "%{http_code} %{content_type}",
                        "--max-time",
                        "10",
                        endpoint,
                    ],
                    text=True,
                    capture_output=True,
                    timeout=20,
                )

                value = result.stdout.strip()

                results.append(
                    {
                        "path": path,
                        "result": value,
                    }
                )

                print(
                    f"  {path:<20} {value}"
                )

            except Exception as exc:
                results.append(
                    {
                        "path": path,
                        "error": str(exc),
                    }
                )

    (evidence / "api_discovery.json").write_text(
        json.dumps(
            results,
            indent=2,
        )
    )

    print()
    print(
        f"{GREEN}[+] API evidence:{RESET} "
        f"{evidence / 'api_discovery.json'}"
    )


# ============================================================
# VULNERABILITY ANALYSIS
# ============================================================

def vulnerability_analysis(target):
    url = normalize_url(target)

    if not authorized(target):
        return

    evidence = evidence_dir(
        target,
        "web_vulnerability_analysis",
    )

    if tool("nuclei"):
        execute(
            [
                "nuclei",
                "-u",
                url,
                "-o",
                str(evidence / "nuclei-findings.txt"),
            ],
            "nuclei.txt",
            evidence,
        )
        return

    if tool("nikto"):
        execute(
            [
                "nikto",
                "-h",
                url,
            ],
            "nikto.txt",
            evidence,
        )
        return

    print(
        f"{RED}[-] Install nuclei or nikto "
        f"to enable vulnerability analysis.{RESET}"
    )


# ============================================================
# TLS / CERTIFICATES
# ============================================================

def tls_analysis(target):
    url = normalize_url(target)

    if not authorized(target):
        return

    parsed = urlparse(url)

    host = parsed.hostname

    if not host:
        print(
            f"{RED}[-] Could not determine hostname.{RESET}"
        )
        return

    evidence = evidence_dir(
        target,
        "web_tls_analysis",
    )

    if tool("openssl"):
        execute(
            [
                "openssl",
                "s_client",
                "-connect",
                f"{host}:443",
                "-servername",
                host,
                "-showcerts",
            ],
            "openssl.txt",
            evidence,
        )
        return

    if tool("nmap"):
        execute(
            [
                "nmap",
                "-p",
                "443",
                "--script",
                "ssl-cert,ssl-enum-ciphers",
                host,
            ],
            "nmap_tls.txt",
            evidence,
        )
        return

    print(
        f"{RED}[-] openssl or nmap is required.{RESET}"
    )


# ============================================================
# PUBLIC DISPATCH
# ============================================================

def run(module, target):
    modules = {
        "HTTP Discovery": http_discovery,
        "Endpoint Enumeration": endpoint_enumeration,
        "Technology Analysis": technology_analysis,
        "API Security": api_security,
        "Vulnerability Analysis": vulnerability_analysis,
        "TLS / Certificates": tls_analysis,
    }

    function = modules.get(module)

    if not function:
        print(
            f"{RED}[-] Web module not implemented: "
            f"{module}{RESET}"
        )
        return

    function(target)
