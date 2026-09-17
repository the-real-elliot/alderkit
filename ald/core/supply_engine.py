#!/usr/bin/env python3

import ast
import importlib.util
import shutil
import subprocess
from pathlib import Path


def _tool(name):
    return shutil.which(name)


def _run(cmd, timeout=30):
    try:
        return subprocess.run(
            cmd,
            text=True,
            capture_output=True,
            timeout=timeout,
        )
    except Exception as exc:
        print(f"[ALD] Command failed: {exc}")
        return None


def _python_imports(root):
    imports = set()

    files = [root] if root.is_file() else [
        f for f in root.rglob("*.py")
        if ".git" not in f.parts
        and "__pycache__" not in f.parts
    ]

    for path in files:
        try:
            tree = ast.parse(
                path.read_text(errors="replace"),
                filename=str(path),
            )
        except (SyntaxError, OSError):
            continue

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for item in node.names:
                    imports.add(item.name.split(".")[0])

            elif isinstance(node, ast.ImportFrom):
                if node.module and node.level == 0:
                    imports.add(node.module.split(".")[0])

    return sorted(imports)


def _classify_import(name, root):
    if name in {"core", "modules", "ald"}:
        return "internal"

    try:
        spec = importlib.util.find_spec(name)
    except (ImportError, ModuleNotFoundError, ValueError):
        spec = None

    if spec is None:
        return "unresolved"

    origin = spec.origin or ""

    if origin in {"built-in", "frozen"}:
        return "stdlib"

    root_str = str(root.resolve())
    if root_str and origin.startswith(root_str):
        return "internal"

    if origin.startswith("/usr/lib/python"):
        return "stdlib"

    return "third-party"


def run(module, target=None):
    if module == "Dependency Analysis":
        print("[ALD] Supply Chain module : Dependency Analysis")
        print()

        path = Path(input("Project path/file: ").strip()).expanduser()

        if not path.exists():
            print("[ALD] Path not found.")
            return

        manifest_names = {
            "requirements.txt",
            "pyproject.toml",
            "Pipfile",
            "poetry.lock",
            "package.json",
            "package-lock.json",
            "pnpm-lock.yaml",
            "yarn.lock",
            "Cargo.toml",
            "Cargo.lock",
            "go.mod",
            "go.sum",
        }

        manifests = [
            p for p in (
                path.rglob("*") if path.is_dir() else [path]
            )
            if p.is_file()
            and p.name in manifest_names
            and ".git" not in p.parts
        ]

        print(f"[ALD] Dependency manifests found: {len(manifests)}")
        print("-" * 54)

        for manifest in manifests:
            print(f"[+] {manifest}")

        if not manifests:
            print("[ALD] No recognized manifests.")
            print()
            print("[ALD] Python dependency classification")
            print("-" * 54)

            imports = _python_imports(path)

            categories = {
                "third-party": [],
                "stdlib": [],
                "internal": [],
                "unresolved": [],
            }

            for name in imports:
                categories[_classify_import(name, path)].append(name)

            for category in (
                "third-party",
                "stdlib",
                "internal",
                "unresolved",
            ):
                print(f"\n[{category.upper()}]")

                if categories[category]:
                    for name in categories[category]:
                        print(f"[+] {name}")
                else:
                    print("[ALD] None detected.")

            print()
            print(
                f"[ALD] Third-party imports: "
                f"{len(categories['third-party'])}"
            )

        print()
        print("[ALD] Package-analysis backends")
        print("-" * 54)

        for name in (
            "trivy",
            "syft",
            "pip-audit",
            "npm",
            "cargo",
            "go",
        ):
            print(f"[ALD] {name}: {_tool(name) or 'not found'}")

        return

    if module == "SBOM":
        print("[ALD] Supply Chain module : SBOM")
        print()

        path = Path(input("Project/image path: ").strip()).expanduser()

        if not path.exists():
            print("[ALD] Path not found.")
            return

        syft = _tool("syft")

        if not syft:
            print("[ALD] syft backend: not found")
            return

        output = Path("ald/reports") / "sbom.json"
        output.parent.mkdir(parents=True, exist_ok=True)

        result = _run(
            [syft, str(path), "-o", "cyclonedx-json"],
            timeout=60,
        )

        if not result:
            return

        if result.returncode != 0:
            print(
                result.stderr.strip()
                or "[ALD] SBOM generation failed."
            )
            return

        output.write_text(result.stdout)
        print(f"[+] SBOM saved: {output}")
        return

    if module == "Evidence":
        report_dir = Path("ald/reports")
        report_dir.mkdir(parents=True, exist_ok=True)

        print("[ALD] Supply Chain module : Evidence")
        print(report_dir.resolve())
        return

    print(f"[ALD] Unknown supply-chain module: {module}")
