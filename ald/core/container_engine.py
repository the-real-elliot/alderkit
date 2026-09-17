#!/usr/bin/env python3

import shutil
import subprocess


def _tool(name):
    return shutil.which(name)


def run(module, target=None):
    docker = _tool("docker")
    podman = _tool("podman")
    runtime = docker or podman

    if module == "Image Analysis":
        print("[ALD] Container module : Image Analysis")
        print()

        if not runtime:
            print("[ALD] Container runtime: not found")
            return

        print(f"[ALD] Runtime: {runtime}")

        try:
            result = subprocess.run(
                [runtime, "images", "--format",
                 "{{.Repository}}:{{.Tag}} {{.ID}} {{.Size}}"],
                text=True,
                capture_output=True,
                timeout=10,
            )

            print("[ALD] Local images")
            print("-" * 54)
            print(result.stdout.strip() or "[ALD] No container images detected.")

        except subprocess.TimeoutExpired:
            print("[ALD] Container query timed out.")

        return

    if module == "Runtime Analysis":
        print("[ALD] Container module : Runtime Analysis")
        print()

        if not runtime:
            print("[ALD] Container runtime: not found")
            return

        try:
            result = subprocess.run(
                [runtime, "ps", "--format",
                 "{{.ID}} {{.Image}} {{.Status}} {{.Names}}"],
                text=True,
                capture_output=True,
                timeout=10,
            )

            print("[ALD] Running containers")
            print("-" * 54)
            print(result.stdout.strip() or "[ALD] No running containers.")

        except subprocess.TimeoutExpired:
            print("[ALD] Runtime query timed out.")

        return

    if module == "SBOM":
        print("[ALD] Container module : SBOM")
        print()
        print(f"[ALD] syft  : {_tool('syft') or 'not found'}")
        print(f"[ALD] trivy : {_tool('trivy') or 'not found'}")
        return

    if module == "Evidence":
        from pathlib import Path
        report_dir = Path("ald/reports")
        report_dir.mkdir(parents=True, exist_ok=True)
        print("[ALD] Container module : Evidence")
        print(report_dir.resolve())
        return

    print(f"[ALD] Unknown container module: {module}")
