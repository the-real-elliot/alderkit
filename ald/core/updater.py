#!/usr/bin/env python3

import shutil
import subprocess
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


def run(command, cwd=None):
    import os

    env = os.environ.copy()

    # Prevent package-manager output from opening interactive pagers.
    env["PAGER"] = "cat"
    env["GIT_PAGER"] = "cat"
    env["SYSTEMD_PAGER"] = "cat"
    env["MANPAGER"] = "cat"
    env["PACMAN_NOCOLOR"] = "1"
    env["ALD_PAGERLESS"] = "1"

    print()
    print(
        f"{CYAN}[ALD UPDATER]{RESET} "
        f"$ {' '.join(command)}"
    )
    print()

    try:
        return subprocess.run(
            command,
            cwd=cwd,
            text=True,
            env=env,
        )
    except KeyboardInterrupt:
        print(
            f"\n{YELLOW}[ALD] Update interrupted.{RESET}"
        )
        return None
    except Exception as exc:
        print(
            f"{RED}[ALD ERROR] {exc}{RESET}"
        )
        return None


def update_ald():
    print()
    print(
        f"{RED}============================================================{RESET}"
    )
    print(
        f"{RED} ALD // SELF UPDATE{RESET}"
    )
    print(
        f"{RED}============================================================{RESET}"
    )

    git = shutil.which("git")

    if not git:
        print(
            f"{RED}[-] git is not installed.{RESET}"
        )
        return False

    git_dir = ROOT / ".git"

    if not git_dir.exists():
        print(
            f"{YELLOW}[!] Aldernix is not a Git repository.{RESET}"
        )
        print(
            "ALD self-update skipped."
        )
        return False

    if not confirm(
        "Pull the latest Aldernix changes?"
    ):
        return False

    result = run(
        [
            git,
            "-C",
            str(ROOT),
            "pull",
            "--ff-only",
        ]
    )

    if result and result.returncode == 0:
        print(
            f"\n{GREEN}[+] ALD updated successfully.{RESET}"
        )
        return True

    print(
        f"\n{RED}[-] ALD update failed.{RESET}"
    )
    return False


def installed_registry_tools():
    from core.registry import status

    tools = set()

    for modules in status().values():
        for info in modules.values():
            for name in info["installed"]:
                tools.add(name)

    return sorted(tools)


def update_tools():
    print()
    print(
        f"{RED}============================================================{RESET}"
    )
    print(
        f"{RED} ALD // REGISTERED TOOL UPDATE{RESET}"
    )
    print(
        f"{RED}============================================================{RESET}"
    )
    print()

    if shutil.which("paru"):
        manager = "paru"
    elif shutil.which("pacman"):
        manager = "pacman"
    else:
        print(
            f"{RED}[-] No supported package manager found.{RESET}"
        )
        return False

    tools = installed_registry_tools()

    if not tools:
        print(
            f"{YELLOW}[!] No registered installed tools detected.{RESET}"
        )
        return True

    print("Registered installed tools:")
    for name in tools:
        print(f"  • {name}")

    print()

    # Important: registry executable names are not always the same
    # as Arch package names. Use the system helper for package-level
    # upgrades rather than blindly passing every executable name.
    print(
        f"{YELLOW}[ALD] Package manager:{RESET} {manager}"
    )
    print(
        "Registered tools are inventoried separately; "
        "the package manager controls actual package updates."
    )

    if manager == "paru":
        command = [
            "paru",
            "-Syu",
        ]
    else:
        command = [
            "sudo",
            "pacman",
            "-Syu",
        ]

    if not confirm(
        "Update installed Arch/AUR packages now?"
    ):
        return False

    result = run(command)

    if result and result.returncode == 0:
        print(
            f"\n{GREEN}[+] Package/tool update completed.{RESET}"
        )
        return True

    print(
        f"\n{RED}[-] Package/tool update failed.{RESET}"
    )
    return False


def update_system():
    print()
    print(
        f"{RED}============================================================{RESET}"
    )
    print(
        f"{RED} ALD // SYSTEM UPDATE{RESET}"
    )
    print(
        f"{RED}============================================================{RESET}"
    )
    print()

    if not shutil.which("sudo"):
        print(
            f"{RED}[-] sudo is unavailable.{RESET}"
        )
        return False

    if not shutil.which("pacman"):
        print(
            f"{RED}[-] pacman is unavailable.{RESET}"
        )
        return False

    if not confirm(
        "Run a full Arch system upgrade?"
    ):
        return False

    result = run(
        [
            "sudo",
            "pacman",
            "-Syu",
        ]
    )

    if result and result.returncode == 0:
        print(
            f"\n{GREEN}[+] System update completed.{RESET}"
        )
        return True

    print(
        f"\n{RED}[-] System update failed.{RESET}"
    )
    return False


def update_all():
    print()
    print(
        f"{RED}============================================================{RESET}"
    )
    print(
        f"{RED} ALD // FULL UPDATE{RESET}"
    )
    print(
        f"{RED}============================================================{RESET}"
    )
    print()
    print(
        "Order:"
    )
    print(
        "  1. ALD repository"
    )
    print(
        "  2. Arch/AUR packages"
    )
    print()

    update_ald()
    update_tools()

    print()
    print(
        f"{GREEN}[+] Full update sequence finished.{RESET}"
    )


def help_text():
    print()
    print("ALD UPDATER")
    print()
    print("  ald update")
    print("      Show updater commands.")
    print()
    print("  ald update ald")
    print("      Update the Aldernix Git repository.")
    print()
    print("  ald update tools")
    print("      Update installed Arch/AUR packages used by ALD.")
    print()
    print("  ald update system")
    print("      Perform a full Arch system upgrade.")
    print()
    print("  ald update all")
    print("      Update ALD + installed packages.")
    print()


def main(args):
    if not args:
        help_text()
        return 0

    command = args[0].lower()

    if command in ("help", "-h", "--help"):
        help_text()
        return 0

    if command == "ald":
        return 0 if update_ald() else 1

    if command == "tools":
        return 0 if update_tools() else 1

    if command == "system":
        return 0 if update_system() else 1

    if command == "all":
        update_all()
        return 0

    print(
        f"{RED}[-] Unknown update command: {command}{RESET}"
    )
    help_text()
    return 1
