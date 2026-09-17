#!/usr/bin/env python3

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

RED = "\033[1;31m"
YELLOW = "\033[1;33m"
GREEN = "\033[1;32m"
CYAN = "\033[1;36m"
RESET = "\033[0m"


def confirm(message):
    print()
    answer = input(
        f"{YELLOW}{message} [y/N]: {RESET}"
    ).strip().lower()

    return answer == "y"



def command_exists(name):
    return shutil.which(name) is not None


def run_command(command):
    print()
    print(
        f"{CYAN}[ALD TOOL FACTORY]{RESET} "
        f"$ {' '.join(command)}"
    )
    print()

    try:
        return subprocess.run(
            command,
            text=True,
        )

    except KeyboardInterrupt:
        print(
            f"\n{YELLOW}[ALD] Operation cancelled.{RESET}"
        )
        return None

    except Exception as exc:
        print(
            f"{RED}[ALD ERROR] {exc}{RESET}"
        )
        return None


def tool_status():
    from core.registry import status

    data = status()

    total = 0
    ready = 0

    print()
    print(
        f"{RED}============================================================{RESET}"
    )
    print(
        f"{RED} ALD // TOOL FACTORY // STATUS{RESET}"
    )
    print(
        f"{RED}============================================================{RESET}"
    )

    for category, modules in data.items():
        print()
        print(f"{YELLOW}[{category}]{RESET}")

        for module, info in modules.items():
            total += 1

            if info["ready"]:
                ready += 1
                state = f"{GREEN}READY{RESET}"
                tools = ", ".join(info["installed"])
            else:
                state = f"{RED}MISSING{RESET}"
                tools = ", ".join(info["candidates"])

            print(
                f"  {state:<16} "
                f"{module:<30} "
                f"{tools}"
            )

    print()
    print(
        f"{CYAN}Coverage:{RESET} {ready}/{total} modules have a backend."
    )
    print()



def need(capability):
    from core.registry import REGISTRY, resolve

    wanted = capability.strip().lower()

    aliases = {
        "web vuln": "vulnerability analysis",
        "web vulnerability": "vulnerability analysis",
        "web vulnerability analysis": "vulnerability analysis",
        "vuln": "vulnerability analysis",
        "http": "http discovery",
        "web discovery": "http discovery",
        "port scan": "network discovery",
        "network scan": "network discovery",
        "username": "username discovery",
        "domain": "domain intelligence",
        "tls": "tls / certificates",
    }

    wanted = aliases.get(wanted, wanted)

    matches = []

    for category, modules in REGISTRY.items():
        for module in modules:
            module_lower = module.lower()

            if (
                wanted == module_lower
                or wanted in module_lower
                or module_lower in wanted
                or wanted in category.lower()
            ):
                matches.append((category, module))

    print()
    print(
        f"{RED}============================================================{RESET}"
    )
    print(
        f"{RED} ALD // CAPABILITY RESOLVER{RESET}"
    )
    print(
        f"{RED}============================================================{RESET}"
    )
    print()
    print(f"Requested: {capability}")
    print()

    if not matches:
        print(
            f"{YELLOW}[!] No registered capability matched.{RESET}"
        )
        print()
        return 1

    # Remove duplicates while preserving order.
    matches = list(dict.fromkeys(matches))

    for index, (category, module) in enumerate(matches, 1):
        info = resolve(category, module)

        print(
            f"{CYAN}[{index}] {category}{RESET} → {module}"
        )

        if info["ready"]:
            print(f"    {GREEN}[READY]{RESET}")

            for name, path in info["installed"].items():
                print(f"      ✓ {name:<18} {path}")

        else:
            print(
                f"    {RED}[NO BACKEND INSTALLED]{RESET}"
            )

            for candidate in info["candidates"]:
                print(f"      • {candidate}")

        print()

    # Automatically continue only when there is exactly one
    # unresolved capability.
    unresolved = []

    for category, module in matches:
        info = resolve(category, module)

        if not info["ready"]:
            unresolved.append(
                (category, module, info)
            )

    if not unresolved:
        print(
            f"{GREEN}[+] Requested capability is already available.{RESET}"
        )
        return 0

    if len(unresolved) != 1:
        print(
            f"{YELLOW}[!] Multiple unresolved capabilities matched.{RESET}"
        )
        print("Select one with a more specific capability name.")
        return 0

    category, module, info = unresolved[0]

    print(
        f"{YELLOW}Missing backend for:{RESET} "
        f"{category} → {module}"
    )
    print()

    candidates = info["candidates"]

    if not candidates:
        print(
            f"{RED}[-] No install candidates are registered.{RESET}"
        )
        return 1

    for i, candidate in enumerate(candidates, 1):
        print(
            f"  {YELLOW}[{i}]{RESET} {candidate}"
        )

    print(
        f"  {YELLOW}[S]{RESET} Search repositories"
    )
    print(
        f"  {YELLOW}[B]{RESET} Back"
    )
    print()

    choice = input(
        f"{YELLOW}ALD TOOL FACTORY > {RESET}"
    ).strip().lower()

    if choice in ("b", "back", "q", "0"):
        return 0

    if choice == "s":
        for candidate in candidates:
            print()
            print(
                f"{CYAN}Searching: {candidate}{RESET}"
            )
            search(candidate)

        return 0

    try:
        selected_index = int(choice) - 1
    except ValueError:
        print(
            f"{RED}[-] Invalid selection.{RESET}"
        )
        return 1

    if not (0 <= selected_index < len(candidates)):
        print(
            f"{RED}[-] Invalid selection.{RESET}"
        )
        return 1

    selected = candidates[selected_index]

    print()
    print(
        f"{CYAN}Selected backend:{RESET} {selected}"
    )

    # Search first so the operator can see what package exists.
    print()
    search(selected)

    print()
    install_choice = input(
        f"Install '{selected}' now? [y/N]: "
    ).strip().lower()

    if install_choice != "y":
        print(
            f"{YELLOW}[ALD] Installation skipped.{RESET}"
        )
        return 0

    if install(selected):
        print()
        print(
            f"{GREEN}[+] Installation completed.{RESET}"
        )

        print()
        print(
            f"{CYAN}[ALD] Verifying backend...{RESET}"
        )

        if verify(selected):
            print()
            print(
                f"{GREEN}[+] Capability is now available.{RESET}"
            )
        else:
            print()
            print(
                f"{YELLOW}[!] Package installed, "
                f"but executable name differs from package name.{RESET}"
            )

        return 0

    print(
        f"{RED}[-] Installation failed or was cancelled.{RESET}"
    )
    return 1


