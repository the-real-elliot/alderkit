#!/usr/bin/env python3

import shutil
import subprocess
from pathlib import Path
from datetime import datetime


TASKS = {
    "1": (
        "Host Summary",
        [
            ("hostname", ["hostname"]),
            ("kernel", ["uname", "-a"]),
            ("uptime", ["uptime"]),
        ],
    ),
    "2": (
        "Process Snapshot",
        [
            ("processes", ["ps", "-eo", "pid,ppid,user,%cpu,%mem,comm", "--sort=-%cpu"]),
        ],
    ),
    "3": (
        "Network Snapshot",
        [
            ("interfaces", ["ip", "-brief", "addr"]),
            ("sockets", ["ss", "-tunap"]),
        ],
    ),
}


def _tool(command):
    return shutil.which(command)


def _run(command, timeout=15):
    try:
        return subprocess.run(
            command,
            text=True,
            capture_output=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        print(f"[ALD] Timeout: {' '.join(command)}")
    except OSError as exc:
        print(f"[ALD] Execution failed: {exc}")
    return None


def run(module, target=None):
    if module == "Task Runner":
        print("[ALD] Automation module : Task Runner")
        print()
        print("[1] Host Summary")
        print("[2] Process Snapshot")
        print("[3] Network Snapshot")
        print("[4] Python Project Compile")
        print("[5] Evidence")
        print()

        choice = input("Task: ").strip()

        if choice in TASKS:
            name, commands = TASKS[choice]
            print(f"\n[ALD] Task: {name}")
            print("-" * 54)

            for label, command in commands:
                tool = _tool(command[0])

                if not tool:
                    print(f"[-] {label}: {command[0]} not found")
                    continue

                print(f"\n[+] {label}")
                result = _run(command)

                if result:
                    output = (result.stdout or "").strip()
                    if output:
                        print(output[:12000])

                    if result.stderr.strip():
                        print(result.stderr.strip()[:4000])

            return

        if choice == "4":
            root = Path(input("Project path [~/Aldernix]: ").strip() or "~/Aldernix").expanduser()

            if not root.exists():
                print("[ALD] Path not found.")
                return

            python = _tool("python")
            if not python:
                print("[ALD] Python backend not found.")
                return

            files = [
                f for f in root.rglob("*.py")
                if ".git" not in f.parts
                and "__pycache__" not in f.parts
            ]

            print(f"[ALD] Python files: {len(files)}")
            failures = 0

            for path in files:
                result = _run([python, "-m", "py_compile", str(path)], timeout=10)
                if not result or result.returncode != 0:
                    failures += 1
                    print(f"[FAIL] {path}")

            print()
            print(f"[ALD] Compile failures: {failures}")
            print("[ALD] Project compile check complete.")
            return

        if choice == "5":
            return run("Evidence", target)

        print("[ALD] Invalid task.")
        return

    if module == "Evidence":
        report_dir = Path("ald/reports")
        report_dir.mkdir(parents=True, exist_ok=True)

        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = report_dir / f"{stamp}_automation_evidence.txt"

        path.write_text(
            "ALD // AUTOMATION EVIDENCE\n"
            f"Timestamp: {datetime.now().astimezone().isoformat()}\n"
            f"Target: {target or '127.0.0.1'}\n"
        )

        print("[ALD] Automation module : Evidence")
        print(f"[+] Evidence saved: {path}")
        return

    print(f"[ALD] Unknown automation module: {module}")
