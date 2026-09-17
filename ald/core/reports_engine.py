#!/usr/bin/env python3

from datetime import datetime
from pathlib import Path


REPORT_ROOT = Path("ald/reports")


def _root():
    REPORT_ROOT.mkdir(parents=True, exist_ok=True)
    return REPORT_ROOT


def _files():
    root = _root()
    return [
        p for p in root.rglob("*")
        if p.is_file()
    ]


def run(module, target=None):
    root = _root()

    if module == "List Reports":
        print("[ALD] Reports module : List Reports")
        print()

        files = sorted(
            _files(),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )

        print(f"[ALD] Report root: {root.resolve()}")
        print("-" * 54)

        if not files:
            print("[ALD] No reports found.")
            return

        for path in files[:100]:
            try:
                rel = path.relative_to(root)
                size = path.stat().st_size
                stamp = datetime.fromtimestamp(
                    path.stat().st_mtime
                ).astimezone().isoformat(timespec="seconds")
                print(f"[+] {rel}")
                print(f"    Size: {size} bytes")
                print(f"    Time: {stamp}")
            except OSError:
                continue

        if len(files) > 100:
            print()
            print("[ALD] Display limited to 100 reports.")

        return

    if module == "Generate Index":
        print("[ALD] Reports module : Generate Index")
        print()

        files = sorted(
            _files(),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )

        index = root / "REPORT_INDEX.txt"

        lines = [
            "ALD // REPORT INDEX",
            f"Generated: {datetime.now().astimezone().isoformat()}",
            f"Root: {root.resolve()}",
            f"Files: {len(files)}",
            "",
        ]

        for path in files:
            try:
                rel = path.relative_to(root)
                stat = path.stat()
                lines.append(
                    f"{rel}\t{stat.st_size} bytes\t"
                    f"{datetime.fromtimestamp(stat.st_mtime).astimezone().isoformat()}"
                )
            except OSError:
                continue

        index.write_text("\n".join(lines))
        print(f"[+] Index saved: {index}")
        return

    if module == "Inspect":
        print("[ALD] Reports module : Inspect")
        print()

        rel = input("Report path: ").strip()

        if not rel:
            print("[ALD] No report specified.")
            return

        path = (root / rel).resolve()

        try:
            path.relative_to(root.resolve())
        except ValueError:
            print("[ALD] Invalid report path.")
            return

        if not path.is_file():
            print("[ALD] Report not found.")
            return

        print(f"[ALD] Report: {path}")
        print(f"[ALD] Size: {path.stat().st_size} bytes")
        print("-" * 54)

        try:
            print(path.read_text(errors="replace")[:12000])
        except Exception as exc:
            print(f"[ALD] Read failed: {exc}")

        return

    if module == "Evidence":
        print("[ALD] Reports module : Evidence")
        print(root.resolve())
        return

    print(f"[ALD] Unknown reports module: {module}")
