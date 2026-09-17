#!/usr/bin/env python3

def analyze_profile(profile):
    if isinstance(profile, str):
        return {
            "target": profile,
            "ports": [],
            "services": [],
            "technologies": [],
        }

    if not isinstance(profile, dict):
        return {
            "target": "unknown",
            "ports": [],
            "services": [],
            "technologies": [],
        }

    return {
        "target": profile.get("target", "unknown"),
        "ports": profile.get("ports", []),
        "services": profile.get("services", []),
        "technologies": profile.get("technologies", []),
    }


def print_plan(profile):
    plan = analyze_profile(profile)

    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(" ALD // INTELLIGENCE PLAN")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print()
    print(f"[ALD] Target: {plan['target']}")
    print(f"[ALD] Ports: {len(plan['ports'])}")
    print(f"[ALD] Services: {len(plan['services'])}")
    print(f"[ALD] Technologies: {len(plan['technologies'])}")
    print()
    print("[ALD] Intelligence plan generated.")
