#!/usr/bin/env python3

from pathlib import Path
from datetime import datetime


REPORT_ROOT = Path("ald/reports")


def _reports():
    REPORT_ROOT.mkdir(parents=True, exist_ok=True)
    return REPORT_ROOT


def run(module, target=None):
    root = _reports()

    if module == "Browse":
        print("[ALD] Evidence module : Browse")
        print()

        entries = sorted(
            root.rglob("*"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )

        print(f"[ALD] Evidence root: {root.resolve()}")
        print("-" * 54)

        if not entries:
            print("[ALD] No evidence files found.")
            return

        shown = 0

        for path in entries:
            if not path.is_file():
                continue

            try:
                size = path.stat().st_size
                mtime = datetime.fromtimestamp(
                    path.stat().st_mtime
                ).astimezone().isoformat(timespec="seconds")
            except OSError:
                continue

            rel = path.relative_to(root)
            print(f"[+] {rel}")
            print(f"    Size : {size} bytes")
            print(f"    Time : {mtime}")
            shown += 1

            if shown >= 100:
                print()
                print("[ALD] Display limited to 100 files.")
                break

        if shown == 0:
            print("[ALD] No evidence files found.")

        return

    if module == "Inspect":
        print("[ALD] Evidence module : Inspect")
        print()

        rel = input("Evidence file: ").strip()

        if not rel:
            print("[ALD] No file specified.")
            return

        path = (root / rel).resolve()

        try:
            path.relative_to(root.resolve())
        except ValueError:
            print("[ALD] Invalid evidence path.")
            return

        if not path.is_file():
            print("[ALD] Evidence file not found.")
            return

        print(f"[ALD] File : {path}")
        print(f"[ALD] Size : {path.stat().st_size} bytes")
        print("-" * 54)

        try:
            data = path.read_text(errors="replace")
            print(data[:12000])
        except Exception as exc:
            print(f"[ALD] Read failed: {exc}")

        return

    if module == "Summary":
        print("[ALD] Evidence module : Summary")
        print()

        files = [
            p for p in root.rglob("*")
            if p.is_file()
        ]

        total_size = 0

        for path in files:
            try:
                total_size += path.stat().st_size
            except OSError:
                pass

        print(f"[ALD] Files : {len(files)}")
        print(f"[ALD] Size  : {total_size} bytes")
        print(f"[ALD] Root  : {root.resolve()}")
        return

    print(f"[ALD] Unknown evidence module: {module}")
