#!/usr/bin/env python3

import json
import subprocess
import shutil
from pathlib import Path
from urllib.parse import urljoin


def _tool(name):
    return shutil.which(name)


def _base_url(target):
    target = target.strip()
    if not target.startswith(("http://", "https://")):
        target = "http://" + target
    return target.rstrip("/") + "/"


def _curl(url):
    curl = _tool("curl")
    if not curl:
        return None

    try:
        return subprocess.run(
            [curl, "-sS", "-L", "--max-time", "8", "-w", "\n%{http_code}", url],
            text=True,
            capture_output=True,
            timeout=10,
        )
    except Exception:
        return None


def run(module, target=None):
    if module == "API Discovery":
        print("[ALD] API module : API Discovery")
        print()

        base = _base_url(target or "127.0.0.1")
        evidence = Path("ald/reports/api_discovery")
        evidence.mkdir(parents=True, exist_ok=True)

        paths = [
            "openapi.json",
            "swagger.json",
            "api",
            "api/",
            "docs",
            "swagger",
            "graphql",
            "graphql/",
        ]

        found = []

        for path in paths:
            url = urljoin(base, path)
            result = _curl(url)

            if not result:
                continue

            body, _, status = result.stdout.rpartition("\n")
            if status.isdigit() and status != "000":
                found.append({
                    "path": "/" + path,
                    "status": int(status),
                    "url": url,
                })

        (evidence / "api_discovery.json").write_text(
            json.dumps(found, indent=2)
        )

        print("[ALD] Common API endpoints")
        print("-" * 54)

        if found:
            for item in found:
                print(f"[+] {item['status']} {item['path']}")
        else:
            print("[ALD] No responsive API candidates detected.")

        print(f"\n[+] Evidence saved: {evidence / 'api_discovery.json'}")
        return

    if module == "Schema Analysis":
        print("[ALD] API module : Schema Analysis")
        print()
        print("[ALD] Supported schema candidates: OpenAPI / Swagger.")
        return

    if module == "Authentication Analysis":
        print("[ALD] API module : Authentication Analysis")
        print()
        print("[ALD] Passive header/status inspection only.")
        return

    if module == "Evidence":
        report_dir = Path("ald/reports")
        report_dir.mkdir(parents=True, exist_ok=True)
        print("[ALD] API module : Evidence")
        print(report_dir.resolve())
        return

    print(f"[ALD] Unknown API module: {module}")
