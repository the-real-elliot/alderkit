#!/usr/bin/env python3

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "config" / "dependencies.json"


def _run(cmd, *, check=False):
    print()
    print("[ALD] $ " + " ".join(cmd))

    try:
        return subprocess.run(
            cmd,
            text=True,
            check=check,
        )
    except FileNotFoundError:
        print(f"[ALD] Command not found: {cmd[0]}")
    except subprocess.CalledProcessError as exc:
        print(f"[ALD] Command failed with exit code {exc.returncode}")
    except Exception as exc:
        print(f"[ALD] Command failed: {exc}")

    return None


def _load_manifest():
    if not MANIFEST.is_file():
        raise RuntimeError(f"Manifest not found: {MANIFEST}")

    data = json.loads(MANIFEST.read_text())

    if not isinstance(data, dict):
        raise RuntimeError("Invalid dependency manifest.")

    return data


def _arch_family():
    try:
        os_release = Path("/etc/os-release").read_text().lower()
    except OSError:
        os_release = ""

    return (
        Path("/etc/arch-release").exists()
        or "id=arch" in os_release
        or "id_like=arch" in os_release
        or shutil.which("pacman") is not None
    )


def _unique(items):
    return list(dict.fromkeys(items))


def _missing_binaries(manifest):
    result = []

    for binary in manifest["binaries"]:
        if shutil.which(binary) is None:
            result.append(binary)

    return result


def _package_for_binary(manifest, binary):
    return manifest["binaries"][binary]


def verify():
    manifest = _load_manifest()

    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(" ALD // DEPENDENCY VERIFICATION")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print()

    total = len(manifest["binaries"])
    available = 0

    for binary in manifest["binaries"]:
        path = shutil.which(binary)

        if path:
            available += 1
            print(f"[+] {binary:<15} {path}")
        else:
            print(f"[-] {binary:<15} missing")

    print()
    print(f"[ALD] Coverage: {available}/{total}")

    return available == total


def _git_update(args):
    root = ROOT

    if not (root / ".git").exists():
        print("[ALD] Git repository not detected.")
        print("[ALD] Skipping ALD source update.")
        return True

    git = shutil.which("git")
    if not git:
        print("[ALD] git not found.")
        print("[ALD] Skipping ALD source update.")
        return True

    remote = subprocess.run(
        [git, "-C", str(root), "remote", "get-url", "origin"],
        text=True,
        capture_output=True,
    )

    if remote.returncode != 0:
        print("[ALD] No GitHub origin configured.")
        print("[ALD] Skipping ALD source update.")
        return True

    origin = remote.stdout.strip()

    status = subprocess.run(
        [git, "-C", str(root), "status", "--porcelain"],
        text=True,
        capture_output=True,
    )

    if status.stdout.strip():
        print("[ALD] Local Git changes detected.")
        print("[ALD] Refusing automatic pull to protect local work.")
        return True

    print(f"[ALD] Git origin: {origin}")

    fetch = subprocess.run(
        [git, "-C", str(root), "fetch", "--prune", "origin"],
        text=True,
        capture_output=True,
    )

    if fetch.returncode != 0:
        print("[ALD] Git fetch failed.")
        print(fetch.stderr.strip())
        return False

    branch = subprocess.run(
        [git, "-C", str(root), "branch", "--show-current"],
        text=True,
        capture_output=True,
    ).stdout.strip()

    if not branch:
        print("[ALD] Detached Git HEAD; skipping source update.")
        return True

    local = subprocess.run(
        [git, "-C", str(root), "rev-parse", "HEAD"],
        text=True,
        capture_output=True,
        check=True,
    ).stdout.strip()

    remote_ref = f"origin/{branch}"

    remote_head = subprocess.run(
        [git, "-C", str(root), "rev-parse", remote_ref],
        text=True,
        capture_output=True,
    )

    if remote_head.returncode != 0:
        print(f"[ALD] Remote branch {remote_ref} not found.")
        return True

    remote_hash = remote_head.stdout.strip()

    if local == remote_hash:
        print("[ALD] ALD source already up to date.")
        return True

    print("[ALD] Source update available.")

    if "--yes" not in args and "-y" not in args:
        answer = input("[ALD] Pull latest ALD source? [y/N]: ").strip().lower()
        if answer not in {"y", "yes"}:
            print("[ALD] Source update skipped.")
            return True

    pull = subprocess.run(
        [git, "-C", str(root), "pull", "--ff-only", "origin", branch],
        text=True,
    )

    if pull.returncode != 0:
        print("[ALD] Fast-forward update failed.")
        return False

    print("[ALD] ALD source updated.")
    return True