def search(package):
    print()
    print(
        f"{CYAN}[ALD TOOL FACTORY]{RESET} "
        f"Searching package repositories for: {package}"
    )

    # Prefer paru when available because it can search both
    # official repositories and the AUR.
    if command_exists("paru"):
        result = run_command(
            ["paru", "-Ss", package]
        )

        return result.returncode == 0 if result else False

    if command_exists("pacman"):
        result = run_command(
            ["pacman", "-Ss", package]
        )

        return result.returncode == 0 if result else False

    print(
        f"{RED}[-] pacman is unavailable.{RESET}"
    )
    return False


def install(package):
    if not package:
        print(
            f"{RED}[-] Package name required.{RESET}"
        )
        return False

    print()
    print(
        f"{YELLOW}ALD will invoke the system package manager.{RESET}"
    )
    print(
        f"Requested package: {package}"
    )
    print()

    answer = input(
        "Continue installation? [y/N]: "
    ).strip().lower()

    if answer != "y":
        print(
            f"{YELLOW}[ALD] Installation cancelled.{RESET}"
        )
        return False

    # paru is preferred on this Arch-based setup.
    if command_exists("paru"):
        result = run_command(
            ["paru", "-S", "--needed", package]
        )
    elif command_exists("pacman"):
        result = run_command(
            ["sudo", "pacman", "-S", "--needed", package]
        )
    else:
        print(
            f"{RED}[-] No supported package manager found.{RESET}"
        )
        return False

    return bool(result and result.returncode == 0)


def info(name):
    from core.catalog import get

    data = get(name)

    if not data:
        print(
            f"{RED}[-] Tool not found in ALD catalog: {name}{RESET}"
        )
        return 1

    print()
    print(
        f"{RED}============================================================{RESET}"
    )
    print(
        f"{RED} ALD // TOOL INFO{RESET}"
    )
    print(
        f"{RED}============================================================{RESET}"
    )
    print()

    print(f"Name        : {name}")
    print(f"Category    : {data['category']}")
    print(f"Binary      : {data['binary']}")
    print(
        "Capabilities: "
        + ", ".join(data["capabilities"])
    )
    print(
        "Packages    : "
        + ", ".join(data["packages"])
    )
    print(
        "Verify      : "
        + " ".join(data["verify"])
    )

    print()

    if command_exists(data["binary"]):
        print(
            f"{GREEN}[READY] {data['binary']} is installed.{RESET}"
        )
    else:
        print(
            f"{RED}[MISSING] {data['binary']} is not installed.{RESET}"
        )

    print()
    return 0



def verify(binary):
    path = shutil.which(binary)

    if path:
        print(
            f"{GREEN}[+] READY{RESET} "
            f"{binary} → {path}"
        )
        return True

    print(
        f"{RED}[-] MISSING{RESET} "
        f"{binary}"
    )
    return False


