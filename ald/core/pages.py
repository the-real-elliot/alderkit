#!/usr/bin/env python3

import os
import shutil
import subprocess


RED = "\033[1;31m"
YELLOW = "\033[1;33m"
GREEN = "\033[1;32m"
CYAN = "\033[1;36m"
WHITE = "\033[1;37m"
RESET = "\033[0m"


def clear():
    os.system("clear")


def header(title, subtitle="SECURITY OPERATIONS CORE"):
    clear()

    print(f"{RED}")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║  A L D  //  E L L I O T                                  ║")
    print(f"║  {title:<56}║")
    print("╚════════════════════════════════════════════════════════════╝")
    print(f"{RESET}")

    print(f"{YELLOW}{subtitle}{RESET}")
    print()


def pause():
    input(f"\n{YELLOW}[ENTER] Return{RESET}")


def menu_page(title, target, options, description=None):
    while True:
        header(title)

        if target:
            print(f"{YELLOW}TARGET:{RESET} {target}")
            print()

        if description:
            print(description)
            print()

        for key, label in options:
            print(f"  {YELLOW}[{key}]{RESET} {label}")

        print(f"\n  {YELLOW}[B]{RESET} Back")
        print()

        choice = input(f"{YELLOW}{title} > {RESET}").strip().lower()

        if choice in ("b", "back", "0", "q"):
            return None

        for key, label in options:
            if choice == str(key).lower():
                return choice

        print(f"\n{RED}[-] Unknown option.{RESET}")


def info_page(title, target, lines, warning=None):
    header(title)

    if target:
        print(f"{YELLOW}TARGET:{RESET} {target}")
        print()

    for line in lines:
        print(line)

    if warning:
        print()
        print(f"{RED}[!] {warning}{RESET}")

    pause()


def tool_available(tool):
    return shutil.which(tool) is not None


def run_local_tool(tool, args=None):
    args = args or []

    if not tool_available(tool):
        print(f"{RED}[-] {tool} is not installed.{RESET}")
        pause()
        return ""

    cmd = [tool] + args

    print(f"{YELLOW}[ALD]{RESET} $ {' '.join(cmd)}")
    print()

    try:
        result = subprocess.run(
            cmd,
            text=True,
            capture_output=True,
            timeout=180,
        )

        output = result.stdout + result.stderr
        print(output)

        return output

    except Exception as exc:
        print(f"{RED}[ALD ERROR] {exc}{RESET}")
        return ""
