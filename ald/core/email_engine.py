#!/usr/bin/env python3

from email import policy
from email.parser import BytesParser
from pathlib import Path
import re


def run(module, target=None):
    if module == "Header Analysis":
        print("[ALD] Email module : Header Analysis")
        print()

        path = Path(input("Email/header file: ").strip()).expanduser()

        if not path.is_file():
            print("[ALD] File not found.")
            return

        try:
            with path.open("rb") as fh:
                msg = BytesParser(policy=policy.default).parse(fh)

            headers = [
                "From",
                "To",
                "Cc",
                "Reply-To",
                "Return-Path",
                "Subject",
                "Date",
                "Message-ID",
                "Received",
                "Authentication-Results",
            ]

            print("[ALD] Header inventory")
            print("-" * 54)

            for name in headers:
                values = msg.get_all(name, [])
                if values:
                    for value in values:
                        print(f"{name}: {value}")

            return

        except Exception as exc:
            print(f"[ALD] Header parsing failed: {exc}")
            return

    if module == "SPF / DKIM / DMARC":
        print("[ALD] Email module : SPF / DKIM / DMARC")
        print()
        path = Path(input("Email/header file: ").strip()).expanduser()

        if not path.is_file():
            print("[ALD] File not found.")
            return

        text = path.read_text(errors="replace")

        checks = {
            "SPF": r"\bspf\b.*?(pass|fail|softfail|neutral|none)",
            "DKIM": r"\bdkim\b.*?(pass|fail|none)",
            "DMARC": r"\bdmarc\b.*?(pass|fail|none)",
        }

        for name, pattern in checks.items():
            match = re.search(pattern, text, re.IGNORECASE)
            print(f"[ALD] {name}: {match.group(0) if match else 'not observed'}")

        return

    if module == "Evidence":
        report_dir = Path("ald/reports")
        report_dir.mkdir(parents=True, exist_ok=True)
        print("[ALD] Email module : Evidence")
        print(report_dir.resolve())
        return

    print(f"[ALD] Unknown email module: {module}")
