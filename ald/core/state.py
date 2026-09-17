#!/usr/bin/env python3

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STATE_FILE = ROOT / "ald" / "config" / "state.json"


def load_state():
    if not STATE_FILE.exists():
        return {"target": None}

    try:
        return json.loads(
            STATE_FILE.read_text()
        )
    except Exception:
        return {"target": None}


def save_state(state):
    STATE_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    STATE_FILE.write_text(
        json.dumps(
            state,
            indent=2,
        )
    )


def get_target():
    return load_state().get("target")


def set_target(target):
    state = load_state()
    state["target"] = target
    save_state(state)


def clear_target():
    state = load_state()
    state["target"] = None
    save_state(state)
