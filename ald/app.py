#!/usr/bin/env python3
"""
ALD // ELLIOT — Security Operations Core — Web GUI

Thin Flask layer over the existing ald.core package. It doesn't add any
new scanning capability — it just exposes registry.status(), catalog,
state, and engine.dispatch() to a browser dashboard instead of the
numbered terminal menu.

PLACEMENT
    Drop this file (and templates/) into the same directory that
    contains your existing `ald/` package, e.g.:

        your_project/
          ald/              <- your existing package, unchanged
          app.py            <- this file
          templates/
            index.html

RUN
    pip install flask
    python app.py
    open http://127.0.0.1:5000

AUTHORIZATION
    engine.execute()/web_endpoint_enum() normally block on an
    interactive `input()` scope-confirmation prompt. A web server can't
    block on stdin, so this layer replaces that prompt with an explicit
    "authorized" flag the browser must send with every run request —
    same gate, same requirement, just moved from a terminal y/N to a
    checkbox the operator has to tick per run. Nothing here weakens or
    bypasses the original confirmation; it re-implements it for a GUI.
"""

import sys
import time
import threading
from pathlib import Path

from flask import Flask, jsonify, request, render_template

sys.path.insert(0, str(Path(__file__).resolve().parent))

from ald.core import registry, state, engine  # noqa: E402

app = Flask(__name__)

# Mirrors the order of your original CLI menu. Anything not present as a
# key in registry.REGISTRY is shown in the GUI as "planned" (visible,
# disabled) rather than hidden, so the dashboard matches the scope of
# the CLI menu without inventing modules that don't exist yet.
MASTER_CATEGORIES = [
    "Reconnaissance", "Web Security", "Network Security", "Wireless",
    "Passwords", "Hash Analysis", "Cryptography", "Encryption / Decryption",
    "OSINT", "Social Engineering", "Active Directory", "Windows Security",
    "Linux Security", "Privilege Escalation", "Exploitation",
    "Reverse Engineering", "Binary Exploitation", "Malware Analysis",
    "Forensics", "Memory Forensics", "Mobile Security", "Cloud Security",
    "Container Security", "API Security", "Database Security", "Fuzzing",
    "Vulnerability Research", "DoS / Stress Testing", "Traffic / PCAP",
    "DNS Security", "Email Security", "Bluetooth", "RFID / NFC",
    "SDR / Radio", "Hardware / IoT", "Steganography", "Certificate / TLS",
    "Threat Intelligence", "Source Code Analysis", "Supply Chain Security",
    "Incident Response", "YARA / IOC Analysis", "Automation",
    "Tool Orchestration", "Evidence", "Reports", "Tool Inventory", "Doctor",
    "ALD Intel", "Tool Matrix",
]

# Modules that engine.dispatch() actually knows how to run today.
DISPATCH_READY = {
    "WEB SECURITY": {"http discovery", "endpoint enumeration", "vulnerability analysis"},
    "NETWORK SECURITY": {"network discovery", "service analysis"},
    "OSINT": {"username discovery", "domain intelligence"},
}

_run_lock = threading.Lock()


def registry_key(name):
    return name.strip().upper()


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/api/menu")
def api_menu():
    reg = registry.status()
    out = []

    for name in MASTER_CATEGORIES:
        key = registry_key(name)
        modules_status = reg.get(key)

        if modules_status is None:
            out.append({"name": name, "key": key, "active": False, "modules": []})
            continue

        modules = []
        for module_name, info in modules_status.items():
            modules.append({
                "name": module_name,
                "candidates": info["candidates"],
                "installed": list(info["installed"].keys()),
                "ready": info["ready"],
                "dispatchable": module_name.lower() in DISPATCH_READY.get(key, set()),
            })

        out.append({"name": name, "key": key, "active": True, "modules": modules})

    return jsonify(out)


@app.get("/api/target")
def get_target():
    return jsonify({"target": state.get_target()})


@app.post("/api/target")
def set_target():
    data = request.get_json(force=True) or {}
    target = (data.get("target") or "").strip()

    if not target:
        return jsonify({"error": "target required"}), 400

    state.set_target(target)
    return jsonify({"target": target})


@app.post("/api/run")
def run_module():
    data = request.get_json(force=True) or {}
    category = registry_key(data.get("category", ""))
    module = (data.get("module") or "").strip()
    authorized = bool(data.get("authorized"))

    target = state.get_target()
    if not target:
        return jsonify({"error": "No target configured."}), 400

    if not authorized:
        return jsonify({"error": "Explicit authorization not confirmed for this target."}), 403

    if not _run_lock.acquire(blocking=False):
        return jsonify({"error": "Another module is already running."}), 409

    original_confirm = engine.confirm_scope
    try:
        # The checkbox above IS the scope confirmation; skip the
        # blocking terminal input() the CLI would normally show.
        engine.confirm_scope = lambda t: True

        started = time.time()
        evidence_dir = engine.dispatch(category, module, target)
        elapsed = round(time.time() - started, 2)

        if evidence_dir is None:
            return jsonify({
                "error": "Module didn't run (tool missing, or not wired into dispatch() yet).",
                "elapsed": elapsed,
            }), 400

        skip = {"command.txt", "exit_code.txt", "target.txt", "module.txt", "timestamp.txt"}
        output_text = ""
        for f in sorted(Path(evidence_dir).iterdir()):
            if f.name in skip or not f.is_file():
                continue
            try:
                output_text += f.read_text(errors="replace")
            except Exception:
                pass

        return jsonify({
            "evidence_dir": str(evidence_dir),
            "output": output_text or "(no output captured)",
            "elapsed": elapsed,
        })

    except Exception as exc:
        return jsonify({"error": str(exc)}), 500

    finally:
        engine.confirm_scope = original_confirm
        _run_lock.release()


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False, threaded=True)