def doctor():
    print()
    print(
        f"{RED}============================================================{RESET}"
    )
    print(
        f"{RED} ALD // TOOL FACTORY // DOCTOR{RESET}"
    )
    print(
        f"{RED}============================================================{RESET}"
    )
    print()

    checks = {
        "python": "Python",
        "pacman": "Pacman",
        "paru": "Paru / AUR helper",
        "nmap": "Network engine",
        "curl": "HTTP engine",
        "openssl": "TLS engine",
        "gdb": "Debugger",
        "strings": "Binary strings",
        "objdump": "Binary inspection",
        "readelf": "ELF inspection",
    }

    passed = 0

    for binary, description in checks.items():
        if verify(binary):
            print(f"       {description}")
            passed += 1

    print()
    print(
        f"{GREEN}Core tool health: "
        f"{passed}/{len(checks)}{RESET}"
    )

    print()
    print(
        f"{CYAN}[ALD] Running Python syntax validation...{RESET}"
    )

    files = [
        ROOT / "ald" / "ald.py",
        ROOT / "ald" / "core" / "pages.py",
        ROOT / "ald" / "core" / "engine.py",
        ROOT / "ald" / "core" / "registry.py",
        ROOT / "ald" / "core" / "state.py",
        ROOT / "ald" / "core" / "web_engine.py",
        ROOT / "ald" / "core" / "selftest.py",
        ROOT / "ald" / "core" / "toolfactory.py",
    ]

    compile_result = subprocess.run(
        [
            sys.executable,
            "-m",
            "py_compile",
            *[str(path) for path in files if path.exists()],
        ],
        text=True,
        capture_output=True,
    )

    if compile_result.returncode == 0:
        print(
            f"{GREEN}[+] Python core: OK{RESET}"
        )
    else:
        print(
            f"{RED}[-] Python core: FAILED{RESET}"
        )
        print(compile_result.stderr)

    return compile_result.returncode == 0


def update_tool(name):
    from core.catalog import get

    data = get(name)

    if not data:
        print(
            f"{RED}[-] Tool not found in ALD catalog: {name}{RESET}"
        )
        return 1

    print()
    print(
        f"{CYAN}[ALD TOOL UPDATE]{RESET} {name}"
    )

    packages = data["packages"]

    print()
    print("Packages:")
    for package in packages:
        print(f"  • {package}")

    print()

    if not confirm(
        f"Update package(s) for {name}?"
    ):
        return 0

    if not shutil.which("paru") and not shutil.which("pacman"):
        print(
            f"{RED}[-] No supported package manager found.{RESET}"
        )
        return 1

    success = True

    for package in packages:
        if shutil.which("paru"):
            result = run_command(
                [
                    "paru",
                    "-S",
                    "--needed",
                    package,
                ]
            )
        else:
            result = run_command(
                [
                    "sudo",
                    "pacman",
                    "-S",
                    "--needed",
                    package,
                ]
            )

        if not result or result.returncode != 0:
            success = False

    print()

    if success:
        print(
            f"{GREEN}[+] Update operation completed.{RESET}"
        )
        return 0

    print(
        f"{RED}[-] Update operation failed.{RESET}"
    )
    return 1



def help_text():
    print()
    print("ALD TOOL FACTORY")
    print()
    print("  ald tool status")
    print("      Show registered security modules and backends.")
    print()
    print("  ald tool search <name>")
    print("      Search Arch/AUR repositories.")
    print()
    print("  ald tool install <package>")
    print("      Install one selected package.")
    print()
    print("  ald tool verify <binary>")
    print("      Verify one executable.")
    print()
    print("  ald tool doctor")
    print("      Check ALD core and important tools.")
    print()

    print("  ald tool need <capability>")
    print("      Resolve backends for a security capability.")
    print()

    print("  ald tool update")
    print("      Update installed ALD-related packages.")
    print()
    print("  ald selftest")
    print("      Run isolated localhost engine tests.")
    print()


def main(args):
    if not args:
        help_text()
        return 0

    command = args[0].lower()

    if command == "status":
        tool_status()
        return 0

    if command == "search":
        if len(args) < 2:
            print(
                f"{RED}Usage: ald tool search <name>{RESET}"
            )
            return 1

        return 0 if search(args[1]) else 1

    if command == "install":
        if len(args) < 2:
            print(
                f"{RED}Usage: ald tool install <package>{RESET}"
            )
            return 1

        return 0 if install(args[1]) else 1

    if command == "verify":
        if len(args) < 2:
            print(
                f"{RED}Usage: ald tool verify <binary>{RESET}"
            )
            return 1

        return 0 if verify(args[1]) else 1

    if command == "info":
        if len(args) < 2:
            print(
                f"{RED}Usage: ald tool info <tool>{RESET}"
            )
            return 1

        return info(args[1])

    if command == "update":
        if len(args) < 2:
            from core.updater import main as updater_main
            return updater_main(["tools"])

        return update_tool(args[1])

    if command == "doctor":
        return 0 if doctor() else 1

    if command == "update":
        from core.updater import main as updater_main
        return updater_main(args[1:])

    if command == "need":
        if len(args) < 2:
            print(
                f"{RED}Usage: ald tool need <capability>{RESET}"
            )
            return 1

        capability = " ".join(args[1:])
        return need(capability)

    if command in ("help", "-h", "--help"):
        help_text()
        return 0

    print(
        f"{RED}[-] Unknown tool command: {command}{RESET}"
    )
    help_text()
    return 1
