#!/usr/bin/env python3

import shutil
import subprocess
from pathlib import Path

def _tool(name):
    return shutil.which(name)

def run(module, target=None):
    if module == "Container Scan":
        print("[ALD] Cloud module : Container Scan")
        print()
        docker = _tool("docker")
        podman = _tool("podman")
        tool = docker or podman
        print(f"[ALD] Container backend: {tool or 'not found'}")
        if tool:
            cmd = [tool, "images"] if tool.endswith("docker") or tool.endswith("podman") else [tool]
            try:
                r = subprocess.run(cmd, text=True, capture_output=True, timeout=10)
                print(r.stdout.strip() or "[ALD] No container images detected.")
            except Exception as exc:
                print(f"[ALD] Container query failed: {exc}")
        return

    if module == "IaC Analysis":
        print("[ALD] Cloud module : IaC Analysis")
        print()
        path = Path(input("IaC file/directory: ").strip()).expanduser()
        if not path.exists():
            print("[ALD] Path not found.")
            return
        files = [path] if path.is_file() else sorted(
            f for f in path.rglob("*")
            if f.is_file() and f.suffix.lower() in {".tf", ".tfvars", ".yaml", ".yml", ".json"}
        )
        print(f"[ALD] IaC files detected: {len(files)}")
        for f in files[:50]:
            print(f"[+] {f}")
        return

    if module == "SBOM":
        print("[ALD] Cloud module : SBOM")
        print()
        for name in ("syft", "trivy"):
            print(f"[ALD] {name}: {_tool(name) or 'not found'}")
        return

    if module == "Code Analysis":
        print("[ALD] Cloud module : Code Analysis")
        print()
        path = Path(input("Source path: ").strip()).expanduser()
        if not path.exists():
            print("[ALD] Path not found.")
            return
        files = [path] if path.is_file() else [
            f for f in path.rglob("*")
            if f.is_file()
        ]
        print(f"[ALD] Files detected: {len(files)}")
        return

    if module == "Evidence":
        report_dir = Path("ald/reports")
        report_dir.mkdir(parents=True, exist_ok=True)
        print("[ALD] Cloud module : Evidence")
        print(report_dir.resolve())
        return

    print(f"[ALD] Unknown cloud module: {module}")