def update(args=None):
    args = args or []

    try:
        manifest = _load_manifest()
    except Exception as exc:
        print(f"[ALD] {exc}")
        return 1

    if not _arch_family():
        print("[ALD] Unsupported platform.")
        print("[ALD] Current dependency profile supports Arch-family systems.")
        return 2

    assume_yes = "--yes" in args or "-y" in args
    deps_only = "--deps-only" in args
    code_only = "--code-only" in args
    verify_only = "--verify" in args

    if not verify_only and not deps_only:
        if not _git_update(args):
            return 4

        # Reload the manifest after a source update.
        try:
            manifest = _load_manifest()
        except Exception as exc:
            print(f"[ALD] {exc}")
            return 1

    if code_only:
        print("[ALD] Code-only update complete.")
        return 0

    packages = _unique(
        manifest["platforms"]["arch"]["packages"]
    )

    missing = _missing_binaries(manifest)

    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(" ALD // SYSTEM UPDATE")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print()
    print("[ALD] Platform          : Arch family")
    print(f"[ALD] Manifest          : {MANIFEST}")
    print(f"[ALD] Declared packages : {len(packages)}")
    print(f"[ALD] Declared binaries : {len(manifest['binaries'])}")
    print(f"[ALD] Missing binaries  : {len(missing)}")
    print()

    if missing:
        print("[ALD] Missing tools")
        print("-" * 54)

        for binary in missing:
            print(
                f"[+] {binary} → "
                f"{_package_for_binary(manifest, binary)}"
            )

        print()

    if verify_only:
        return 0 if verify() else 3

    print("[ALD] Deduplicated package set")
    print("-" * 54)

    for package in packages:
        print(f"[+] {package}")

    if not assume_yes:
        answer = input(
            "\n[ALD] Update/install dependency set? [y/N]: "
        ).strip().lower()

        if answer not in {"y", "yes"}:
            print("[ALD] Update cancelled.")
            return 0

    pacman = shutil.which("pacman")
    paru = shutil.which("paru")

    if not pacman:
        print("[ALD] pacman not found.")
        return 2

    if paru:
        cmd = [paru, "-Syu", "--needed"]

        if assume_yes:
            cmd.append("--noconfirm")

        cmd.extend(packages)

        print()
        print("[ALD] Using paru for repository/AUR/BlackArch resolution.")
    else:
        cmd = ["sudo", pacman, "-Syu", "--needed"]

        if assume_yes:
            cmd.append("--noconfirm")

        cmd.extend(packages)

        print()
        print("[ALD] paru not found; using pacman.")

    result = _run(cmd)

    if result is None or result.returncode != 0:
        print("[ALD] Dependency update failed.")
        return 5

    print()
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(" ALD // POST-UPDATE VERIFICATION")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print()

    # Keep syntax validation cheap and local.
    python = shutil.which("python")
    if python:
        compile_result = subprocess.run(
            [
                python,
                "-m",
                "py_compile",
                str(ROOT / "ald" / "ald.py"),
                str(ROOT / "ald" / "core" / "update_engine.py"),
            ],
            text=True,
            capture_output=True,
        )

        if compile_result.returncode != 0:
            print("[ALD] Python syntax verification failed.")
            print(compile_result.stderr.strip())
            return 6

    ok = verify()

    print()

    if ok:
        print("[ALD] Tool coverage: 28/28")
        print("[ALD] Dependency update complete.")
        return 0

    print("[ALD] Some declared tools are still missing.")
    return 7

def cli(args=None):
    args = args or sys.argv[2:]

    if "--verify" in args:
        return update(args)

    return update(args)
