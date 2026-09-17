#!/usr/bin/env python3

def authorized():
    print("\033[1;33m[ALD]\033[0m Authorized-security-assessment mode.")
    answer = input("Do you have permission to assess this target? [y/N]: ")
    return answer.lower() == "y"
