#!/usr/bin/env python3

import json
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[2]
REPORTS = ROOT / "ald" / "reports"

RED = "\033[1;31m"
YELLOW = "\033[1;33m"
GREEN = "\033[1;32m"
CYAN = "\033[1;36m"
RESET = "\033[0m"


def tool(name):
    return shutil.which(name)


def normalize_url(target):
    target = str(target).strip()

    if "://" not in target:
        return "http://" + target

    return target


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
    print(f"Target: {target}")
    print()

    answer = input(
        "Do you have explicit authorization to assess this target? [y/N]: "
    ).strip().lower()

    return answer == "y"


def execute(command, output_name, evidence):
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
        msg = "Command timed out after 300 seconds."

        (evidence / output_name).write_text(msg)

        print(f"{RED}[-] {msg}{RESET}")
        return evidence

    except Exception as exc:
        msg = f"Execution error: {exc}"

        (evidence / output_name).write_text(msg)

        print(f"{RED}[-] {msg}{RESET}")
        return evidence


# ============================================================
# HTTP DISCOVERY
# ============================================================

def http_discovery(target):
    if not authorized(target):
        return None

    url = normalize_url(target)
    evidence = evidence_dir(
        target,
        "web_http_discovery",
    )

    if tool("httpx"):
        return execute(
            [
                "httpx",
                "-silent",
                "-u",
                url,
                "-status-code",
                "-title",
                "-tech-detect",
                "-server",
            ],
            "httpx.txt",
            evidence,
        )

    if tool("curl"):
        return execute(
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

    print(
        f"{RED}[-] httpx/curl not installed.{RESET}"
    )


# ============================================================
# TECHNOLOGY ANALYSIS
# ============================================================

def technology_analysis(target):
    if not authorized(target):
        return None

    url = normalize_url(target)
    evidence = evidence_dir(
        target,
        "web_technology_analysis",
    )

    if tool("whatweb"):
        return execute(
            [
                "whatweb",
                "--color=never",
                url,
            ],
            "whatweb.txt",
            evidence,
        )

    if tool("httpx"):
        return execute(
            [
                "httpx",
                "-silent",
                "-u",
                url,
                "-title",
                "-tech-detect",
                "-status-code",
                "-server",
            ],
            "httpx.txt",
            evidence,
        )

    if tool("curl"):
        return execute(
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

    print(
        f"{RED}[-] No technology-analysis tool available.{RESET}"
    )


# ============================================================
# ENDPOINT ENUMERATION
# ============================================================

def endpoint_enumeration(target):
    if not authorized(target):
        return None

    url = normalize_url(target).rstrip("/")
    evidence = evidence_dir(target, "web_endpoint_enumeration")

    wordlists = [
        "/usr/share/wordlists/dirb/common.txt",
        "/usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt",
    ]

    wordlist = next(
        (p for p in wordlists if Path(p).exists()),
        None,
    )

    if tool("ffuf") and wordlist:
        return execute(
            [
                "ffuf",
                "-u", url + "/FUZZ",
                "-w", wordlist,
                "-s",
            ],
            "ffuf.txt",
            evidence,
        )

    if tool("feroxbuster"):
        return execute(
            [
                "feroxbuster",
                "-u", url,
                "--no-state",
            ],
            "feroxbuster.txt",
            evidence,
        )

    if tool("gobuster") and wordlist:
        return execute(
            [
                "gobuster",
                "dir",
                "-u", url,
                "-w", wordlist,
            ],
            "gobuster.txt",
            evidence,
        )

    # Safe fallback for small authorized/local targets.
    common = [
        "/", "/robots.txt", "/favicon.ico", "/login",
        "/admin", "/api", "/docs", "/swagger.json",
        "/openapi.json", "/graphql", "/health",
    ]

    curl = tool("curl")

    if not curl:
        print(f"{RED}[-] No endpoint-enumeration backend available.{RESET}")
        return None

    results = []

    for path in common:
        try:
            result = subprocess.run(
                [
                    curl,
                    "-sS",
                    "-o", "/dev/null",
                    "-w", "%{http_code} %{size_download}",
                    "--max-time", "5",
                    url + path,
                ],
                text=True,
                capture_output=True,
                timeout=8,
            )

            line = result.stdout.strip()

            if line and not line.startswith("000"):
                results.append(f"{path} -> {line}")

        except (subprocess.TimeoutExpired, OSError):
            continue

    out = evidence / "common_paths.txt"
    out.write_text(
        "\n".join(results) if results else "No responsive common paths detected.\n"
    )

    print(f"{CYAN}[ALD] Common endpoint checks{RESET}")
    print("-" * 54)

    if results:
        for item in results:
            print(f"[+] {item}")
    else:
        print("[ALD] No responsive common paths detected.")

    print(f"\n[+] Evidence saved: {out}")
    return results


# ============================================================
# API SECURITY
# ============================================================

def api_security(target):
    if not authorized(target):
        return None

    url = normalize_url(target)
    evidence = evidence_dir(
        target,
        "web_api_security",
    )

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

    if not tool("curl"):
        print(
            f"{RED}[-] curl is required for API discovery.{RESET}"
        )
        return None

    for path in paths:
        endpoint = url.rstrip("/") + path

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
                f"  {path:<18} {value}"
            )

        except Exception as exc:
            results.append(
                {
                    "path": path,
                    "error": str(exc),
                }
            )

    output = evidence / "api_discovery.json"

    output.write_text(
        json.dumps(
            results,
            indent=2,
        )
    )

    print()
    print(
        f"{GREEN}[+] API evidence:{RESET} {output}"
    )

    return evidence


# ============================================================
# VULNERABILITY ANALYSIS
# ============================================================

def vulnerability_analysis(target):
    if not authorized(target):
        return None

    url = normalize_url(target)
    evidence = evidence_dir(
        target,
        "web_vulnerability_analysis",
    )

    if tool("nuclei"):
        return execute(
            [
                "nuclei",
                "-u",
                url,
            ],
            "nuclei.txt",
            evidence,
        )

    if tool("nikto"):
        return execute(
            [
                "nikto",
                "-h",
                url,
            ],
            "nikto.txt",
            evidence,
        )

    print(
        f"{RED}[-] nuclei and nikto are both missing.{RESET}"
    )


# ============================================================
# TLS
# ============================================================

def tls_analysis(target):
    if not authorized(target):
        return None

    url = normalize_url(target)
    parsed = urlparse(url)

    host = parsed.hostname

    if not host:
        print(f"{RED}[-] Could not determine hostname.{RESET}")
        return None

    port = parsed.port or (443 if parsed.scheme == "https" else 80)

    evidence = evidence_dir(
        target,
        "web_tls_analysis",
    )

    print(f"{YELLOW}[ALD] TLS analysis{RESET}")
    print(f"Host : {host}")
    print(f"Port : {port}")
    print()

    # Plain HTTP targets are not TLS endpoints.
    if parsed.scheme != "https" and port != 443:
        message = (
            f"Target is using {parsed.scheme.upper()} on port {port}.\n"
            "No TLS handshake was attempted.\n"
            "Use an HTTPS target or HTTPS port for certificate analysis."
        )

        print(f"{GREEN}[+] TLS not applicable.{RESET}")
        print()
        print(message)

        (evidence / "tls_status.txt").write_text(message)

        print()
        print(
            f"{GREEN}[+] Evidence saved:{RESET} "
            f"{evidence}"
        )

        return evidence

    if tool("openssl"):
        return execute(
            [
                "openssl",
                "s_client",
                "-connect",
                f"{host}:{port}",
                "-servername",
                host,
                "-showcerts",
            ],
            "openssl.txt",
            evidence,
        )

    if tool("nmap"):
        return execute(
            [
                "nmap",
                "-Pn",
                "-p",
                str(port),
                "--script",
                "ssl-cert,ssl-enum-ciphers",
                host,
            ],
            "nmap_tls.txt",
            evidence,
        )

    print(
        f"{RED}[-] openssl/nmap unavailable.{RESET}"
    )

    return None


# ============================================================
# DISPATCH
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

    if function is None:
        print(
            f"{RED}[-] Unknown web module: {module}{RESET}"
        )
        return None

    return function(target)
